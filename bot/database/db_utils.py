from config.config import DB_CONFIG
import aiosqlite, os, logging
    
async def get_connect():
    try:
        db_path = os.path.abspath('bot/database/database.db')
        conn = await aiosqlite.connect(db_path)
        conn.row_factory = aiosqlite.Row
        return conn
    except aiosqlite.Error as e:
        print("An error occurred while connecting to the database:", e)
        return None


async def save_post(post_text: str, time_start: str, time_end: str, channels: list, user_id: int):
    db_path = os.path.abspath('bot/database/database.db')
    conn = await aiosqlite.connect(db_path)
    
    try:
        conn.row_factory = aiosqlite.Row
        
        # Проверяем, зарегистрирован ли пользователь в базе
        cursor = await conn.execute("SELECT id FROM users WHERE userid = ?", (user_id,))
        user = await cursor.fetchone()
        
        if not user:
            await conn.execute("INSERT INTO users (userid) VALUES (?)", (user_id,))
            await conn.commit()
            cursor = await conn.execute("SELECT id FROM users WHERE userid = ?", (user_id,))
            user = await cursor.fetchone()
            logging.info(f"✅ Новый пользователь добавлен: Telegram ID {user_id}")

        user_db_id = user_id
        
        for link in channels:
            cursor = await conn.execute("SELECT id FROM channels WHERE link = ? AND user_id = ?", (link, user_db_id))
            channel = await cursor.fetchone()

            if not channel:
                await conn.execute("INSERT INTO channels (link, user_id) VALUES (?, ?)", (link, user_db_id))
                await conn.commit()
                cursor = await conn.execute("SELECT id FROM channels WHERE link = ? AND user_id = ?", (link, user_db_id))
                channel = await cursor.fetchone()
                logging.info(f"✅ Новый канал добавлен: {link} для пользователя {user_id}")
            else:
                logging.info(f"ℹ️ Канал уже существует: {link} (ID: {channel['id']}) для пользователя {user_id}")

            await conn.execute(
                "INSERT INTO posts (channels_id, post_text, time_start, time_end, status) VALUES (?, ?, ?, ?, ?)",
                (channel['id'], post_text, time_start, time_end, 0)
            )
            await conn.commit()
            logging.info(f"✅ Пост успешно сохранен для канала ID: {channel['id']}")

    except aiosqlite.Error as e:
        logging.error(f"Ошибка при сохранении данных: {e}")

    finally:
        await conn.close()

async def get_channel(conn, user_id: int):
    try:
        logging.info(f"Получаем каналы для user_id={user_id}")
        cursor = await conn.execute(
            "SELECT id, link FROM channels WHERE user_id = ?", (user_id,)
        )
        result = await cursor.fetchall()
        channels = [dict(row) for row in result]  # Преобразуем в словари для читаемости
        logging.info(f"Найденные каналы: {channels}")
        return result
    except Exception as e:
        logging.error(f"Ошибка при получении каналов: {e}")


async def get_post(conn, channel_id: int):
    try:
        cursor = await conn.execute(
            "SELECT id, post_text, time_start, time_end, status FROM posts WHERE channels_id = ? AND status = 0",
            (channel_id,)
        )
        result = await cursor.fetchone()
        if result:
            logging.info(f"Найденный пост: {dict(result)}")
        return result
    except Exception as e:
        logging.error(f"Ошибка при получении поста: {e}")


async def update_status(conn, post_id: int, status: int):
    try:
        await conn.execute(
            "UPDATE posts SET status = ? WHERE id = ?", (status, post_id)
        )
        await conn.commit()
    except Exception as e:
        logging.error(f"Ошибка при обновлении статуса: {e}")
        
import aiosqlite

async def get_channel_id(conn, link: str, user_id: int):
    try:
        cursor = await conn.execute(
            "SELECT id FROM channels WHERE link = ? AND user_id = ?", (link, user_id)
        )
        result = await cursor.fetchone()

        if result:
            logging.info(f"ID канала для {link}: {result['id']}")
            return result["id"]

        logging.warning(f"Канал {link} для user_id {user_id} не найден.")
        return None
    except Exception as e:
        logging.error(f"Ошибка при получении ID канала: {e}")

