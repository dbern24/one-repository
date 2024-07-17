from aiogram import Router, types, Bot, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from my_bot.bot.utils import database as db
from my_bot.bot.utils.config import CHANNEL_ID


auxiliary_router = Router()

last_button_press = {}


async def check_sub_channels(user_id, bot: Bot):
    channels = await db.get_active_channels()
    for channel in channels:
        channel_name = channel[0]
        channel_id = channel[1]
        try:
            chat_member = await bot.get_chat_member(channel_id, user_id)
            if chat_member.status == 'left':
                return False
        except Exception as e:
            await bot.send_message(CHANNEL_ID,
                                   f"Ошибка при проверке пользователя {user_id} на канале {channel_name} ({channel_id}): {e}.")
            return False
    return True


@auxiliary_router.callback_query(F.data == 'check_sub_channels_repeat')
async def check_sub_channels_repeat(callback_query: types.CallbackQuery, bot: Bot):
    first_name = callback_query.from_user.first_name

    if await check_sub_channels(callback_query.from_user.id, bot):
        await callback_query.answer(text=f"{first_name}, проверка прошла успешно!", show_alert=True)
        await callback_query.message.delete()
        await bot.send_message(callback_query.from_user.id, 'Вы вернулись в «Главное меню»:', reply_markup=user_menu)
    else:
        await callback_query.answer(text="", show_alert=True)
        message_text = (
            f"<b>{first_name}</b>, проверка не пройдена! Пожалуйста, проверьте подписку на канал(ы) и повторите попытку."
        )
        await bot.send_message(callback_query.from_user.id, message_text, parse_mode="HTML",
                               reply_markup=await not_signed())
        await callback_query.message.delete()


async def user_not_subscribed_message(message: types.Message, bot: Bot):
    first_name = message.from_user.first_name
    message_text = (
        f"{first_name}, подпишитесь на требуемые канал(ы), чтобы пользоваться ботом!"
    )
    await bot.send_chat_action(message.chat.id, "typing")
    await bot.send_message(message.from_user.id, message_text, reply_markup=await not_signed())


@auxiliary_router.message(F.text == '⬅️ Назад')
async def menu_plugins(message: types.Message):
    if message.chat.type == 'private':
        await message.reply('Вы вернулись в «Главное меню»:', reply_markup=user_menu)


# Создание клавиатуры для пользователя
user_menu = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [types.KeyboardButton(text="💼 Профиль"), types.KeyboardButton(text="👩🏻‍🔧 Помощь")],
        [types.KeyboardButton(text="🎁 Реферальный бонус")],
        [types.KeyboardButton(text="⛏ Майнинг")],
    ]
)


help_menu = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [types.KeyboardButton(text="Служба поддержки пользователей 🛠️")],
        [types.KeyboardButton(text="Канал и сообщество 🌐")],
        [types.KeyboardButton(text="⬅️ Назад")],
    ]
)


referral_menu = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [types.KeyboardButton(text="Как работает реферальный бонус? ❓")],
        [types.KeyboardButton(text="Получить ссылку для приглашения 🔗")],
        [types.KeyboardButton(text="⬅️ Назад")],
    ]
)


mining_menu = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [types.KeyboardButton(text="Как работает майнинг? ❓")],
        [types.KeyboardButton(text="Получить валюту 💰")],
        [types.KeyboardButton(text="⬅️ Назад")],
    ]
)


# inline

async def not_signed():
    inline_keyboard = []

    channels = await db.get_active_channels()
    for channel in channels:

        buttons_set = InlineKeyboardButton(text=channel[0], url=channel[2])
        inline_keyboard.append([buttons_set])

    buttons = InlineKeyboardButton(text="Я подписался, проверьте!", callback_data="check_sub_channels_repeat")
    inline_keyboard.append([buttons])

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard
