import time
import random

from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Bot, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

import data.config as cfg
import keyboard.inline as inl
import keyboard.reply as rpl

import data.long_messages as lmsg

from data.db import Database


class Form(StatesGroup):
    amount = State()
    wallet = State()


db = Database('data/database.db')
last_button_press = {}

router = Router()


@router.callback_query(lambda query: query.data == 'subchanneldone')
async def subchanneldone(message: types.Message, bot: Bot):
    if await check_sub_channels(cfg.channels, message.from_user.id, bot):

        user_id = message.from_user.id
        first_name = message.from_user.first_name
        await bot.send_photo(message.from_user.id, photo=cfg.photo_start_url,
                             caption=lmsg.start_message(first_name, user_id), parse_mode="html",
                             reply_markup=rpl.mainMenu)

        await message.answer(text="", show_alert=True)

    else:
        await bot.send_message(message.from_user.id, text=lmsg.not_sub_message, parse_mode="html",
                               reply_markup=inl.showchannels())
        await message.answer(text="", show_alert=True)


@router.callback_query(lambda query: query.data == 'subchanneldoneRef')
async def subchanneldone(message: types.Message, bot: Bot):
    if await check_sub_channels(cfg.channels, message.from_user.id, bot):

        await bot.send_message(message.from_user.id, "🎊 <b>Благодарим за присоединение!</b> Вам доступно реферальное вознаграждение, за регистрацию по ссылке пользователя!",
                               parse_mode="html", reply_markup=rpl.mainMenuRef)
        await message.answer(text="", show_alert=True)

    else:
        await bot.send_message(message.from_user.id, text=lmsg.not_sub_message, parse_mode="html",
                               reply_markup=inl.showchannels())
        await message.answer(text="", show_alert=True)


async def check_sub_channels(channels, user_id, bot: Bot):
    for channel in channels:
        chat_member = await bot.get_chat_member(channel[1], user_id)
        if chat_member.status == 'left':
            return False
    return True


@router.message(lambda message: message.text == "🎉 Получить реферальную награду!")
async def bot_message(message: types.Message, bot: Bot):
    if message.chat.type == "private":

        try:

            if await check_sub_channels(cfg.channels, message.from_user.id, bot):

                user_id = message.from_user.id
                refreward_value = db.get_refreward(user_id)
                referrer_id = db.get_referrer_id(user_id)

                await bot.send_chat_action(message.chat.id, "typing")

                if refreward_value:  # Если refreward_value равно True > т.е. ДА юзер получал награду.

                    await bot.send_message(user_id, "❌ Получить награду за регистрацию по реферальной ссылке можно только один раз!", parse_mode="html", reply_markup=rpl.mainMenu)

                else:  # Если refreward_value равно False  > т.е. НЕТ юзер НЕ получал награду.

                    try:

                        db.update_refreward(user_id, 'yes')  # Тут мы обновляем значение на ДА, что юзер уже получал награду после цыкла.
                        await bot.send_message(cfg.log_channel, f"✅ Новый пользователь приглашен по реферальной программе!\n\nПриглашен от: tg://user?id={referrer_id}\n\nПриглашенный пользователь: tg://user?id={user_id}", message_thread_id=cfg.thread_id_ref, parse_mode="html")

                        await bot.send_message(user_id, "🎉 <b>Благодарим за присоединение!</b>\n\nВы и человек, который вас пригласил, получаете дополнительные монеты на счет!", parse_mode="html")
                        db.add_to_balance(user_id, 0.20)

                        await bot.send_message(referrer_id, "🎉 <b>По вашей ссылке зарегистрировался новый пользователь!</b>\n\nНа ваш баланс начислена награда! Спасибо за помощь в развитии нашего проекта!", parse_mode="html")
                        db.add_to_balance(referrer_id, 0.20)

                        user_id = message.from_user.id
                        first_name = message.from_user.first_name
                        await bot.send_photo(message.from_user.id, photo=cfg.photo_start_url,
                                             caption=lmsg.start_message(first_name, user_id), parse_mode="html",
                                             reply_markup=rpl.mainMenu)

                    except Exception as e:
                        await bot.send_message(cfg.log_channel, f"⚠️ <b>Ошибка: (ref_reward) User: {user_id}!</b>\n{e}.", message_thread_id=cfg.thread_id_sponsor, parse_mode="html")

            else:
                await bot.send_chat_action(message.chat.id, "typing")
                await bot.send_message(message.from_user.id, text=lmsg.not_sub_message, parse_mode="html",
                                       reply_markup=inl.showchannelsRef())

        except Exception as e:
            await bot.send_message(cfg.log_channel, f"⚠️ <b>Ошибка:</b> {e}.", message_thread_id=cfg.thread_id_sponsor, parse_mode="html")
            await bot.send_message(message.from_user.id, "⚠️ <b>Произошла ошибка!</b> Пожалуйста, попробуйте позже. Отчет о проблеме отправлен модераторам!",
                                   parse_mode="html")
            print(f"Failed [Профиль]: {e}.")


@router.message(lambda message: message.text == "💼 Профиль")
async def bot_message(message: types.Message, bot: Bot):
    if message.chat.type == "private":

        try:

            if await check_sub_channels(cfg.channels, message.from_user.id, bot):
                await bot.send_chat_action(message.chat.id, "typing")

                balance = db.get_balance(message.from_user.id)
                user_id = message.from_user.id
                user = await bot.get_chat(user_id)
                user_firs_name = user.first_name
                user_name = user.username

                withdraw = InlineKeyboardBuilder()
                withdraw.button(text="Вывод 📥", callback_data="process_withdraw_step")
                withdraw.adjust(1)

                await bot.send_message(message.from_user.id, lmsg.profile_message(user_firs_name, user_id, balance),
                                       parse_mode="html", reply_markup=withdraw.as_markup())

            else:
                await bot.send_chat_action(message.chat.id, "typing")
                await bot.send_message(message.from_user.id, text=lmsg.not_sub_message, parse_mode="html",
                                       reply_markup=inl.showchannels())

        except Exception as e:
            await bot.send_message(cfg.log_channel, f"⚠️ <b>Ошибка:</b> {e}.", message_thread_id=cfg.thread_id_sponsor,
                                   parse_mode="html")
            await bot.send_message(message.from_user.id, "⚠️ <b>Произошла ошибка!</b> Пожалуйста, попробуйте позже. Отчет о проблеме отправлен модераторам!",
                                   parse_mode="html")


# Cистема по выводу.

@router.callback_query(lambda query: query.data == 'process_withdraw_step')
async def process_withdraw(callback_query: types.CallbackQuery, bot: Bot):

    confirm = InlineKeyboardBuilder()
    confirm.button(text="Я ознакомился и подтверждаю вывод! ✅", callback_data="process_withdraw_step_two")
    confirm.button(text="Отменить ❌", callback_data="cancel_withdraw")
    confirm.adjust(2)

    balance = db.get_balance(callback_query.from_user.id)

    if balance <= 20:  # В случае если баланс меньше 10:

        await callback_query.answer(text='', show_alert=True)
        await bot.send_message(callback_query.from_user.id,
                               "❌ К сожалению, у вас недостаточно средств для выполнения этой операции! Минимальная сумма вывода составляет не менее 20 $USDC!")
    else:
        await callback_query.answer(text='', show_alert=True)
        await bot.send_message(callback_query.from_user.id, lmsg.withdraw_message(), parse_mode="html", reply_markup=confirm.as_markup())


@router.callback_query(lambda query: query.data == 'process_withdraw_step_two')
async def process_withdraw(callback_query: types.CallbackQuery, bot: Bot):

    usdt = InlineKeyboardBuilder()
    usdt.button(text="$USDC в сети BEP-20", callback_data="process_withdraw_usdc")
    usdt.button(text="Отменить ❌", callback_data="cancel_withdraw")
    usdt.adjust(1)

    await callback_query.message.delete()
    await bot.send_message(callback_query.from_user.id, f"Пожалуйста, выберите валюту из списка ниже для проведения операции вывода:\n\nПри выводе средств может взиматься комиссия в размере от 10% до 30%, которая используется для оплаты труда модераторов.", parse_mode="html", reply_markup=usdt.as_markup())
    await callback_query.answer(text='', show_alert=True)


@router.callback_query(lambda query: query.data == 'process_withdraw_usdc')
async def process_withdraw(callback_query: types.CallbackQuery, bot: Bot):
    balance = db.get_balance(callback_query.from_user.id)

    if balance <= 20:  # В случае если баланс меньше 10:
        await bot.send_message(callback_query.from_user.id,
                               "❌ К сожалению, у вас недостаточно средств для выполнения этой операции!")
        await callback_query.answer(text='', show_alert=True)

    else:

        accept = InlineKeyboardBuilder()
        accept.button(text="Я согласен ✅", callback_data="process_next_usdс")
        accept.button(text="Отменить ❌", callback_data="cancel_withdraw")
        accept.adjust(2)

        await bot.send_message(callback_query.from_user.id, lmsg.alert_message(), parse_mode="html", reply_markup=accept.as_markup())
        await callback_query.answer(text='', show_alert=True)
        await callback_query.message.delete()
        return


@router.callback_query(lambda query: query.data == 'process_next_usdс')
async def process_withdraw(callback_query: types.CallbackQuery, state: FSMContext):

    cancel = InlineKeyboardBuilder()
    cancel.button(text="Отменить процедуру ❌", callback_data="cancel_withdraw")
    cancel.adjust(1)

    await callback_query.message.answer(f"Введите желаемую сумму USDC для вывода:", reply_markup=cancel.as_markup())
    await callback_query.answer(text='', show_alert=True)
    await callback_query.message.delete()
    await state.set_state(Form.amount)


@router.callback_query(lambda query: query.data == 'cancel_withdraw')
async def process_cancle(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer(text='', show_alert=True)
    await callback_query.message.delete()
    await state.clear()
    return


@router.message(Form.amount)
async def process_amount(message: Message, state: FSMContext) -> None:
    if message.text.isdigit():

        balance = db.get_balance(message.from_user.id)
        amount = float(message.text)

        if 0 <= amount <= balance:

            cancel = InlineKeyboardBuilder()
            cancel.button(text="Отменить процедуру ❌", callback_data="cancel_withdraw")
            cancel.adjust(1)

            await state.update_data(amount=amount)
            await message.answer(f"Теперь введите ваш USDC кошелек в сети BEP-20:", reply_markup=cancel.as_markup())
            await state.set_state(Form.wallet)
        else:

            repeat = InlineKeyboardBuilder()
            repeat.button(text="Повторить процедуру 🔄", callback_data="process_next_usdс")
            repeat.adjust(1)

            await message.answer(f"Введенное вами число должно быть больше 0 и не превышать ваш текущий баланс.", reply_markup=repeat.as_markup())
            await state.clear()
    else:

        repeat = InlineKeyboardBuilder()
        repeat.button(text="Повторить процедуру 🔄", callback_data="process_next_usdс")
        repeat.adjust(1)

        await message.answer(f"Ввести можно только число, повторите процедуру вновь!", reply_markup=repeat.as_markup())
        await state.clear()


@router.message(Form.wallet)
async def process_amount(message: Message, state: FSMContext, bot: Bot) -> None:
    await state.update_data(wallet=message.text)

    data = await state.get_data()
    amount = data.get('amount')
    wallet = message.text

    msg_withdraw_user = f"""
    ✅ <b>Заявка на вывод успешно подана и будет рассмотрена в ближайшее время!</b>\n\n<b>Указанный кошелек:</b> {str(wallet)}.\n<b>Сумма вывода:</b> {str(amount)}.\n\n<blockquote>Вывод средств на ваш кошелек может занять от 15 минут до 48 часов до того момента, когда запрос будет обработан.</blockquote> \n\nВаш аккаунт будет проверен на нарушения правил, мультиаккаунтинг и другие запрещенные методы. В случае нарушения ваша нагарада будет обнулена.
    """

    await message.answer(msg_withdraw_user, parse_mode="html")

    user_id = message.from_user.id
    user = await bot.get_chat(user_id)
    user_first_name = user.first_name
    user_name = user.username

    msg_withdraw = f"""
    ⚠️ <b>Пользователь подал заявку на вывод средств!</b>
    \n\n<b>Имя:</b> {user_first_name}.\n<b>ID:</b> {user_id}.\n<b>Username:</b> @{user_name}.\n\n<b>Информация для вывода:</b>\nКошелек: {str(wallet)}.\nСумма: {str(amount)}.\n\n<b>Для снятия суммы с пользователя используйте эту команду:</b> /withdraw {user_id} {str(amount)}.
    """

    await bot.send_message(cfg.log_channel, msg_withdraw, parse_mode="html")
    await state.clear()


# Продолжение главного меню.

@router.message(lambda message: message.text == "👩🏻‍🔧 Помощь")
async def knowledge_base_hundler(message: types.Message, bot: Bot):
    if message.chat.type == "private":

        try:

            await bot.send_chat_action(message.chat.id, "typing")
            await bot.send_message(message.from_user.id, "Вы перешли к меню «👩🏻‍🔧 Помощь»:", reply_markup=rpl.helpMenu,
                                   parse_mode="html")

        except Exception as e:
            await bot.send_message(cfg.log_channel, f"⚠️ <b>Failed:</b> {e}.", message_thread_id=cfg.thread_id_sponsor,
                                   parse_mode="html")
            await bot.send_message(message.from_user.id, "⚠️ <b>Произошла ошибка!</b> Пожалуйста, попробуйте позже. Отчет о проблеме отправлен модераторам!",
                                   parse_mode="html")


@router.message(lambda message: message.text == "Служба поддержки пользователей 🛠️")
async def knowledge_base_hundler(message: types.Message, bot: Bot):
    if message.chat.type == "private":

        try:

            await bot.send_chat_action(message.chat.id, "typing")

            support = InlineKeyboardBuilder()
            support.button(text="👩🏻‍🔧 Я хочу связаться с службой поддержки!", url="https://t.me/CrypteXSupportBot")
            support.adjust(1)

            await message.answer(lmsg.support_message(), reply_markup=support.as_markup(), parse_mode="html")

        except Exception as e:
            await bot.send_message(cfg.log_channel, f"⚠️ <b>Failed:</b> {e}.", message_thread_id=cfg.thread_id_sponsor,
                                   parse_mode="html")
            await bot.send_message(message.from_user.id, "⚠️ <b>Произошла ошибка!</b> Пожалуйста, попробуйте позже. Отчет о проблеме отправлен модераторам!",
                                   parse_mode="html")


@router.message(lambda message: message.text == "Канал и сообщество 🌐")
async def knowledge_base_hundler(message: types.Message, bot: Bot):
    if message.chat.type == "private":

        try:

            await bot.send_chat_action(message.chat.id, "typing")
            await bot.send_message(message.from_user.id, lmsg.resources, parse_mode="html", disable_web_page_preview=True)

        except Exception as e:
            await bot.send_message(cfg.log_channel, f"⚠️ <b>Ошибка:</b> {e}.", message_thread_id=cfg.thread_id_sponsor,
                                   parse_mode="html")
            await bot.send_message(message.from_user.id, "⚠️ <b>Произошла ошибка!</b> Пожалуйста, попробуйте позже. Отчет о проблеме отправлен модераторам!",
                                   parse_mode="html")


@router.message(lambda message: message.text == "Вопросы и ответы ❓")
async def knowledge_base_hundler(message: types.Message, bot: Bot):
    if message.chat.type == "private":

        try:

            await bot.send_chat_action(message.chat.id, "typing")

            knowledge_base = InlineKeyboardBuilder()
            knowledge_base.button(text="Как работает наш бот?", callback_data="knowledge_answer_1")
            knowledge_base.button(text="Необходимо ли вкладывать деньги для использования бота?", callback_data="knowledge_answer_2")
            knowledge_base.button(text="Как можно вывести средства из бота?", callback_data="knowledge_answer_3")
            knowledge_base.button(text="Где мы берем финансирование нашего проекта?", callback_data="knowledge_answer_4")
            knowledge_base.button(text="Какие обновления и контент проекта нас ждут?", callback_data="knowledge_answer_5")
            knowledge_base.adjust(1)

            await message.answer(lmsg.knowledge_base, reply_markup=knowledge_base.as_markup(), parse_mode="html")

        except Exception as e:
            await bot.send_message(cfg.log_channel, f"⚠️ <b>Ошибка:</b> {e}.", message_thread_id=cfg.thread_id_sponsor,
                                   parse_mode="html")
            await bot.send_message(message.from_user.id, "⚠️ <b>Произошла ошибка!</b> Пожалуйста, попробуйте позже. Отчет о проблеме отправлен модераторам!",
                                   parse_mode="html")


@router.callback_query(lambda query: query.data == 'knowledge_answer_1')
async def knowledge_answer_1(callback_query: types.CallbackQuery, bot: Bot):

    cancel = InlineKeyboardBuilder()
    cancel.button(text="Я прочел, удалить 🗑", callback_data="cancel_withdraw")
    cancel.adjust(1)

    await callback_query.answer(text='', show_alert=True)
    await bot.send_message(callback_query.from_user.id, text=lmsg.knowledge_answer_1, reply_markup=cancel.as_markup(), parse_mode="html")


@router.callback_query(lambda query: query.data == 'knowledge_answer_2')
async def knowledge_answer_1(callback_query: types.CallbackQuery, bot: Bot):

    cancel = InlineKeyboardBuilder()
    cancel.button(text="Я прочел, удалить 🗑", callback_data="cancel_withdraw")
    cancel.adjust(1)

    await callback_query.answer(text='', show_alert=True)
    await bot.send_message(callback_query.from_user.id, text=lmsg.knowledge_answer_2, reply_markup=cancel.as_markup(), parse_mode="html")


@router.callback_query(lambda query: query.data == 'knowledge_answer_3')
async def knowledge_answer_1(callback_query: types.CallbackQuery, bot: Bot):

    cancel = InlineKeyboardBuilder()
    cancel.button(text="Я прочел, удалить 🗑", callback_data="cancel_withdraw")
    cancel.adjust(1)

    await callback_query.answer(text='', show_alert=True)
    await bot.send_message(callback_query.from_user.id, text=lmsg.knowledge_answer_3, reply_markup=cancel.as_markup(), parse_mode="html")


@router.callback_query(lambda query: query.data == 'knowledge_answer_4') 
async def knowledge_answer_1(callback_query: types.CallbackQuery, bot: Bot):

    cancel = InlineKeyboardBuilder()
    cancel.button(text="Я прочел, удалить 🗑", callback_data="cancel_withdraw")
    cancel.adjust(1)

    await callback_query.answer(text='', show_alert=True)
    await bot.send_message(callback_query.from_user.id, text=lmsg.knowledge_answer_4, reply_markup=cancel.as_markup(), parse_mode="html")


@router.callback_query(lambda query: query.data == 'knowledge_answer_5')
async def knowledge_answer_1(callback_query: types.CallbackQuery, bot: Bot):

    cancel = InlineKeyboardBuilder()
    cancel.button(text="Я прочел, удалить 🗑", callback_data="cancel_withdraw")
    cancel.adjust(1)

    await callback_query.answer(text='', show_alert=True)
    await bot.send_message(callback_query.from_user.id, text=lmsg.knowledge_answer_5, reply_markup=cancel.as_markup(), parse_mode="html")


@router.message(Command("leaderboard"))
async def leader_hundler(message: types.Message, bot: Bot):
    if message.chat.type == "private":
        try:

            if await check_sub_channels(cfg.channels, message.from_user.id, bot):
                await bot.send_chat_action(message.chat.id, "typing")

                total_users_count = db.count_total_users()
                number_with_offset = total_users_count + 0
                balance = db.get_balance(message.from_user.id)

                top_users = db.get_top5_users()

                response = f"*🏆 Топ-20 пользователей лидирующих по балансу:*\n"
                for idx, (user_id, balance) in enumerate(top_users, start=1):
                    response += f"\n*{idx} место*: *текущий баланс:* {balance} $USDC"

                response += f"\n\n📇 *Пользователей зарегистрировано в нашем боте:* {number_with_offset}."

                await message.answer(response, parse_mode="markdown")

            else:
                await bot.send_chat_action(message.chat.id, "typing")
                await bot.send_message(message.from_user.id, text=lmsg.not_sub_message, parse_mode="html",
                                       reply_markup=inl.showchannels())

        except Exception as e:
            await bot.send_message(cfg.log_channel, f"⚠️ <b>Ошибка::</b> {e}.", message_thread_id=cfg.thread_id_sponsor,
                                   parse_mode="html")
            await bot.send_message(message.from_user.id, "⚠️ <b>Произошла ошибка!</b> Пожалуйста, попробуйте позже. Отчет о проблеме отправлен модераторам!",
                                   parse_mode="html")


URL_P = "https://telegra.ph/file/0749d3088c2c4e1479f45.png"

message_text_ad = (
    """ 

🔥 <b>Внимание, криптоэнтузиасты!</b> 🔥

Хотите быть в курсе всех аирдропов и ретродропов с бесплатной раздачей криптовалют? 💸 Тогда <a href='https://t.me/+t6zummR7uvRlYzQ6'>наш канал</a> - именно то, что вам нужно!

<b>Присоединяйтесь к <a href='https://t.me/+t6zummR7uvRlYzQ6'>VILLI_AL</a> в Telegram, и вы получите:</b>
🚀 Эксклюзивные новости и аналитика по криптовалютам
🎁 Уведомления о самых выгодных бесплатных раздачах криптовалют
📈 Советы и стратегии от экспертов для успешного развития в сфере криптовалют

Не упустите шанс увеличить свои знания и прибыль! Подписывайтесь на <a href='https://t.me/+t6zummR7uvRlYzQ6'>VILLI_AL</a> прямо сейчас и становитесь частью нашего криптосообщества! 💎

    """
)


@router.message(lambda message: message.text == "🎁 Реферальный бонус")
async def knowledge_base_hundler(message: types.Message, bot: Bot):
    if message.chat.type == "private":

        try:

            await bot.send_chat_action(message.chat.id, "typing")

            await bot.send_message(message.from_user.id, "Вы перешли к меню «🎁 Реферальный бонус»:",
                                   reply_markup=rpl.refMenu, parse_mode="html")

            await bot.send_photo(message.from_user.id, photo=URL_P, caption=message_text_ad, parse_mode="html")
            await bot.send_message(6769252698, text="+1 показ.", parse_mode="html")


        except Exception as e:
            await bot.send_message(cfg.log_channel, f"⚠️ <b>Ошибка:</b> {e}.", message_thread_id=cfg.thread_id_sponsor,
                                   parse_mode="html")
            await bot.send_message(message.from_user.id,
                                   "⚠️ <b>Произошла ошибка!</b> Пожалуйста, попробуйте позже. Отчет о проблеме отправлен модераторам!",
                                   parse_mode="html")


@router.message(lambda message: message.text == "Как работает реферальный бонус? ❓")
async def referral_hundler(message: types.Message, bot: Bot):
    if message.chat.type == "private":
        try:
            if await check_sub_channels(cfg.channels, message.from_user.id, bot):
                await bot.send_chat_action(message.chat.id, "typing")

                how = InlineKeyboardBuilder()
                how.button(text="Какие условия получения награды?", callback_data="how_claim_ref_reward")
                how.adjust(1)

                await message.answer(lmsg.ref_q_message(), disable_web_page_preview=True, reply_markup=how.as_markup(), parse_mode="html")

            else:
                await bot.send_chat_action(message.chat.id, "typing")
                await bot.send_message(message.from_user.id, text=lmsg.not_sub_message, parse_mode="html",
                                       reply_markup=inl.showchannels())

        except Exception as e:
            await bot.send_message(cfg.log_channel, f"⚠️ <b>Ошибка:</b> {e}.", message_thread_id=cfg.thread_id_sponsor,
                                   parse_mode="html")
            await bot.send_message(message.from_user.id, "⚠️ <b>Произошла ошибка!</b> Пожалуйста, попробуйте позже. Отчет о проблеме отправлен модераторам!",
                                   parse_mode="html")


@router.callback_query(lambda query: query.data == 'how_claim_ref_reward')
async def how_claim_ref_reward(callback_query: types.CallbackQuery, bot: Bot):

    try:

        bonus = InlineKeyboardBuilder()
        bonus.button(text="Вернуться обратно 🔙", callback_data="how_working_ref_bonus")
        bonus.adjust(1)

        await callback_query.answer(text='', show_alert=True)
        await callback_query.message.edit_text(lmsg.ref_q_inline_message(), reply_markup=bonus.as_markup(), parse_mode="html")
    except Exception as e:
        await callback_query.bot.send_message(cfg.log_channel, f"⚠️ <b>Ошибка:</b> {e}.", parse_mode="html")
        await callback_query.message.answer("⚠️ <b>Произошла ошибка!</b> Пожалуйста, попробуйте позже.", parse_mode="html")


@router.callback_query(lambda query: query.data == 'how_working_ref_bonus')
async def how_working_ref_bonus(callback_query: types.CallbackQuery, bot: Bot):

    try:

        how = InlineKeyboardBuilder()
        how.button(text="Какие условия получения награды?", callback_data="how_claim_ref_reward")
        how.adjust(1)

        await callback_query.answer(text='', show_alert=True)
        await callback_query.message.edit_text(lmsg.ref_q_message(), disable_web_page_preview=True, reply_markup=how.as_markup(), parse_mode="html")

    except Exception as e:
        await callback_query.bot.send_message(cfg.log_channel, f"⚠️ <b>Ошибка:</b> {e}.", parse_mode="html")
        await callback_query.message.answer("⚠️ <b>Произошла ошибка!</b> Пожалуйста, попробуйте позже.", parse_mode="html")


@router.message(lambda message: message.text == "Получить ссылку для приглашения 🔗")
async def referral_hundler(message: types.Message, bot: Bot):
    if message.chat.type == "private":
        try:
            if await check_sub_channels(cfg.channels, message.from_user.id, bot):

                await bot.send_chat_action(message.chat.id, "typing")

                user_id = message.from_user.id

                builder = InlineKeyboardBuilder()
                builder.button(text="Поделиться ссылкой!",
                               url=f"tg://msg_url?url=https://t.me/{cfg.bot_username}?start={user_id}")
                builder.adjust(1)

                base_amount_per_referral = 0.20
                referral_count = db.count_reeferals(message.from_user.id)
                total_earned = base_amount_per_referral * referral_count

                reward_count_for_user = db.count_referral_rewards_for_user(message.from_user.id)
                total_earned_for_user = base_amount_per_referral * reward_count_for_user

                await message.answer(
                    text=lmsg.ref_link_message(reward_count_for_user, total_earned_for_user, user_id, db, cfg),
                    reply_markup=builder.as_markup(), parse_mode="html")


            else:
                await bot.send_chat_action(message.chat.id, "typing")
                await bot.send_message(message.from_user.id, text=lmsg.not_sub_message, parse_mode="html",
                                       reply_markup=inl.showchannels())

        except Exception as e:
            await bot.send_message(cfg.log_channel, f"⚠️ <b>Failed:</b> {e}.", message_thread_id=cfg.thread_id_sponsor,
                                   parse_mode="html")
            await bot.send_message(message.from_user.id, "⚠️ <b>Произошла ошибка!</b> Пожалуйста, попробуйте позже. Отчет о проблеме отправлен модераторам!",
                                   parse_mode="html")


@router.message(lambda message: message.text == "⛏ Майнинг")
async def knowledge_base_hundler(message: types.Message, bot: Bot):
    if message.chat.type == "private":

        try:

            await bot.send_chat_action(message.chat.id, "typing")

            await bot.send_message(message.from_user.id, "Вы перешли к меню «⛏ Майнинг»:", reply_markup=rpl.claimMenu,
                                   parse_mode="html")

        except Exception as e:
            await bot.send_message(cfg.log_channel, f"⚠️ <b>Failed:</b> {e}.", message_thread_id=cfg.thread_id_sponsor,
                                   parse_mode="html")
            await bot.send_message(message.from_user.id, "⚠️ <b>Произошла ошибка!</b> Пожалуйста, попробуйте позже. Отчет о проблеме отправлен модераторам!",
                                   parse_mode="html")


@router.message(lambda message: message.text == "Как работает майнинг? ❓")
async def referral_hundler(message: types.Message, bot: Bot):
    if message.chat.type == "private":
        try:
            if await check_sub_channels(cfg.channels, message.from_user.id, bot):
                await bot.send_chat_action(message.chat.id, "typing")

                await message.answer(lmsg.how_claim_message(), parse_mode="html")

            else:
                await bot.send_chat_action(message.chat.id, "typing")
                await bot.send_message(message.from_user.id, text=lmsg.not_sub_message, parse_mode="html",
                                       reply_markup=inl.showchannels())

        except Exception as e:
            await bot.send_message(cfg.log_channel, f"⚠️ <b>Failed:</b> {e}.", message_thread_id=cfg.thread_id_sponsor,
                                   parse_mode="html")
            await bot.send_message(message.from_user.id, "⚠️ <b>Произошла ошибка!</b> Пожалуйста, попробуйте позже. Отчет о проблеме отправлен модераторам!",
                                   parse_mode="html")


# Чем выше вес, тем больше вероятность, что этот смайлик будет выбран при вращении рулетки.

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


@router.message(lambda message: message.text == "Получить валюту 💰")
async def bot_message(message: types.Message, bot: Bot):
    if message.chat.type == "private":
        try:
            if await check_sub_channels(cfg.channels, message.from_user.id, bot):
                await bot.send_chat_action(message.chat.id, "typing")
                user_id = message.from_user.id
                current_time = int(time.time())

                if user_id not in last_button_press or current_time - last_button_press[user_id] >= 3600:
                    # Вращаем рулетку
                    emoji_result = await spin_wheel()
                    # Добавляем сумму на баланс
                    db.add_to_balance(user_id, emoji_result["cost"])
                    last_button_press[user_id] = current_time

                    await bot.send_message(cfg.log_channel, f"{user_id} получает зачисление +{emoji_result['cost']} ({emoji_result['emoji']}) на баланс.",
                                           message_thread_id=cfg.thread_id_get_usdc, parse_mode="html")

                    await message.answer(f"{emoji_result['emoji']} <b>Поздравляем!</b> К вашему балансу добавлено +{emoji_result['cost']} $USDC!",
                                         parse_mode="html")
                else:
                    time_left = 3600 - (current_time - last_button_press[user_id])
                    await message.answer(f"Попробуйте снова через {time_left // 60} минут!")
            else:
                await bot.send_chat_action(message.chat.id, "typing")
                await bot.send_message(message.from_user.id, text=lmsg.not_sub_message, parse_mode="html",
                                       reply_markup=inl.showchannels())
        except Exception as e:
            await bot.send_message(cfg.log_channel, f"⚠️ <b>Failed:</b> {e}.", message_thread_id=cfg.thread_id_sponsor,
                                   parse_mode="html")
            await bot.send_message(message.from_user.id, "⚠️ <b>Произошла ошибка!</b> Пожалуйста, попробуйте позже. Отчет о проблеме отправлен модераторам!",
                                   parse_mode="html")


@router.message(lambda message: message.text == "⬅️ Назад")
async def start(message: types.Message, bot: Bot):
    if message.chat.type == 'private':

        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        language_code = message.from_user.language_code

        if not db.user_exists(message.from_user.id):

            info_text = f"<b>Зарегистрирован новый пользователь! Используя «⬅️ Назад».</b>\n\n"
            info_text += f"User ID: {user_id}\nСсылка на профиль: <a href='tg://user?id={user_id}'>{first_name}</a>.\n"
            info_text += f"Username: @{username}\n" if username else "No username\n"
            info_text += f"First Name: {first_name}\n"
            info_text += f"Last Name: {last_name}\n" if last_name else "No last name\n"
            info_text += f"Language Code: {language_code}\n" if language_code else "No language code\n"

            await bot.send_message(cfg.log_channel, info_text, message_thread_id=cfg.thread_id_start, parse_mode="html")
            await bot.send_photo(message.from_user.id, photo=cfg.photo_start_url, caption=lmsg.start_message(first_name, user_id), parse_mode="html", reply_markup=rpl.mainMenu)

            try:
                db.add_user(message.from_user.id, 0)
            except Exception as e:
                await bot.send_message(cfg.log_channel, f"Failed to add user to db: {e}.",
                                       message_thread_id=cfg.thread_id_db, parse_mode="html")
        else:
            await bot.send_photo(message.from_user.id, photo=cfg.photo_start_url, caption=lmsg.start_message(first_name, user_id), parse_mode="html", reply_markup=rpl.mainMenu)
