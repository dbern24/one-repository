from aiogram import Bot, types, Router
from aiogram.filters import Command

import data.config as cfg
import keyboard.inline as inl
import keyboard.reply as rpl
import data.long_messages as lmsg


from data.db import Database

db = Database('data/database.db')

router = Router()


@router.message(Command("start"))
async def start(message: types.Message, bot: Bot):
    if message.chat.type == 'private':

        if not db.user_exists(message.from_user.id):
            
            user_id = message.from_user.id
            username = message.from_user.username
            first_name = message.from_user.first_name
            last_name = message.from_user.last_name
            language_code = message.from_user.language_code
        
            info_text = f"<b>Зарегистрирован новый пользователь!</b>\n\n"
            info_text += f"User ID: {user_id}\nСсылка на профиль: <a href='tg://user?id={user_id}'>{first_name}</a>.\n"
            info_text += f"Username: @{username}\n" if username else "No username\n"
            info_text += f"First Name: {first_name}\n"
            info_text += f"Last Name: {last_name}\n" if last_name else "No last name\n"
            info_text += f"Language Code: {language_code}\n" if language_code else "No language code\n"
        
            await bot.send_message(cfg.log_channel, info_text, message_thread_id=cfg.thread_id_start, parse_mode="html")

            await bot.send_photo(message.from_user.id, photo=cfg.photo_start_url, caption=lmsg.start_message(first_name, user_id), parse_mode="html", reply_markup=rpl.mainMenu)

            start_command = message.text
            referrer_id = str(start_command[7:])
            if str(referrer_id) != "":

                if str(referrer_id) != str(message.from_user.id):

                    db.add_user(message.from_user.id, referrer_id)
                    await bot.send_message(message.from_user.id, text="🎊 <b>Благодарим за присоединение!</b> Вам доступно реферальное вознаграждение, за регистрацию по реферальной ссылке!", parse_mode="html", reply_markup=rpl.mainMenuRef)
                    
                    pass

                else:
                    db.add_user(message.from_user.id, 0)
                    await bot.send_message(message.from_user.id, "❌ Нельзя регистрироваться по своей же ссылке!")
            else:
                try:
                    db.add_user(message.from_user.id, 0)
                except Exception as e:
                    print(f"Failed to add user to db: {e}.")
        else:
            user_id = message.from_user.id
            first_name = message.from_user.first_name
            await bot.send_photo(message.from_user.id, photo=cfg.photo_start_url, caption=lmsg.start_message(first_name, user_id), parse_mode="html", reply_markup=rpl.mainMenu)


@router.callback_query(lambda query: query.data == 'subchanneldone')  # Улавливаем нажатие кнопки на проверку того подписался ли пользователь.
async def subchanneldone(message: types.Message, bot: Bot):
    if await check_sub_channels(cfg.channels, message.from_user.id, bot):

        user_id = message.from_user.id
        await bot.send_message(message.from_user.id, text=lmsg.start_message(message.from_user, user_id), parse_mode="markdown", reply_markup=rpl.mainMenu)
        await message.answer(text="", show_alert=True)

    else:
        await bot.send_message(message.from_user.id, text=lmsg.not_sub_message, parse_mode="markdown", reply_markup=inl.showchannels())
        await message.answer(text="", show_alert=True)


async def check_sub_channels(channels, user_id, bot: Bot):
    for channel in channels:
        chat_member = await bot.get_chat_member(channel[1], user_id)
        if chat_member.status == 'left':
            return False
    return True

