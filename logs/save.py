from datetime import datetime
import csv
import logging
import os
from aiogram.types import FSInputFile  # Вместо InputFile

async def export_date(conn, user_id, bot):
    try:
        cursor = await conn.execute("""
            SELECT
                c.link,
                p.post_text,
                p.status
            FROM posts p
            JOIN channels c ON p.channels_id = c.id
            WHERE c.user_id = ?
        """, (user_id,))  # Передаем параметр как кортеж

        result = await cursor.fetchall()

        os.makedirs("logs", exist_ok=True)
        file_name = f"results_{user_id}.csv"
        file_path = os.path.abspath(f"logs/{file_name}")  # Абсолютный путь

        # Записываем данные в CSV
        with open(file_path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Ссылка", "Статус"])
            for row in result:
                writer.writerow([row['link'], row['status']])

        logging.info(f"✅ Результаты мониторинга сохранены в {file_path}")

        # Используем FSInputFile
        input_file = FSInputFile(file_path)
        await bot.send_document(chat_id=user_id, document=input_file, caption="Ваш отчет")

        return file_path

    except Exception as e:
        logging.error(f"❌ Ошибка при экспорте данных: {e}")

