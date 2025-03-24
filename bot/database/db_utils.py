from config.config import DB_CONFIG
import asyncpg
import aiosqlite, os
    
async def get_connect():
    try:
        db_path = os.path.abspath('bot/database/database.db')
        conn = await aiosqlite.connect(db_path)
        conn.row_factory = aiosqlite.Row
        return conn
    except aiosqlite.Error as e:
        print("An error occurred while connecting to the database:", e)
        return None
    
#Сохранить каналы и связать их с постом
async def save_post(post_text: str, time_start: str, time_end: str, channels: list):
    db_path = os.path.abspath('bot/database/database.db')
    conn = await aiosqlite.connect(db_path)
    try:
        conn.row_factory = aiosqlite.Row
        for name, link in channels:
            cursor = await conn.execute("SELECT id FROM channels WHERE link = ?", (link,))
            channel = await cursor.fetchone()

            if not channel:
                await conn.execute("INSERT INTO channels (names, link) VALUES (?, ?)", (name, link))
                await conn.commit()
                cursor = await conn.execute("SELECT id FROM channels WHERE link = ?", (link,))
                channel = await cursor.fetchone()
                print(f"✅ Новый канал добавлен: {name} (link: {link})")
            else:
                print(f"ℹ️ Канал уже существует: {name} (ID: {channel[0]})")

            await conn.execute(
                "INSERT INTO posts (channels_id, post_text, time_start, time_end, status) VALUES (?, ?, ?, ?, ?)",
                (channel[0], post_text, time_start, time_end, 0)  # 0 = False
            )
            await conn.commit()
            print(f"✅ Пост успешно сохранен для канала ID: {channel[0]}")

    except aiosqlite.Error as e:
        print(f"Ошибка при сохранении данных: {e}")

    finally:
        await conn.close()
      
async def get_channel(conn):
    try: 
        cursor = await conn.execute("SELECT id, link FROM channels")
        return await cursor.fetchall()
    except Exception as e:
        print(f"Ошибка при получении каналов: {e}")

async def get_post(conn, channel_id):
    try:
        cursor = await conn.execute(
            "SELECT id, post_text, time_start, time_end, status FROM posts WHERE channels_id = ? AND status = 0",
            (channel_id,)
        )
        return await cursor.fetchone()
    except Exception as e:
        print(f"Ошибка при получении поста: {e}")
    
async def update_status(conn, post_id, status):
    try:
        await conn.execute(
            "UPDATE posts SET status = ? WHERE id = ?",
            (status, post_id)
        )
        await conn.commit()
    except Exception as e:
        print(f"Ошибка при обновлении статуса: {e}")

        
async def clear_database(conn):
    try:
        await conn.execute("PRAGMA foreign_keys = OFF;")

        await conn.execute("DELETE FROM posts;")
        await conn.execute("DELETE FROM channels;")
        
        await conn.execute("DELETE FROM sqlite_sequence WHERE name='posts';")
        await conn.execute("DELETE FROM sqlite_sequence WHERE name='channels';")

        await conn.execute("PRAGMA foreign_keys = ON;")
        await conn.commit()

        print("База данных успешно очищена и сброшены счетчики ID.")
    except Exception as e:
        print(f"Ошибка при очистке базы данных: {e}")