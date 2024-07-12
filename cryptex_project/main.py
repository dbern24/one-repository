import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from data import config as cfg
from data.db import Database
from hundlers import admin_commands, start_hundler, main_menu

logging.basicConfig(level=logging.INFO)

bot = Bot(token=cfg.token)
dp = Dispatcher()
db = Database('data/database.db')


dp.include_routers(

    main_menu.router,
    start_hundler.router,
    admin_commands.router

                  )


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
