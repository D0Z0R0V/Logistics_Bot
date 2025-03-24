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
        
        conn = await get_connect()
        try:
            channels = await get_channel(conn)
            if not channels:
                logging.warning("⚠️ Каналы не найдены в базе данных.")
                return

            for channel_id, link in channels:
                logging.info(f"Идет проверка канала {link}....")
                try:
                    async for message in client.iter_messages(link, limit=10):
                        post_data = await get_post(conn, channel_id)
                        if post_data:
                            post_id, post_text, time_start, time_end, status = post_data
                            current_time = datetime.now().time()
                            
                            if isinstance(time_start, str):
                                time_start = datetime.strptime(time_start, "%H:%M").time()
                            if isinstance(time_end, str):
                                time_end = datetime.strptime(time_end, "%H:%M").time()

                            if time_start <= current_time <= time_end:
                                if (message.text and post_text in message.text) or (message.caption and post_text in message.caption):
                                    await update_status(conn, post_id, 1)
                                    logging.info(f"✅ Найден пост в {link}")
                                else:
                                    logging.info(f"❌ В {link} пост не найден")
                except Exception as e:
                    logging.error(f"Ошибка при проверке {link}: {e}")
        finally:
            await conn.close()

                    
async def monitoring():
    while True:
        current_time = datetime.now().time()
        monitoring_end_time = time(20, 20)

        if current_time > monitoring_end_time:
            logging.info("⏳ Время проверки постов прошло, завершение мониторинга.")
            break

        try:
            await check_posts()
            logging.info("⏳ Ожидание следующей проверки (1 час)")
            await asyncio.sleep(60)
        except Exception as e:
            logging.error(f"Ошибка в мониторинге: {e}", exc_info=True)
            await asyncio.sleep(60) 
