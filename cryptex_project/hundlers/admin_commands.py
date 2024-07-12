from aiogram.filters import Command
from aiogram import Router, types, Bot

from data.db import Database
import data.long_messages as lmsg
import data.config as cfg
import keyboard.reply as rpl


db = Database('data/database.db')

router = Router()


@router.message(Command('admin'))
async def admin_command_handler(message: types.Message, bot: Bot):
    if message.chat.type == "private":

        if message.from_user.id in cfg.admin_ids:

            await bot.send_message(message.from_user.id, lmsg.admin_panel, parse_mode="html", reply_markup=rpl.AdmMenu)


        else:
            
            await message.answer("Извините, вы не имеете доступа к этой команде.")


@router.message(lambda message: message.text == "Список спонсоров 👥")
async def admin_command_handler(message: types.Message, bot: Bot):
    if message.chat.type == "private":
        
        if message.from_user.id in cfg.admin_ids:

            formatted_info = ""
            for channel in cfg.channels:
                name = channel[0]
                chat_id = channel[1]
                link = channel[2]
                formatted_info += f"Название канала: {name}\n"
                formatted_info += f"ID чата: {chat_id}\n"
                formatted_info += f"Ссылка на канал: {link}\n\n"

            await bot.send_message(message.from_user.id, formatted_info, disable_web_page_preview=True)

        else:
            
            await message.answer("Извините, вы не имеете доступа к этой команде.")


@router.message(lambda message: message.text == "Управление балансами 💰")
async def admin_command_handler(message: types.Message, bot: Bot):
    if message.chat.type == "private":
        
        if message.from_user.id in cfg.admin_ids:
            
            await bot.send_message(message.from_user.id, "💰 *Используйте команды для упралвения балансами пользователей:*\n\nСнять с баланса: /withdraw [user_id] [сумма].\n\nПросмотр баланса: /check [user_id]\n\nПрибавка к балансу: /add [user_id] [сумма].", parse_mode="markdown")

        else:
            
            await message.answer("Извините, вы не имеете доступа к этой команде.")


@router.message(lambda message: message.text == "Таблица UID лидеров") 
async def admin_command_handler(message: types.Message, bot: Bot):
    if message.chat.type == "private":
        
        if message.from_user.id in cfg.admin_ids:
            
            await bot.send_chat_action(message.chat.id, "typing")
    
            total_users_count = db.count_total_users()
            number_with_offset = total_users_count + 0
            balance = db.get_balance(message.from_user.id)
    
            top_users = db.get_top5_users()
    
            response = f"*🆔 Таблица лидеров включая их UID для управления балансами:*\n"
            for idx, (user_id, balance) in enumerate(top_users, start=1):
                response += f"\n*{idx} {user_id}*: {balance}."
                
            await message.answer(response, parse_mode="markdown")
            
        else:
            
            await message.answer("Извините, вы не имеете доступа к этой команде.")


@router.message(lambda message: message.text == "Cтатистика 📊") 
async def admin_command_handler(message: types.Message, bot: Bot):
    if message.chat.type == "private":
        
        if message.from_user.id in cfg.admin_ids:
            
            await bot.send_chat_action(message.chat.id, "typing")
    
            total_users_count = db.count_total_users()
            number_with_offset = total_users_count + 0
            balance = db.get_balance(message.from_user.id)

            await bot.send_message(message.from_user.id, f"\n\n📇 На текущий момент в боте зарегистрировано {number_with_offset} пользователей!\n\nБолее детальная статистика:\n\nВ разработке...", parse_mode="markdown")
                            
        else:
            
            await message.answer("Извините, вы не имеете доступа к этой команде.")



@router.message(lambda message: message.text == "Рассылка 📩") 
async def admin_command_handler(message: types.Message, bot: Bot):
    if message.chat.type == "private":
        
        if message.from_user.id in cfg.admin_ids:
            
            await bot.send_chat_action(message.chat.id, "typing")

            await message.answer("Рассылка в разработке...", parse_mode="markdown")
                            
        else:
            
            await message.answer("Извините, вы не имеете доступа к этой команде.")
            

@router.message(Command('check'))
async def check_command_handler(message: types.Message):
    if message.chat.type == "private":
        
        if message.from_user.id in cfg.admin_ids:
            
            try:
                command, user_id = message.text.split(' ')
                user_id = int(user_id)
            except ValueError:
                await message.answer("Неправильный формат команды. Используйте /check [user_id].")
                return
            except Exception as e:
                await message.answer(f"Произошла ошибка: {e}")
                return

            balance = db.get_balance(user_id)

            await message.answer(f"Баланс пользователя с ID {user_id}: {balance}.")
            return
        else:
            await message.answer("Извините, вы не имеете доступа к этой команде.")

            pass


@router.message(Command('withdraw'))
async def withdraw_balance_command_handler(message: types.Message, bot: Bot):
    if message.chat.type == "private":
        if message.from_user.id in cfg.admin_ids:
            try:
                command, user_id, amount_str = message.text.split(' ')
                user_id = int(user_id)
                amount = float(amount_str)  # Изменено на float

            except ValueError:
                await message.answer("Неправильный формат команды. Используйте /withdraw [user_id] [сумма]")
                return

            except Exception as e:
                await message.answer(f"Произошла ошибка: {e}")
                return

            if not db.subtract_from_balance(user_id, amount):
                await message.answer(
                    "Не удалось снять сумму с баланса пользователя. Пользователь может иметь недостаточно средств.")
                return

            balance = db.get_balance(user_id)

            await message.answer(f"✅ Успешно обработано изменение баланса пользователя!\n\nБаланс пользователя до: {user_id}: {balance + amount}.\nТекущий баланс пользователя: {user_id}: {balance}.")
            await bot.send_message(cfg.log_channel, f"📤 C баланса пользователя: {user_id}, было снято валюту в кол-во: {amount}!\n\nБаланс пользователя до: {user_id}: {balance + amount}.\nТекущий баланс пользователя: {user_id}: {balance}.", message_thread_id=cfg.thread_id_admin)

            return
        else:
            await message.answer("Извините, вы не имеете доступа к этой команде.")


@router.message(Command('add'))
async def add_balance_command_handler(message: types.Message, bot: Bot):
    if message.chat.type == "private":
        if message.from_user.id in cfg.admin_ids:
            try:
                command, user_id, amount_str = message.text.split(' ')
                user_id = int(user_id)
                amount = float(amount_str)  # Изменено на float

            except ValueError:
                await message.answer("Неправильный формат команды. Используйте /add [user_id] [сумма].")
                return

            except Exception as e:
                await message.answer(f"Произошла ошибка: {e}")
                return

            if amount < 0:
                await message.answer("Сумма должна быть положительным числом.")
                return

            db.add_to_balance(user_id, amount)  # Изменено: не проверяем результат

            balance = db.get_balance(user_id)

            await message.answer(f"✅ Успешно обработано изменение баланса пользователя!\n\nБаланс пользователя до: {user_id}: {balance - amount}.\nТекущий баланс пользователя: {user_id}: {balance}.")
            await bot.send_message(cfg.log_channel, f"📥 К балансу пользователя: {user_id}, была начислена валюта в кол-во: {amount}!\n\nБаланс пользователя до: {user_id}: {balance - amount}.\nТекущий баланс пользователя: {user_id}: {balance}.", message_thread_id=cfg.thread_id_admin)

        else:
            await message.answer("Извините, вы не имеете доступа к этой команде.")

