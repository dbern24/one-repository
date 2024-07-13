from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

API_TOKEN = '7434583914:AAEjZaWFwOgrxnoEax22N8AI2XRdMqKqeaM'
ADMIN_USER_ID = 6769252698  # Админ user_id в Telegram
CHANNEL_ID = '6769252698'  # Канал для отправки логов

STOCK_CHANNEL_ID = '-1002197983589'  # Канал для отправки программ

channels = [
    ["Подписаться", "-1002245580308", "https://t.me/+1Go_x_6tSiE3ZTQy"],
]

ERC20_WALLET = '0xf0eB253d8529D608d60E0775756c049c1Ccf83Aa'
BEP20_WALLET = '0xf0eB253d8529D608d60E0775756c049c1Ccf83Aa'
TRON_WALLET = 'TVLyosBtc3KKeVWXMdv4ZCum4Xn3RWLMMe'

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