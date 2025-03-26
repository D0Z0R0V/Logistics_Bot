from datetime import datetime, time
from telethon import TelegramClient
from asyncpg import Connection
from bot.database.db_utils import get_connect, get_channel, get_post, update_status, get_channel_id
from config.config import API_HASH, API_ID
from logs.save import export_date
from fuzzywuzzy import fuzz
import re

import asyncio, logging, os

SESSION_NAME = "monitoring"

def clean_text(text):
    # должен убрать провелы и препинание
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'[^\w\s]', '', text)
    return text.lower()

async def check_posts(user_id):
    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        logging.info("Запуск мониторинга каналов...")

        conn = await get_connect()
        try:
            channels = await get_channel(conn, user_id)
            if not channels:
                logging.warning("⚠️ Каналы не найдены в базе данных.")
                return

            for row in channels:
                link = row["link"]
                logging.info(f"Идет проверка канала {link}....")

                try:
                    channel_id = await get_channel_id(conn, link, user_id)
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
                                message_text = message.text if message.text else (message.caption if message.caption else "")
                                clean_post_text = clean_text(post_text)
                                clean_message_text = clean_text(message_text)

                                logging.info(f"Текст сообщения: {clean_message_text}")
                                logging.info(f"Ищем текст: {clean_post_text}")

                                similarity = fuzz.partial_ratio(clean_post_text, clean_message_text)
                                logging.info(f"Сходство текста: {similarity}%")

                                if similarity > 80:  # Порог схожести можно регулировать
                                    await update_status(conn, post_id, 1)
                                    logging.info(f"✅ Найден пост в {link} (сходство: {similarity}%)")
                                else:
                                    logging.info(f"❌ В {link} пост не найден (сходство: {similarity}%)")
                except Exception as e:
                    logging.error(f"Ошибка при проверке {link}: {e}")
        finally:
            await conn.close()

                    
async def monitoring(user_id, bot, time_end):
    if isinstance(time_end, str):
        monitoring_end_time = datetime.strptime(time_end, "%H:%M").time()
    elif isinstance(time_end, time):
        monitoring_end_time = time_end
    else:
        raise ValueError("Некорректный формат времени окончания мониторинга")

    logging.info(f"⏳ Мониторинг до {monitoring_end_time}")
    while True:
        current_time = datetime.now().time()
        #monitoring_end_time = time(10, 20)

        if current_time >= monitoring_end_time:
            logging.info("⏳ Время проверки постов прошло, завершение мониторинга.")
            conn = await get_connect()
            await export_date(conn, user_id, bot)
            await conn.close()
            break

        try:
            await check_posts(user_id)
            logging.info("⏳ Ожидание следующей проверки (30 минут)")
            await asyncio.sleep(60)
        except Exception as e:
            logging.error(f"Ошибка в мониторинге: {e}", exc_info=True)
            await asyncio.sleep(60)


