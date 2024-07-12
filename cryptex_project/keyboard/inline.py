from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.config import channels


def showchannels():
    inline_keyboard = []

    for channel in channels:
        btn = InlineKeyboardButton(text=channel[0], url=channel[2])
        inline_keyboard.append([btn])

    btnDoneSub = InlineKeyboardButton(text="Хорошо, я уже подписан! ✅", callback_data="subchanneldone")
    inline_keyboard.append([btnDoneSub])

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard


def showchannelsRef():
    inline_keyboard = []

    for channel in channels:
        btn = InlineKeyboardButton(text=channel[0], url=channel[2])
        inline_keyboard.append([btn])

    btnDoneSub = InlineKeyboardButton(text="Хорошо, я уже подписан! ✅", callback_data="subchanneldoneRef")
    inline_keyboard.append([btnDoneSub])

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard
    

def showchannels_startonly():
    inline_keyboard = []

    for channel in channels:
        btn = InlineKeyboardButton(text=channel[0], url=channel[2])
        inline_keyboard.append([btn])

    btnDoneSub = InlineKeyboardButton(text="Проверить! ✅", callback_data="ref_reward")
    inline_keyboard.append([btnDoneSub])

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    return keyboard
