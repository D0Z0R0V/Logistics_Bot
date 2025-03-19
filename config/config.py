from dotenv import load_dotenv
import os


BOT_TOKEN = os.getenv("BOT_TOKEN")

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "dbuser": os.getenv("DB_USER"),
    "dbpassword": os.getenv("DB_PASSWORD"),
    "dbhost": os.getenv("DB_HOST"),
    "dbport": os.getenv("DB_PORT")
}