from aiogram import Router, types, Bot, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from my_bot.bot.utils.auxiliary import check_sub_channels, user_not_subscribed_message
from my_bot.bot.utils import database as db

leaderboard_router = Router()

EXCLUDED_USER_ID = 90


@leaderboard_router.message(Command("leaderboard"))
async def leaderboard(message: types.Message, bot: Bot):
    if message.chat.type == 'private':

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Что получают лидеры?", callback_data="withdraw")],
        ])

        if await check_sub_channels(message.from_user.id, bot):
            user_id = message.from_user.id

            top_users = await db.get_top_users_by_balance()
            leaderboard_text = "🏆 <b>Узнайте, кто на вершине рейтинга! Может быть, это вы?</b>\n\n"
            rank = 1
            for user in top_users:
                if user['user_id'] == EXCLUDED_USER_ID:
                    continue

                user_info = await bot.get_chat(user['user_id'])
                username = user_info.first_name
                if user_info.last_name:
                    username += f" {user_info.last_name}"
                leaderboard_text += (f"<b>{rank}.</b> {username} | {user['referrals']} 👥 | {user['balance']:.2f} 💰"
                                     f"\n\n"
                                     )
                rank += 1

            leaderboard_text += ("\nПродолжайте фармить монеты и увеличивайте свой баланс, чтобы занять лидирующие "
                                 "позиции.")

            await message.answer(leaderboard_text, parse_mode="HTML")
        else:
            await user_not_subscribed_message(message, bot)
