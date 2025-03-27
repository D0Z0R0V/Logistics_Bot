from datetime import datetime
import csv
import logging
import os
from aiogram.types import FSInputFile

async def export_date(conn, user_id, bot, time_end):
    try:
        cursor = await conn.execute("""
            SELECT id FROM users WHERE userid = ?""",
            (user_id,))
        
        data = await cursor.fetchone()
        data_id = data['id']

        cursor = await conn.execute("""
            SELECT
                c.link,
                p.post_text,
                p.status
            FROM posts p
            JOIN channels c ON p.channels_id = c.id
            WHERE c.user_id = ? AND p.time_end = ?
        """, (user_id, time_end))
        
        result = await cursor.fetchall()

        if not result:
            logging.info(f"❌ Нет данных для отчета (время: {time_end}).")
            return None

        os.makedirs("logs", exist_ok=True)
        time_str = time_end.strftime("%H%M") 
        file_name = f"results_{data_id}_{time_str}.csv"
        file_path = os.path.abspath(f"logs/{file_name}")

        with open(file_path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Ссылка", "Статус"])
            for row in result:
                writer.writerow([row['link'], row['status']])

        logging.info(f"✅ Результаты мониторинга сохранены в {file_path}")

        input_file = FSInputFile(file_path)
        await bot.send_document(chat_id=user_id, document=input_file, caption=f"Ваш отчет за {time_end.strftime('%H:%M')}")

        return file_path

    except Exception as e:
        logging.error(f"❌ Ошибка при экспорте данных: {e}")

