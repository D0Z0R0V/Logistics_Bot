from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import asyncio, os, logging

from dotenv import load_dotenv
from config.config import BOT_TOKEN
from bot.database.db import init_db
from bot.handlers import menu, postlist


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token = BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

async def main():
    logging.basicConfig(level = logging.INFO)
    
    dp.include_routers(
        menu.router,
        postlist.router,
    )
    
    try:
        logging.info("Инициализация базы данных......")
        await init_db()
        logging.info("База успешно инициализирована!")
    except Exception as e:
        logging.error(f"Ошибка инициализации: {e}")
        return
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    asyncio.run(main())