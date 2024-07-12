from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


mainMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text="💼 Профиль"), KeyboardButton(text="👩🏻‍🔧 Помощь")],
    [KeyboardButton(text="🎁 Реферальный бонус")],
    [KeyboardButton(text="⛏ Майнинг")]
])

helpMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text="Вопросы и ответы ❓"), KeyboardButton(text="Канал и сообщество 🌐")],
    [KeyboardButton(text="Служба поддержки пользователей 🛠️")],
    [KeyboardButton(text="⬅️ Назад")]
])


refMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text="Как работает реферальный бонус? ❓")],
    [KeyboardButton(text="Получить ссылку для приглашения 🔗")],
    [KeyboardButton(text="⬅️ Назад")]
])

claimMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text="Как работает майнинг? ❓")],
    [KeyboardButton(text="Получить валюту 💰")],
    [KeyboardButton(text="⬅️ Назад")]
])





AdmMenu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text="Управление балансами 💰")],
    [KeyboardButton(text="Список спонсоров 👥"), KeyboardButton(text="Таблица UID лидеров")],
    [KeyboardButton(text="Cтатистика 📊"), KeyboardButton(text="Рассылка 📩")],
])

mainMenuRef = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[

    [KeyboardButton(text="🎉 Получить реферальную награду!")],
    [KeyboardButton(text="Профиль 💼"), KeyboardButton(text="База знаний 📘")],
    [KeyboardButton(text="Реферальный бонус 🎁")],
    [KeyboardButton(text="Лидеры по балансу 🏆")],
    [KeyboardButton(text="⚡️ Получить +10 монет к балансу!")]

])
