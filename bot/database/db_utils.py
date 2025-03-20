from config import DB_CONFIG
import asyncpg

async def get_connect():
    return await asyncpg.connect(
        user=DB_CONFIG["dbuser"],
        password=DB_CONFIG["dbpassword"],
        database=DB_CONFIG["dbname"],
        host=DB_CONFIG["dbhost"],
        port=DB_CONFIG["dbport"]
    )
    
#Сохранить каналы и связать их с постом
async def save_post(post_text: str, time_start: str, time_end: str, channels: list):
    conn = await get_connect()
    try:
        async with conn.transaction():
            for name, link in channels:
                channel = await conn.fetchrow("SELECT id FROM channels WHERE link = $1", link)
                if not channel:
                    channel_id = await conn.fetchval(
                        "INSERT INTO channels (names, link) VALUES ($1, $2) RETURNING id",
                        name, link
                    )
                else:
                    channel_id = channel["id"]
                    
                await conn.execute(
                    "INSERT INTO posts (channels_id, post_text, time_start, time_end, status) VALUES ($1, $2, $3, $4, $5)",
                    channel_id, post_text, time_start, time_end, False
                )
    finally:
        await conn.close()
        
async def get_channel(conn):
    return await conn.fetch("SELECT id, link FROM channels")

async def get_post(conn, channel_id):
    return await conn.fetchrow(
        "SELECT id, post_text, time_start, time_end FROM posts WHERE channels_id = $1 AND status = FALSE",
        channel_id
    )
    
async def update_status(conn, post_id, status):
    return await conn.execute(
        "UPDATE posts SET status = $1 AND WHERE = $2", status, post_id
    )