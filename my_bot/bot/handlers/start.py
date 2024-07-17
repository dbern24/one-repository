from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from my_bot.bot.utils import database as db
from my_bot.bot.utils.auxiliary import user_menu
from my_bot.bot.utils.config import log_channel, thread_id_start, referral_reward_price, photo_start_url

start_router = Router()


def start_message(first_name, user_id):

    text = f"""
<b>Приветствуем тебя в экосистеме CrypteX, <a href="tg://user?id={user_id}">{first_name}</a>!</b> 👋

<a href="https://t.me/CrypteXCoinsBot">CrypteX</a> — это особая платформа в Telegram, где проявляя активность, позволит вам зарабатывать монеты внутри бота, и обменивать их на реальную криптовалюту!

Подписывайся на канал <a href="https://t.me/CrypteXCommunity">нашего сообщества</a>, чтобы быть в курсе всех новостей!
"""

    return text


@start_router.message(Command("start"))
async def start_handler(message: types.Message, bot: Bot):
    if message.chat.type == 'private':

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Я не робот 🤖", callback_data="not_a_robot")],
        ])

        is_not_new_user = await db.user_exists(message.from_user.id)
        first_name = message.from_user.first_name
        user_id = message.from_user.id
        start_command = message.text
        referrer_id = start_command[7:]

        if is_not_new_user:
            await bot.send_photo(message.from_user.id, photo=photo_start_url,
                                 caption=start_message(first_name, user_id), parse_mode="HTML", reply_markup=user_menu)
        else:
            if referrer_id:
                if referrer_id != str(message.from_user.id):
                    try:
                        # Добавляем пользователя в базу данных и устанавливаем статус "не получено" для награды
                        await db.add_user(message.from_user.id, int(referrer_id))
                        await db.update_reward_status(message.from_user.id, 'not_received')

                        # Проверяем, является ли пользователь приглашенным
                        invited_by = await db.get_invited_by(message.from_user.id)
                        if invited_by:
                            # Получаем ID пригласившего пользователя
                            inviter_id = invited_by

                            message_inviter_id = (
                                f"Ваш реферал {first_name} успешно зарегистрирован и проходит проверку!"
                            )
                            await bot.send_message(inviter_id, text=message_inviter_id, parse_mode="HTML")

                    except Exception as e:
                        await message.answer(text=f"Произошла ошибка: {e}.", show_alert=True)
                else:
                    await bot.send_message(message.from_user.id, "Запрещено регистрироваться по своей же ссылке!")
            else:
                try:
                    await db.add_user(message.from_user.id, 0)
                except Exception as e:
                    await message.answer(text=f"Произошла ошибка: {e}", show_alert=True)

            user_id = message.from_user.id
            username = message.from_user.username
            first_name = message.from_user.first_name
            last_name = message.from_user.last_name
            language_code = message.from_user.language_code

            info_text = f"<b>Зарегистрирован новый пользователь!</b>\n\n"
            info_text += f"User ID: {user_id}\nСсылка на профиль: <a href='tg://user?id={user_id}'>{first_name}</a>.\n"
            info_text += f"Username: @{username}\n" if username else "No username\n"
            info_text += f"First Name: {first_name}\n"
            info_text += f"Last Name: {last_name}\n" if last_name else "No last name\n"
            info_text += f"Language Code: {language_code}\n" if language_code else "No language code\n"

            await bot.send_message(log_channel, info_text, message_thread_id=thread_id_start, parse_mode="HTML")

            message_text = (
                f"<b>Постой-ка <a href='tg://user?id={user_id}'>{first_name}, а я о тебе никогда не слышал!</b>"
                f"\n\n"
                f"Твои $USDC уже ждут тебя, но сначала тебе нужно пройти проверку, чтобы стать участником бота! 👇"
            )
            await message.answer(message_text, parse_mode="HTML", reply_markup=keyboard)


# callback_query

@start_router.callback_query(lambda c: c.data == 'not_a_robot')
async def handle_download_stats(callback_query: types.CallbackQuery, bot: Bot):

    await callback_query.answer(text="", show_alert=True)
    await callback_query.message.delete()

    user_id = callback_query.from_user.id
    first_name = callback_query.from_user.first_name

    try:
        await db.update_verification_status(user_id, is_verified=1)

        await bot.send_message(user_id, f"Проверка на реального пользователя пройдена, {first_name}, удачи!",
                               parse_mode="HTML")

        invited_by = await db.get_invited_by(user_id)
        if invited_by and invited_by != 0:

            reward_status = await db.get_reward_status(user_id)
            if reward_status == 'not_received':
                try:

                    await db.update_reward_status(user_id, 'received')
                    message_user_id = (
                        f"Вам начислено +{referral_reward_price} $USDC за регистрацию по реферальной ссылке!")
                    await bot.send_message(user_id, text=message_user_id, parse_mode="HTML")

                    message_invited_by = (
                        f"Вам начислено +{referral_reward_price} $USDC за успешное приглашение пользователя через реферальную программу!"
                    )
                    await bot.send_message(invited_by, text=message_invited_by, parse_mode="HTML")

                except Exception as e:
                    await callback_query.answer(text=f"Произошла ошибка: {e}.", show_alert=True)

    except Exception as e:
        await callback_query.answer(text=f"Что-то пошло не так: {e}.", show_alert=True)

    await bot.send_photo(callback_query.from_user.id, photo=photo_start_url,
                         caption=start_message(first_name, user_id), parse_mode="html", reply_markup=user_menu)


