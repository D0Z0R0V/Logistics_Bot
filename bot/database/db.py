from config.config import DB_CONFIG
import asyncpg


async def init_db():
    with open("bot/database/schema.sql") as f:
        create_tables = f.read()
        
    conn = await asyncpg.connect(
        user=DB_CONFIG["dbuser"],
        password=DB_CONFIG["dbpassword"],
        database=DB_CONFIG["dbname"],
        host=DB_CONFIG["dbhost"],
        port=DB_CONFIG["dbport"]
    )
    
    try:
        await conn.execute(create_tables)
        print("База инициализирвоана.")
        
    finally:
        await conn.close()