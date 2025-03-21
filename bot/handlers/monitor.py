from datetime import datetime, time
from telethon import TelegramClient
from asyncpg import Connection
from bot.database.db_utils import get_connect, get_channel, get_post, update_status
from config.config import API_HASH, API_ID

import asyncio
import logging

SESSION_NAME = "monitoring"

async def check_posts():
    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        logging.info("Запуск мониторинга каналов...")
        
        async with get_connect as conn:
            channels = await get_channel(conn)
            for channel_id, link in channels:
                logging.info(f"Идет проверка канала{link}....")
                try:
                    async for message in client.iter_message(link, limit = 10):
                        post_data = await get_post(conn, channel_id)
                        if post_data:
                            post_id, post_text, time_start, time_end, status = post_data
                            currentt = datetime.now().time()
                            
                            if time_start <= currentt <= time_end:
                                if post_text in message.text:
                                    await update_status(conn, post_id, status)
                                    logging.info(f"✅ Найден пост в {link}")
                                else:
                                    logging.info(f"❌ В {link} пост не найден")
                except Exception as e:
                    logging.error(f"Ошибка при проверке {link}: {e}")
                    
async def monitoring():
    while True:
        current_time = datetime.now().time()
        times = time(10, 20)
        
        if current_time > times:
            logging.info("⏳ Время проверки постов прошло, завершение мониторинга.")
            break
        
        await check_posts()
        logging.info("⏳ Ожидание следующей проверки (1 час)")
        await asyncio.sleep(3600)
