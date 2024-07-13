import asyncio
import logging
import random
import string

from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import database as db
from config import CHANNEL_ID, ERC20_WALLET, BEP20_WALLET, TRON_WALLET, ADMIN_USER_ID, user_menu, channels, \
    soft_menu, \
    not_sub

# Создание экземпляра маршрутизатора
user_router = Router()


# Определение состояния для процесса пополнения
class TopupStates(StatesGroup):
    waiting_for_amount = State()


# Функция для генерации случайного номера ордера
def generate_order_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


# Функция для проверки подписки на каналы
async def check_sub_channels(channels, user_id, bot: Bot):
    for channel in channels or ADMIN_USER_ID:
        channel_id = channel[1]
        try:
            chat_member = await bot.get_chat_member(channel_id, user_id)
            if chat_member.status == 'left':
                return False
        except Exception as e:
            await bot.send_message(CHANNEL_ID, f"Ошибка при проверке пользователя {user_id}: {e}.")
            return False
    return True


# Функция для проверки подписки на каналы повторно, по нажатию на кнопку
@user_router.callback_query(lambda c: c.data == 'check_sub_channels_repeat')
async def check_sub_channels_repeat(callback_query: types.CallbackQuery, bot: Bot):

    if await check_sub_channels(channels, callback_query.from_user.id, bot):

        await callback_query.answer(text="", show_alert=True)
        await bot.send_message(callback_query.from_user.id, text="✅ <b>Одобрено успешно!</b> Продолжай пользоваться ботом и следи за каналом, там много интересного!", parse_mode="html")
        await callback_query.message.delete()
        await bot.send_message(callback_query.from_user.id, 'Перенаправление в «Главное меню»:', reply_markup=user_menu)
    else:

        await callback_query.answer(text="", show_alert=True)
        await bot.send_message(callback_query.from_user.id, text="❗️<b>Не удалось проверить!</b> Подпишись на официальный канал нашего проекта, чтобы иметь возможность использовать нашего бота!", parse_mode="html", reply_markup=not_sub())
        await callback_query.message.delete()


# Обработчик команды /start
@user_router.message(Command('start'))
async def cmd_start(message: types.Message, bot: Bot):
    if message.chat.type == 'private':
        # Проверка, является ли пользователь новым, и добавление его в базу данных, если это так
        is_new_user = await db.add_user_if_not_exists(message.from_user.id)

        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        language_code = message.from_user.language_code

        if is_new_user:
            # Формирование сообщения о новом пользователе
            info_text = f"<b>Зарегистрирован новый пользователь!</b>\n\n"
            info_text += f"User ID: {user_id}\nСсылка на профиль: <a href='tg://user?id={user_id}'>{first_name}</a>\n"
            info_text += f"Username: @{username}\n" if username else "No username\n"
            info_text += f"First Name: {first_name}\n"
            info_text += f"Last Name: {last_name}\n" if last_name else "No last name\n"
            info_text += f"Language Code: {language_code}\n" if language_code else "No language code\n"

            # Отправка сообщения о новом пользователе в канал
            await bot.send_message(CHANNEL_ID, info_text)

    if await check_sub_channels(channels, message.from_user.id, bot):

        # Ответное сообщение пользователю
        await message.reply('Добро пожаловать!', reply_markup=user_menu)

    else:
        await bot.send_message(message.from_user.id,
                               text="Подпишись на официальный канал нашего проекта, чтобы иметь возможность использовать нашего бота!",
                               parse_mode="html", reply_markup=not_sub())


# Обработчик сообщения "Про бот"
@user_router.message(lambda message: message.text == 'Про бот')
async def about_bot(message: types.Message, bot: Bot):
    if message.chat.type == 'private':

        if await check_sub_channels(channels, message.from_user.id, bot):

            await message.reply('Это тестовый бот, созданный для демонстрации функционала!')

        else:
            await bot.send_message(message.from_user.id,
                                   text="Подпишись на официальный канал нашего проекта, чтобы иметь возможность использовать нашего бота!",
                                   parse_mode="html", reply_markup=not_sub())


# Обработчик сообщения "Программы"
@user_router.message(lambda message: message.text == 'Программы')
async def menu_plugins(message: types.Message):
    if message.chat.type == 'private':
        await message.reply('Меню «Программы»:', reply_markup=soft_menu)


# Обработчик сообщения "Плагины"
@user_router.message(lambda message: message.text == 'Плагины')
async def menu_plugins(message: types.Message):
    if message.chat.type == 'private':
        await message.reply('Меню «Плагины»:', reply_markup=soft_menu)


# Обработчик сообщения "Главное меню 🔙"
@user_router.message(lambda message: message.text == 'Главное меню 🔙')
async def menu_plugins(message: types.Message):
    if message.chat.type == 'private':
        await message.reply('Вы вернулись в «Главное меню»:', reply_markup=user_menu)


# Обработчик callback-запроса "cancel"
@user_router.callback_query(lambda c: c.data == 'cancel')
async def cancel(callback_query: types.CallbackQuery, bot: Bot):
    await callback_query.message.delete()


# Обработчик сообщения "Мой баланс"
@user_router.message(lambda message: message.text == 'Мой баланс')
async def my_balance(message: types.Message):
    if message.chat.type == 'private':
        user_id = message.from_user.id
        balance = await db.get_user_balance(user_id)

        # Форматирование баланса до 2 знаков после запятой
        formatted_balance = f"{balance:.2f}"

        first_name = message.from_user.first_name

        # Ответное сообщение с балансом пользователя и кнопкой "Пополнить"
        await message.reply(
            f"Имя: <a href='tg://user?id={user_id}'>{first_name}</a>\nID: {user_id}\nВаш баланс: {formatted_balance} USDT.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Пополнить 💰", callback_data="topup")],
                ]
            ))


# Обработчик callback-запроса "topup"
@user_router.callback_query(lambda c: c.data == 'topup')
async def topup(callback_query: types.CallbackQuery, bot: Bot):
    await bot.send_message(callback_query.from_user.id, "Выберите способ пополнения USDT:",
                           reply_markup=InlineKeyboardMarkup(
                               inline_keyboard=[
                                   [InlineKeyboardButton(text="ERC-20 (Ethereum)", callback_data="topup_erc20")],
                                   [InlineKeyboardButton(text="BEP-20 (Binance Smart Chain)",
                                                         callback_data="topup_bep20")],
                                   [InlineKeyboardButton(text="TRC-20 (Tron)", callback_data="topup_tron")],
                                   [InlineKeyboardButton(text="Отменить", callback_data="cancel")]
                               ]
                           ))
    await callback_query.answer(text="", show_alert=True)


# Обработчик повторного запроса на пополнение
@user_router.callback_query(lambda c: c.data == 'topup_repeat')
async def topup(callback_query: types.CallbackQuery, bot: Bot):
    await bot.send_message(callback_query.from_user.id, "Выберите способ пополнения USDT:",
                           reply_markup=InlineKeyboardMarkup(
                               inline_keyboard=[
                                   [InlineKeyboardButton(text="ERC-20 (Ethereum)", callback_data="topup_erc20")],
                                   [InlineKeyboardButton(text="BEP-20 (Binance Smart Chain)",
                                                         callback_data="topup_bep20")],
                                   [InlineKeyboardButton(text="TRC-20 (Tron)", callback_data="topup_tron")],
                                   [InlineKeyboardButton(text="Отменить", callback_data="cancel")]
                               ]
                           ))
    await callback_query.message.delete()
    await callback_query.answer(text="", show_alert=True)


# Обработчик выбора сети ERC-20 для пополнения
@user_router.callback_query(lambda c: c.data == 'topup_erc20')
async def topup_erc20(callback_query: types.CallbackQuery, bot: Bot):
    await bot.send_message(callback_query.from_user.id, "Вы уверены, что хотите выбрать сеть ERC-20 USDT?",
                           reply_markup=InlineKeyboardMarkup(
                               inline_keyboard=[
                                   [InlineKeyboardButton(text="Подтвердить", callback_data="topup_confirm_erc20"),
                                    InlineKeyboardButton(text="Отменить", callback_data="topup_repeat")]
                               ]
                           ))
    await callback_query.message.delete()
    await callback_query.answer(text="", show_alert=True)


# Обработчик выбора сети BEP-20 для пополнения
@user_router.callback_query(lambda c: c.data == 'topup_bep20')
async def topup_bep20(callback_query: types.CallbackQuery, bot: Bot):
    await bot.send_message(callback_query.from_user.id, "Вы уверены, что хотите выбрать сеть BEP20 USDT?",
                           reply_markup=InlineKeyboardMarkup(
                               inline_keyboard=[
                                   [InlineKeyboardButton(text="Подтвердить", callback_data="topup_confirm_bep20"),
                                    InlineKeyboardButton(text="Отменить", callback_data="topup_repeat")]
                               ]
                           ))
    await callback_query.message.delete()
    await callback_query.answer(text="", show_alert=True)


# Обработчик выбора сети TRON для пополнения
@user_router.callback_query(lambda c: c.data == 'topup_tron')
async def topup_tron(callback_query: types.CallbackQuery, bot: Bot):
    await bot.send_message(callback_query.from_user.id, "Вы уверены, что хотите выбрать сеть TRON USDT?",
                           reply_markup=InlineKeyboardMarkup(
                               inline_keyboard=[
                                   [InlineKeyboardButton(text="Подтвердить", callback_data="topup_confirm_tron"),
                                    InlineKeyboardButton(text="Отменить", callback_data="topup_repeat")]
                               ]
                           ))
    await callback_query.message.delete()
    await callback_query.answer(text="", show_alert=True)


# Функция для создания сообщения с информацией об ордере
def order_info_message(order_id, amount, wallet_address, network):
    order_info = f"""
🧾 <b>Ордер #{order_id} успешно создан!</b>

<b>Сумма:</b> <code>{amount}</code> USDT
<b>Выбранная сеть:</b> {network}
<b>Адрес для пополнения:</b> <code>{wallet_address}</code>
<b>Время пополнения:</b> 15 минут

❗️Отправляйте только <b>USDT в сети {network} строго в указанном количестве,</b> иначе монеты могут быть утеряны!
    """
    return order_info


def order_info_message_to_admin(order_id, amount, wallet_address, network, user_id):
    order_info = f"""
Пользователь {user_id} создал новый ордер <code>{order_id}</code>!

<b>Сумма:</b> {amount} USDT
<b>Выбранная сеть:</b> {network}
<b>Адрес для пополнения:</b> <code>{wallet_address}</code>

Команда для подтверждения операции: <code>/complete {order_id}</code>.
    """
    return order_info


# Асинхронная функция для проверки статуса ордера через 15 минут
async def check_order_status(bot: Bot, user_id: int, order_id: str, message_id: int):
    await asyncio.sleep(900)  # 15 минут это 900 секунд
    order = await db.get_order_by_id(order_id)
    if order and order['status'] != 'completed':  # or 'canceled'
        await db.cancel_order(order_id)
        await bot.send_message(user_id,
                               f"❗️<b>Внимание!</b> Ваш ордер #{order_id} был отменен по причине: время пополнения вышло.",
                               parse_mode="HTML")  # , reply_to_message_id=message_id
        await bot.send_message(CHANNEL_ID,
                               f"Ордер <code>{order_id}</code> был отменен по причине: время пополнения вышло.",
                               parse_mode="HTML")


# Обработчик подтверждения выбранной сети для пополнения
@user_router.callback_query(lambda c: c.data in ['topup_confirm_erc20', 'topup_confirm_bep20', 'topup_confirm_tron'])
async def topup_confirm(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id

    # Обновление состояния с типом кошелька и запрос суммы пополнения
    await state.update_data(wallet_type=callback_query.data)
    await callback_query.message.delete()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отменить", callback_data="cancel")]
        ]
    )
    msg = await callback_query.message.answer("Введите сумму пополнения (мин 10 USDT, макс 5000 USDT):",
                                              reply_markup=keyboard)
    await state.update_data(last_message_id=msg.message_id)
    await state.set_state(TopupStates.waiting_for_amount)


@user_router.message(TopupStates.waiting_for_amount)
async def process_topup_amount(message: types.Message, state: FSMContext, bot: Bot):
    global wallet_address, network
    user_id = message.from_user.id

    try:
        # Проверка и форматирование суммы пополнения
        amount = float(message.text)
        if amount < 10 or amount > 5000:
            raise ValueError

        order_id = generate_order_id()
        amount_with_random_digits = round(amount + random.uniform(0, 0.9999), 4)
        data = await state.get_data()
        wallet_type = data.get('wallet_type')

        # Установка адреса кошелька и сети в зависимости от выбранного типа
        if wallet_type == 'topup_confirm_erc20':
            wallet_address = ERC20_WALLET
            network = 'ERC20'
        elif wallet_type == 'topup_confirm_bep20':
            wallet_address = BEP20_WALLET
            network = 'BEP20'
        elif wallet_type == 'topup_confirm_tron':
            wallet_address = TRON_WALLET
            network = 'TRON'

        # Создание ордера в базе данных
        await db.create_order(order_id, user_id, amount_with_random_digits)

        data = await state.get_data()
        last_message_id = data.get('last_message_id')

        if last_message_id:
            try:
                await bot.edit_message_text(text="Введите сумму пополнения (мин 10 USDT, макс 5000 USDT):",
                                            chat_id=user_id, message_id=last_message_id)
            except Exception as e:
                pass  # Игнорируем ошибки удаления
                print(f"{e}")

        # Сохранение order_id в состоянии
        await state.update_data(order_id=order_id)

        order_message = await bot.send_message(user_id,
                                               order_info_message(order_id, amount_with_random_digits, wallet_address,
                                                                  network))
        await bot.send_message(CHANNEL_ID,
                               order_info_message_to_admin(order_id, amount_with_random_digits, wallet_address, network,
                                                           user_id))

        await state.clear()

        # Запуск задачи для проверки статуса ордера через 15 минут
        await asyncio.create_task(check_order_status(bot, user_id, order_id, order_message.message_id))

    except ValueError:
        data = await state.get_data()
        last_message_id = data.get('last_message_id')

        if last_message_id:
            try:
                await bot.edit_message_text(text="Введите сумму пополнения (мин 10 USDT, макс 5000 USDT):",
                                            chat_id=user_id, message_id=last_message_id)

            except Exception as e:
                pass  # Игнорируем ошибки удаления
                print(f"{e}")

        await message.answer(
            "❗️ <b>Неверно указана сумма!</b> Пожалуйста, повторите попытку и укажите правильную сумму, (мин 10 USDT, макс 5000 USDT).",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Повторить попытку", callback_data="topup_repeat")]
                ]
            ))
        await state.clear()