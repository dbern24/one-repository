from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

API_TOKEN = ''
ADMIN_USER_ID =   # Админ user_id в Telegram
CHANNEL_ID = ''  # Канал для отправки логов

STOCK_CHANNEL_ID = ''  # Канал для отправки программ

channels = [
    ["Подписаться", "", "https://t.me/"],
]

ERC20_WALLET = ''
BEP20_WALLET = ''
TRON_WALLET = ''

# Создание клавиатуры для пользователя
user_menu = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [types.KeyboardButton(text="Мой баланс"), types.KeyboardButton(text="Про бот")],
        [types.KeyboardButton(text="Программы"), types.KeyboardButton(text="Плагины")],
    ]
)

soft_menu = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [types.KeyboardButton(text="Adobe Photoshop (2024 г.)")],
        [types.KeyboardButton(text="Adobe AfterEffects (2024 г.)")],
        [types.KeyboardButton(text="Adobe Lightroom (2024 г.)")],
        [types.KeyboardButton(text="Adobe Illustrator (2024 г.)")],
        [types.KeyboardButton(text="Adobe Premierepro (2024 г.)")],
        [types.KeyboardButton(text="Главное меню 🔙")],
    ]
)

plugin_menu = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [types.KeyboardButton(text="в разработке...")],
        [types.KeyboardButton(text="в разработке...")],
        [types.KeyboardButton(text="Главное меню 🔙")],
    ]
)


# inline

def not_sub():
    inline_keyboard = []

    for channel in channels:
        btn = InlineKeyboardButton(text=channel[0], url=channel[2])
        inline_keyboard.append([btn])

    btnDoneSub = InlineKeyboardButton(text="Проверить", callback_data="check_sub_channels_repeat")
    inline_keyboard.append([btnDoneSub])

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    return keyboard
