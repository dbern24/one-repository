import random
import time

from aiogram import Router, Bot, types, F
from my_bot.bot.utils.auxiliary import check_sub_channels, user_not_subscribed_message, mining_menu
from my_bot.bot.utils import database as db
from my_bot.bot.utils.config import thread_id_get_usdc, log_channel
from aiogram.utils.keyboard import ReplyKeyboardBuilder

mining_router = Router()

last_button_press = {}


@mining_router.message(F.text == '⛏ Майнинг')
async def menu_plugins(message: types.Message, bot: Bot):
    if message.chat.type == 'private':
        if await check_sub_channels(message.from_user.id, bot):
            await message.reply('Меню «⛏ Майнинг»:', reply_markup=mining_menu)
        else:
            await user_not_subscribed_message(message, bot)


@mining_router.message(F.text == 'Как работает майнинг? ❓')
async def explain_mining(message: types.Message, bot: Bot):
    if await check_sub_channels(message.from_user.id, bot):
        user_id = message.from_user.id
        message_text = (
            f"<b>Как работает майнинг? ❓</b>\n\n"
            f"При нажатии кнопки «Майнинг» вызывается специальная функция, которая случайным образом выбирает вашу "
            f"награду, стоимость каждой награды различна,"
            f"и вы можете выиграть различную сумму в зависимости от вашей удачи!\n\n"
            f"<b>Таким образом, шансы выпадения каждого элемента составляют:</b>\n"
            f"💎 +0.08 (35.7%)\n"
            f"🪙 +0.10 (28.6%)\n"
            f"🌋 +0.11 (21.4%)\n"
            f"⛏ +0.15 (14.3%)"
        )
        await message.answer(message_text, parse_mode="HTML")
    else:
        await user_not_subscribed_message(message, bot)


list_emoji = [
    {"emoji": "💎", "weight": 10, "cost": 0.08},
    {"emoji": "🪙", "weight": 2, "cost": 0.10},
    {"emoji": "🌋", "weight": 1, "cost": 0.11},
    {"emoji": "⛏️", "weight": 1, "cost": 0.15}
]


async def spin_wheel():
    total_weight = sum(emoji["weight"] for emoji in list_emoji)
    random_num = random.uniform(0, total_weight)
    cumulative_weight = 0
    chosen_emoji = None

    for emoji in list_emoji:
        cumulative_weight += emoji["weight"]
        if random_num <= cumulative_weight:
            chosen_emoji = emoji
            break

    return chosen_emoji


@mining_router.message(F.text == 'Получить валюту 💰')
async def get_currency(message: types.Message, bot: Bot):
    if await check_sub_channels(message.from_user.id, bot):
        user_id = message.from_user.id
        current_time = int(time.time())

        if user_id not in last_button_press or current_time - last_button_press[user_id] >= 3600:
            emoji_result = await spin_wheel()
            await db.update_user_balance(user_id, emoji_result["cost"])
            last_button_press[user_id] = current_time

            await bot.send_message(
                log_channel,
                f"{user_id} получает зачисление +{emoji_result['cost']} ({emoji_result['emoji']}) на баланс.",
                message_thread_id=thread_id_get_usdc, parse_mode="html"
            )

            await message.answer(
                f"{emoji_result['emoji']} <b>Поздравляем!</b> К вашему балансу прибавлено +{emoji_result['cost']} $USDC!",
                parse_mode="html"
            )
        else:
            time_left = 3600 - (current_time - last_button_press[user_id])
            await message.answer(f"Попробуйте снова через {time_left // 60} минут!")
    else:
        await user_not_subscribed_message(message, bot)
