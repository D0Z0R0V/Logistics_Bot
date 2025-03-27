from aiogram import Router, F
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import Bot

from bot.database.db_utils import save_post
from bot.handlers.monitor import monitoring
import asyncio
import re

router = Router()

class AddCheck(StatesGroup):
    CHANNELS = State()
    POST_TEXT = State()
    TIME_RANGE = State()

@router.message(Command("add_check"))
async def get_posts(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(user_id=user_id)

    await message.answer("Отправьте список каналов (каждая ссылка на новой строчке). Пример:\nhttps://t.me/example_channel")
    await state.set_state(AddCheck.CHANNELS)

@router.message(AddCheck.CHANNELS)
async def process_channel(message: Message, state: FSMContext):
    valid_channels = set()
    
    # Регулярка для ссылок
    pattern = r"https?://(?:t\.me|telegram\.me)/(?:[a-zA-Z0-9_]{5,32}|\+[a-zA-Z0-9_-]+|c/\d+/[0-9]+|[a-zA-Z0-9_]{5,32}/\d+|\+[a-zA-Z0-9_-]+)"

    # 1️⃣ Обработка ссылок внутри текста (text_link)
    if message.entities:
        for entity in message.entities:
            if entity.type == "text_link":  
                valid_channels.add(entity.url)

    # 2️⃣ Обработка явных ссылок в тексте
    for line in message.text.split("\n"):
        link = line.strip()
        if re.match(pattern, link):
            valid_channels.add(link)
        else:
            matches = re.findall(pattern, link)
            valid_channels.update(matches)

    if not valid_channels:
        await message.answer("❌ Не удалось получить ни одной корректной ссылки на канал. Попробуйте снова.")
        return

    await state.update_data(channels=list(valid_channels))
    await message.answer("✅ Ссылки успешно обработаны. Теперь отправьте полный текст поста.")
    await state.set_state(AddCheck.POST_TEXT)

@router.message(AddCheck.POST_TEXT)
async def get_post(message: Message, state: FSMContext):
    await state.update_data(post_text=message.text)
    await message.answer("Введите временной интервал в формате HH:MM-HH:MM (например, 08:00-10:00).")
    await state.set_state(AddCheck.TIME_RANGE)

@router.message(AddCheck.TIME_RANGE, F.text.contains("-"))
async def get_time(message: Message, state: FSMContext):
    time_range = message.text.strip()

    if "-" not in time_range:
        await message.answer("❌ Некорректный формат. Введите в формате HH:MM-HH:MM.")
        return

    time_start, time_end = time_range.split("-")
    user_data = await state.get_data()

    await save_post(
        post_text=user_data["post_text"],
        time_start=time_start.strip(),
        time_end=time_end.strip(),
        channels=user_data["channels"],
        user_id=user_data["user_id"]
    )

    await message.answer("✅ Данные сохранены! Бот начнет мониторинг в указанное время.")
    asyncio.create_task(monitoring(user_id=user_data["user_id"], bot=message.bot, time_end=time_end))

    await state.clear()
