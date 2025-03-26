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
    channels = message.text.strip().split("\n")
    valid_channels = []

    #регулярка для каналов
    for link in channels:
        if re.match(r"^https?://t\.me/(?:[a-zA-Z0-9_]{5,32}|\+[a-zA-Z0-9_-]+|c/\d+/[0-9]+|[a-zA-Z0-9_]{5,32}/[0-9]+)$", link.strip()):
            valid_channels.append(link.strip())
        else:
            await message.answer(f"⚠️ Некорректная ссылка: {link}. Ожидается формат https://t.me/название_канала")

    if not valid_channels:
        await message.answer("❌ Не удалось получить ни одной корректной ссылки на канал. Попробуйте снова.")
        return

    await state.update_data(channels=valid_channels)
    await message.answer("Теперь отправьте полный текст поста.")
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
