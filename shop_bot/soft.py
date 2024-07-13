from aiogram import Router, types, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import database as db
from config import STOCK_CHANNEL_ID

soft_router = Router()

# отказ от ответственности. <a href="https://www.adobe.com/ru/">на сайте Adobe</a> \\ Это не покупка продукта или услуги — мы сообщество, и ваша поддержка помогает нам развиваться! Платеж идет на поддержку нашего сообщества, и вы получаете обещанную помощь от него!

alert_msg = """ 
\nПодтверждая покупку, вы соглашаетесь, что приобретаете товар только для ознакомления, покупайте только официальные программы! 
"""

# photoshop

description_p = """
<b>Приобрести Adobe Photoshop 2024 г. (версия 25.9) | #репак_от_кролика.</b>

<b>Информация о файле:</b> .exe 3366.2MB для Windows 64bit.

Встречайте долгожданное обновление Adobe Photoshop v25.9.0.573, <a href="https://helpx.adobe.com/ru/photoshop/using/whats-new/2024-4.html#adjustment-brush-tool">читать статью</a>. Инструмент «Корректирующая кисть» теперь доступен для обычных пользователей.

💰<b>Цена:</b> 10 USDT – навсегда, с прилагаемой инструкцией по установке.
"""


@soft_router.message(lambda message: message.text == 'Adobe Photoshop (2024 г.)')
async def buy_orchid(message: types.Message):
    if message.chat.type == 'private':
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Купить 💰", callback_data="buy_orchid_confirm")],
            ]
        )
        await message.reply(description_p, parse_mode="HTML", reply_markup=keyboard)


@soft_router.callback_query(lambda c: c.data == 'buy_orchid_confirm')
async def confirm_buy_orchid(callback_query: types.CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id
    balance = await db.get_user_balance(user_id)

    if balance < 10:
        await bot.send_message(user_id, "У вас недостаточно средств для покупки. Пожалуйста, пополните баланс.")
    else:
        await bot.send_message(user_id, "Вы уверены, что хотите приобрести Adobe Photoshop 2024 г. (версия 25.9)?" + alert_msg, parse_mode="HTML",
                               reply_markup=InlineKeyboardMarkup(
                                   inline_keyboard=[
                                       [InlineKeyboardButton(text="Подтвердить",
                                                             callback_data="buy_orchid_final_confirm"),
                                        InlineKeyboardButton(text="Отменить", callback_data="cancel")],
                                   ]
                               ))

    await callback_query.answer(text="", show_alert=True)


@soft_router.callback_query(lambda c: c.data == 'buy_orchid_final_confirm')
async def final_confirm_buy_orchid(callback_query: types.CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id
    balance = await db.get_user_balance(user_id)

    if balance < 10:
        await bot.send_message(user_id, "У вас недостаточно средств для покупки! Пожалуйста, пополните ваш баланс.")
    else:

        await db.update_user_balance(user_id, -10)
        # Отправка файла из группы
        try:
            await bot.forward_message(chat_id=user_id, from_chat_id=STOCK_CHANNEL_ID, message_id=10)
            await callback_query.message.delete()
        except Exception as e:
            await callback_query.reply(f"Произошла ошибка: {e}")

        await bot.send_message(user_id, "Спасибо за покупку! Удачного использования, возвращайтесь ещё!")

    await callback_query.answer(text="", show_alert=True)


# photoshop

description_a = """
<b>Приобрести Adobe Photoshop 2024 г. (версия 25.9) | #репак_от_кролика.</b>

<b>Информация о файле:</b> .exe 3366.2MB для Windows 64bit.

Встречайте долгожданное обновление Adobe Photoshop v25.9.0.573, <a href="https://helpx.adobe.com/ru/photoshop/using/whats-new/2024-4.html#adjustment-brush-tool">читать статью</a>. Инструмент «Корректирующая кисть» теперь доступен для обычных пользователей.

💰<b>Цена:</b> 10 USDT – навсегда, с прилагаемой инструкцией по установке.
"""


@soft_router.message(lambda message: message.text == 'Adobe AfterEffects (2024 г.)')
async def buy_orchid(message: types.Message):
    if message.chat.type == 'private':
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Купить 💰", callback_data="buy_orchid_confirm_a")],
            ]
        )
        await message.reply(description_a, parse_mode="HTML", reply_markup=keyboard)


@soft_router.callback_query(lambda c: c.data == 'buy_orchid_confirm_a')
async def confirm_buy_orchid(callback_query: types.CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id
    balance = await db.get_user_balance(user_id)

    if balance < 10:
        await bot.send_message(user_id, "У вас недостаточно средств для покупки. Пожалуйста, пополните баланс.")
    else:
        await bot.send_message(user_id, "Вы уверены, что хотите приобрести Adobe Photoshop 2024 г. (версия 25.9)?",
                               reply_markup=InlineKeyboardMarkup(
                                   inline_keyboard=[
                                       [InlineKeyboardButton(text="Подтвердить",
                                                             callback_data="buy_orchid_final_confirm_a"),
                                        InlineKeyboardButton(text="Отменить", callback_data="cancel")],
                                   ]
                               ))

    await callback_query.answer(text="", show_alert=True)


@soft_router.callback_query(lambda c: c.data == 'buy_orchid_final_confirm_a')
async def final_confirm_buy_orchid(callback_query: types.CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id
    balance = await db.get_user_balance(user_id)

    if balance < 10:
        await bot.send_message(user_id, "У вас недостаточно средств для покупки! Пожалуйста, пополните ваш баланс.")
    else:

        await db.update_user_balance(user_id, -10)
        # Отправка файла из группы
        try:
            await bot.forward_message(chat_id=user_id, from_chat_id=STOCK_CHANNEL_ID, message_id=10)
            await callback_query.message.delete()
        except Exception as e:
            await callback_query.reply(f"Произошла ошибка: {e}")

        await bot.send_message(user_id, "Спасибо за покупку! Удачного использования, возвращайтесь ещё!")

    await callback_query.answer(text="", show_alert=True)


# остальное
@soft_router.callback_query(lambda c: c.data == 'cancel')
async def cancel(callback_query: types.CallbackQuery, bot: Bot):
    await callback_query.message.delete()
