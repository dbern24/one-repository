import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties

from utils.config import API_TOKEN
from utils import database as db

from handlers.admin import admin_router
from handlers.start import start_router

from handlers.profile import profile_router
from handlers.help import help_router
from handlers.mining import mining_router
from handlers.referral_bonus import referral_bonus_router
from handlers.leaderboard import leaderboard_router

from utils.auxiliary import auxiliary_router

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.include_router(admin_router)
dp.include_router(start_router)

dp.include_router(profile_router)
dp.include_router(help_router)
dp.include_router(mining_router)
dp.include_router(referral_bonus_router)
dp.include_router(leaderboard_router)

dp.include_router(auxiliary_router)


async def main():
    await db.init_db()
    await dp.start_polling(bot)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
