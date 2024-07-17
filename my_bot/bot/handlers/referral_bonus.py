from aiogram import Router, types, Bot, F
from aiogram.utils.keyboard import InlineKeyboardBuilder

from my_bot.bot.utils.auxiliary import check_sub_channels, user_not_subscribed_message, referral_menu
from my_bot.bot.utils import database as db
from my_bot.bot.utils.config import referral_reward_price, bot_username

referral_bonus_router = Router()


@referral_bonus_router.message(F.text == '🎁 Реферальный бонус')
async def show_referral_menu(message: types.Message, bot: Bot):
    if message.chat.type == 'private':
        if await check_sub_channels(message.from_user.id, bot):
            await message.reply('Меню «🎁 Реферальный бонус»:', reply_markup=referral_menu)
        else:
            await user_not_subscribed_message(message, bot)


@referral_bonus_router.message(F.text == 'Как работает реферальный бонус? ❓')
async def explain_referral_bonus(message: types.Message, bot: Bot):
    if await check_sub_channels(message.from_user.id, bot):
        message_text = (
            f"<b>Как работает реферальный бонус?</b>\n\n"
            f"Каждый новый пользователь, который присоединяется к нашему боту по вашему приглашению, "
            f"приносит вам и ему самому вознаграждение, но только если пройдет проверку на бота!\n\n"
            f"🎁 <b>Выплата за каждого пользователя:</b> +{referral_reward_price}$\n\n"
            f"Имеете канал с более чем 3.000 подписчиками? Присоединяйтесь к нашей "
            f"<a href='https://t.me/+OqBTRBDNafk1M2Ji'>партнёрской программе</a> прямо сейчас!"
        )
        await message.answer(message_text, parse_mode="HTML")
    else:
        await user_not_subscribed_message(message, bot)


@referral_bonus_router.message(F.text == 'Получить ссылку для приглашения 🔗')
async def get_invitation_link(message: types.Message, bot: Bot):
    if await check_sub_channels(message.from_user.id, bot):
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="Поделиться",
                        url=f"tg://msg_url?url=https://t.me/{bot_username}?start={message.from_user.id}")

        user_id = message.from_user.id
        base_amount_per_referral = 0.20
        referral_count = await db.count_referrals(user_id)
        total_earned = base_amount_per_referral * referral_count

        reward_count_for_user = await db.count_referral_rewards_for_user(user_id)
        total_earned_for_user = base_amount_per_referral * reward_count_for_user

        message_text = (
            f"🎁 <b>Получайте +{referral_reward_price} $USDC за каждого приглашенного друга!</b>\n\n"
            f"<b>Количество приглашенных вами людей:</b> {referral_count}\n"
            f"<b>Количество получивших награду:</b> {reward_count_for_user}\n"
            f"<b>Заработано на приглашенных:</b> {total_earned_for_user:.2f} $USDC\n\n"
            f"[!] Статистика сейчас недоступна, мы работаем над этим.\n\n"
            f"Пригласительная ссылка: <code>https://t.me/{bot_username}?start={user_id}</code>"
        )
        await message.answer(message_text, reply_markup=keyboard.as_markup(), disable_web_page_preview=True,
                             parse_mode="HTML")
    else:
        await user_not_subscribed_message(message, bot)
