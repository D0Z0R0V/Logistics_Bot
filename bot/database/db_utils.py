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