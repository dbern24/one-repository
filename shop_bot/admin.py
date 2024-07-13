import os
from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from magic_filter import F

from config import ADMIN_USER_ID
import database as db

admin_router = Router()


class AdminStates(StatesGroup):
    waiting_for_broadcast_message = State()
    waiting_for_confirmation = State()
    waiting_for_button = State()
    waiting_for_user_count = State()
    waiting_for_image = State()


@admin_router.message(lambda message: message.text == 'Отправить рассылку 📤' and message.from_user.id == ADMIN_USER_ID)
async def send_broadcast_prompt(message: types.Message, state: FSMContext):
    if message.chat.type == 'private':
        await message.reply('Введите сообщение для рассылки:')
        await state.set_state(AdminStates.waiting_for_broadcast_message)


@admin_router.message(AdminStates.waiting_for_broadcast_message)
async def handle_broadcast_message(broadcast_message: types.Message, state: FSMContext):
    if broadcast_message.from_user.id == ADMIN_USER_ID:
        await state.update_data(broadcast_message=broadcast_message.html_text, keyboard=None)

        total_users, inactive_users = await db.get_user_statistics()
        active_users = total_users - inactive_users

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"Все ({total_users})", callback_data=f"send_to_all_{total_users}"),
                 InlineKeyboardButton(text="Отменить ❌", callback_data="cancel")],
            ]
        )

        await broadcast_message.reply(
            f"Введите количество пользователей для рассылки (активных: {active_users}, неактивных: {inactive_users}, всего: {total_users}):",
            reply_markup=keyboard
        )
        await state.set_state(AdminStates.waiting_for_user_count)
    else:
        await broadcast_message.reply('Произошла ошибка.')


@admin_router.message(AdminStates.waiting_for_user_count)
async def handle_user_count_message(user_count_message: types.Message, state: FSMContext):
    if user_count_message.from_user.id == ADMIN_USER_ID:
        try:
            user_count = int(user_count_message.text)
            await state.update_data(user_count=user_count)

            data = await state.get_data()
            broadcast_message = data.get('broadcast_message')

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Подтвердить ✔️", callback_data="confirm"),
                     InlineKeyboardButton(text="Отменить ❌", callback_data="cancel")],
                    [InlineKeyboardButton(text="Добавить кнопку ➕", callback_data="add_button")],
                    [InlineKeyboardButton(text="Загрузить изображение 🖼", callback_data="upload_image")]
                ]
            )

            await user_count_message.reply("Вы хотите отправить это сообщение?", reply_markup=keyboard)
            await state.set_state(AdminStates.waiting_for_confirmation)
        except ValueError:
            await user_count_message.reply('Ошибка! Введите число пользователей.')
    else:
        await user_count_message.reply('Произошла ошибка.')


@admin_router.message(AdminStates.waiting_for_image, F.photo)
async def handle_image_message(image_message: types.Message, state: FSMContext):
    if image_message.from_user.id == ADMIN_USER_ID:
        photo = image_message.photo[-1]
        await state.update_data(image=photo.file_id)

        data = await state.get_data()
        broadcast_message = data.get('broadcast_message')
        keyboard = data.get('keyboard')

        keyboard_confirmation = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Подтвердить ✅", callback_data="confirm"),
                 InlineKeyboardButton(text="Отменить ❌", callback_data="cancel")],
                [InlineKeyboardButton(text="Добавить кнопку ➕", callback_data="add_button")],
                [InlineKeyboardButton(text="Удалить изображение ❌", callback_data="delete_image")]
            ]
        )

        await image_message.reply_photo(photo.file_id, caption=broadcast_message, reply_markup=keyboard_confirmation)
        await state.set_state(AdminStates.waiting_for_confirmation)
    else:
        await image_message.reply('Произошла ошибка.')


@admin_router.callback_query(lambda c: c.data.startswith('confirm') or c.data.startswith('cancel') or c.data.startswith(
    'add_button') or c.data.startswith('send_to_all') or c.data == 'upload_image' or c.data == 'delete_image')
async def process_callback_button(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    broadcast_message = data.get('broadcast_message')
    keyboard = data.get('keyboard')
    image = data.get('image')

    if callback_query.data == 'upload_image':
        await bot.send_message(callback_query.from_user.id, "Загрузите изображение:")
        await state.set_state(AdminStates.waiting_for_image)
    elif callback_query.data == 'delete_image':
        await state.update_data(image=None)
        keyboard_confirmation = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Подтвердить ✅", callback_data="confirm"),
                 InlineKeyboardButton(text="Отменить ❌", callback_data="cancel")],
                [InlineKeyboardButton(text="Добавить кнопку ➕", callback_data="add_button")],
                [InlineKeyboardButton(text="Загрузить изображение 🖼", callback_data="upload_image")]
            ]
        )
        await bot.send_message(callback_query.from_user.id, broadcast_message, reply_markup=keyboard_confirmation)
    elif callback_query.data.startswith('confirm'):
        users = await db.get_all_users()
        user_count = data.get('user_count')
        successful_count = 0
        failed_count = 0
        sent_users = []

        # Создаем список для выжимки
        delivery_status = {}

        for user in users[:user_count]:
            try:
                if image:
                    await bot.send_photo(user[0], image, caption=broadcast_message, reply_markup=keyboard)
                else:
                    await bot.send_message(user[0], broadcast_message, reply_markup=keyboard)
                await db.reset_failed_send(user[0])
                successful_count += 1
                sent_users.append(user[0])
                # Добавляем информацию о доставке в выжимку
                delivery_status[user[0]] = "Delivered"
            except Exception as e:
                print(f"Не удалось отправить сообщение пользователю {user[0]}: {e}")
                await db.increment_failed_send(user[0])
                failed_count += 1
                # Добавляем информацию о неудачной доставке в выжимку
                delivery_status[user[0]] = "Not delivered"

        # Отправляем сообщение с общей статистикой
        await bot.send_message(callback_query.from_user.id,
                               f'<b>Общая статистика рассылки:</b>\n\nCообщение было успешно отправлено: {successful_count}\nНе удалось отправить сообщение: {failed_count}')

        # Создаем файл со статистикой и выжимкой
        stats_filename = 'stats.txt'
        with open(stats_filename, 'w') as file:
            file.write(f'Successful: {successful_count}\n')
            file.write(f'Failed: {failed_count}\n')
            file.write('Sent to users:\n')
            for index, (user_id, status) in enumerate(delivery_status.items(), start=1):
                file.write(f'{index}. User ID: {user_id}, Status: {status}\n')

        keyboard_stats = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Загрузить файл статистики 💾", callback_data="download_stats")],
            ]
        )
        await bot.send_message(callback_query.from_user.id,
                               '<b>Завершена рассылка, загрузить файл подробной статистики?</b>', parse_mode="html",
                               reply_markup=keyboard_stats)

        await state.clear()
    elif callback_query.data.startswith('cancel'):
        await callback_query.answer(text="", show_alert=True)
        await state.clear()
    elif callback_query.data.startswith('add_button'):
        await bot.send_message(callback_query.from_user.id,
                               'Введите кнопки в формате "название - ссылка", каждая кнопка на новой строке:')
        await state.set_state(AdminStates.waiting_for_button)
    elif callback_query.data.startswith('send_to_all'):
        user_count = int(callback_query.data.split('_')[-1])
        await state.update_data(user_count=user_count)

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Подтвердить ✅", callback_data="confirm"),
                 InlineKeyboardButton(text="Отменить ❌", callback_data="cancel")],
                [InlineKeyboardButton(text="Добавить кнопку ➕", callback_data="add_button")],
                [InlineKeyboardButton(text="Загрузить изображение 🖼", callback_data="upload_image")]
            ]
        )

        await bot.send_message(callback_query.from_user.id, "Вы хотите отправить это сообщение?", reply_markup=keyboard)
        await state.set_state(AdminStates.waiting_for_confirmation)

    await callback_query.message.delete()


@admin_router.message(AdminStates.waiting_for_button)
async def handle_button_message(button_message: types.Message, state: FSMContext, bot: Bot):
    if button_message.from_user.id == ADMIN_USER_ID:
        try:
            data = await state.get_data()
            broadcast_message = data.get('broadcast_message')
            existing_keyboard = data.get('keyboard')
            image = data.get('image')

            buttons = []
            for line in button_message.text.strip().split('\n'):
                title, url = line.split(' - ', 1)
                buttons.append(InlineKeyboardButton(text=title, url=url))

            if existing_keyboard:
                existing_keyboard.inline_keyboard.append(buttons)
                keyboard = existing_keyboard
            else:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])

            await state.update_data(keyboard=keyboard)

            # Отправка примера сообщения с кнопками и изображением (если есть)
            if image:
                await bot.send_photo(button_message.from_user.id, image, caption=broadcast_message,
                                     reply_markup=keyboard)
            else:
                await bot.send_message(button_message.from_user.id, broadcast_message, reply_markup=keyboard)

            keyboard_confirmation = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Подтвердить ✅", callback_data="confirm"),
                     InlineKeyboardButton(text="Отменить ❌", callback_data="cancel")],
                    [InlineKeyboardButton(text="Добавить кнопку ➕", callback_data="add_button")]
                ]
            )

            await bot.send_message(button_message.from_user.id, "Кнопки добавлены. Вы хотите отправить это сообщение?",
                                   reply_markup=keyboard_confirmation)
            await state.set_state(AdminStates.waiting_for_confirmation)
        except ValueError:
            await bot.send_message(button_message.from_user.id,
                                   'Произошла ошибка при добавлении кнопок. Проверьте формат и попробуйте снова.')
    else:
        await button_message.reply('Произошла ошибка.')


@admin_router.callback_query(lambda c: c.data == 'download_stats')
async def handle_download_stats(callback_query: types.CallbackQuery, bot: Bot):
    stats_filename = 'stats.txt'
    await bot.answer_callback_query(callback_query.id, text="", show_alert=True)

    if os.path.isfile(stats_filename):
        await bot.send_document(callback_query.from_user.id, FSInputFile(stats_filename))
        os.remove(stats_filename)
    else:
        await bot.answer_callback_query(callback_query.id, text="❌ Документ не найден или уже был загружен!",
                                        show_alert=True)


@admin_router.message(lambda message: message.text == 'Получить статистику 📊' and message.from_user.id == ADMIN_USER_ID)
async def cmd_stat(message: types.Message):
    if message.chat.type == 'private':

        if message.from_user.id == ADMIN_USER_ID:
            total_users, inactive_users = await db.get_user_statistics()
            active_users = total_users - inactive_users

            await message.reply(
                f'<b>Текущая, общая статистика по проекту:</b>\n\nВсего пользователей: {total_users}\nИз них активных пользователей: {active_users}\nИз них неактивных пользователей: {inactive_users}',
                parse_mode="html")
        else:
            await message.reply('У вас нет доступа к этой команде.')


@admin_router.message(Command('admin'))
async def cmd_admin(message: types.Message):
    if message.chat.type == 'private':

        if message.from_user.id == ADMIN_USER_ID:
            await message.reply('Добро пожаловать в панель администратора!', reply_markup=admin_menu)
            #   await message.answer_sticker(sticker="CAACAgIAAxkBAVmXumZORG9sI1OsnMN_K5-EXdOywuxmAAIYFAACTnNgSphCYN5qYn20NQQ")
        else:
            await message.reply('У вас нет доступа к админ панели.')


@admin_router.message(Command('complete'))
async def complete_order(message: types.Message, bot: Bot, state: FSMContext):
    if message.chat.type == 'private':

        if message.from_user.id == ADMIN_USER_ID:
            order_id = message.text.split()[1]
            order = await db.get_order_by_id(order_id)  # Предполагаем, что функция get_order_by_id в том же модуле

            if order and order['status'] == 'pending':  # Убедитесь, что order - это словарь
                await db.complete_order(order_id)
                await db.update_user_balance(order['user_id'], order['amount'])
                await message.reply("Ордер успешно подтвержден.")
                await bot.send_message(order['user_id'],
                                       f"Ваш ордер #{order_id} был подтвержден, средства успешно зачислены на ваш баланс!")
                await state.clear()
            else:
                await message.reply("Неверный или уже завершенный ордер.")
        else:
            await message.reply('У вас нет доступа к этой команде.')


# Создание клавиатуры для администратора
admin_menu = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [types.KeyboardButton(text="Получить статистику 📊")],
        [types.KeyboardButton(text="Отправить рассылку 📤")],
    ]
)
