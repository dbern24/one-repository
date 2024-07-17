from aiogram import Router, types, Bot, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from my_bot.bot.utils.auxiliary import check_sub_channels, user_not_subscribed_message
from my_bot.bot.utils import database as db

profile_router = Router()


@profile_router.message(F.text == '💼 Профиль')
async def show_profile(message: types.Message, bot: Bot):
    if message.chat.type == 'private':
        if await check_sub_channels(message.from_user.id, bot):

            user_id = message.from_user.id
            balance = await db.get_user_balance(user_id)

            formatted_balance = f"{balance:.2f}"
            first_name = message.from_user.first_name
            username = message.from_user.username

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Вывод 📥", callback_data="withdraw")],
                 ])

            message_text = (
                f"💼 <b>Детали профиля, {first_name}!</b>"
                f"\n"
                f"├👤 <b>Ваш юзернейм:</b> @{username}"
                f"\n"
                f"├🪪 <b>Ваш ID:</b> {user_id}"
                f"\n"
                f"├🌐 <b>Язык бота:</b> Русский"
                f"\n"
                f"└💶 <b>Текущий баланс:</b> {formatted_balance} $USDC"
                f"\n\n"
                f"🚀 Приглашай друзей через реферальную программу и з"
                f"арабатывай ещё больше $USDC без ограничений по времени майнинга!"
            )

            await message.answer(message_text, reply_markup=keyboard, parse_mode="HTML")
        else:
            await user_not_subscribed_message(message, bot)


@profile_router.callback_query(F.data == 'withdraw') # Поддержка сетей: Polygon, Etherum и другие..
async def withdraw(callback_query: types.CallbackQuery, bot: Bot):
    await callback_query.answer(text="Уже скоро!\n\nВывод AirDrop токенов ($USDC) будет доступен "
                                     "с 30 июля 2024 года в 12:00 UTC.", show_alert=True)