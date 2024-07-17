from aiogram import Router, types, Bot, F
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from my_bot.bot.utils.auxiliary import check_sub_channels, user_not_subscribed_message, help_menu
from my_bot.bot.utils import database as db

help_router = Router()


@help_router.message(F.text == '👩🏻‍🔧 Помощь')
async def show_help_menu(message: types.Message, bot: Bot):
    if message.chat.type == 'private':
        if await check_sub_channels(message.from_user.id, bot):
            await message.reply('Меню «👩🏻‍🔧 Помощь»:', reply_markup=help_menu)
        else:
            await user_not_subscribed_message(message, bot)


@help_router.message(F.text == 'Служба поддержки пользователей 🛠️')
async def show_support_menu(message: types.Message, bot: Bot):
    if await check_sub_channels(message.from_user.id, bot):
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="Вопросы и ответы (F.A.Q.) ❓", url="https://t.me/CrypteXCommunity/12")
        keyboard.button(text="👩🏻‍🔧 Я хочу связаться с службой поддержки!", url="https://t.me/CrypteXSupportBot")

        message_text = (
            f"🔧 <b>Есть замечания или предложения по улучшению работы бота?</b>"
            f"Наша команда поддержки всегда готова помочь и ответить на любой ваш вопрос!"
            f"\n\n"
            f"Поддержка проекта Cryptex работает ежедневно с 10:00 до 3:00 по GMT+2, учитывайте это при обращении!"
        )

        await message.answer(message_text, reply_markup=keyboard.as_markup(), parse_mode="HTML")
    else:
        await user_not_subscribed_message(message, bot)


@help_router.message(F.text == 'Канал и сообщество 🌐')
async def show_community_resources(message: types.Message, bot: Bot):
    if await check_sub_channels(message.from_user.id, bot):
        message_text = (
            f"🌐 <b>Полезные ресурсы нашего проекта:</b>"
            f"\n\n"
            f"<a href='https://t.me/CrypteXCommunity'>CrypteX | Community & News 🗞</a> — Наше сообщество, "
            f"где вы найдете все новости, идеи и обновления нашего проекта!"
            f"\n\n"
            "<a href='https://t.me/+OqBTRBDNafk1M2Ji'>CrypteX | Affiliate Program</a> — Эксклюзивная закрытая "
            "аффилиат-программа (программа партнерства) для партнеров нашего проекта!"
            "\n\n"
            "Если у вас есть канал с более чем 3.000 подписчиков и вы заинтересованы в партнерстве с нами, "
            "не стесняйтесь связаться с нами!"
        )
        await message.answer(message_text, disable_web_page_preview=True, parse_mode="HTML")
    else:
        await user_not_subscribed_message(message, bot)
