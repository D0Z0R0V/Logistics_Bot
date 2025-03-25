from datetime import datetime
import csv, logging


async def export_date(conn):
    try:
        cursor = conn.execute("""
                SELECT
                    c.link,
                    p.post_text,
                    p.status
                FROM posts p
                JOIN channels c ON p.channels_id = c.id""")
        result = await conn.fetchall()
        file_name = f"results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        file_path = f"/bot/logs/{file_name}"
        
        with open(file_path,"w", newline="") as file:
            writen = csv.writer(file)
            writen.writerow(["Ссылка", "Текст поста", "Статус"])
            for row in result:
                writen.writerow(row)
                
        logging.info(f"Результаты мониторинга сохранены в {file_path}")
        return file_path
        
    except Exception as e:
        logging.error(f"Ошибка при экспорте данных {e}")