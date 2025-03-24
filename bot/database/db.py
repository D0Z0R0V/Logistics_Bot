from config.config import DB_CONFIG
import asyncpg


import aiosqlite

async def init_db():
    async with aiosqlite.connect("bot/database/database.db") as conn:
        with open("bot/database/schema.sql", "r") as f:
            create_tables = f.read()

        await conn.executescript(create_tables)
        print("База инициализирована.")
