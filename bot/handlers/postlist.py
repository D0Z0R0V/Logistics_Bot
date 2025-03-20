from aiogram import Router, F
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from bot.database.db_utils import save_post
from monitor import monitoring
import asyncio


router = Router()

class AddCheck(StatesGroup):
    CHANNELS = State()
    POST_TEXT = State()
    TIME_RANGE = State()


@router.message(Command("add_check"))
async def get_posts(message: Message, state: FSMContext):
    await message.answer("Отправьте список каналов (каждый канал с новой строчки), где название - это ссылка на канал")
    await state.set_state(AddCheck.CHANNELS)
    
@router.message(AddCheck.CHANNELS)
async def process_channel(message: Message, state: FSMContext):
    channels = message.text.strip().split("\n")
    channel_data = []
    
    for line in channels:
        parts = line.split(" ")
        if len(parts) < 2:
            continue
        name = " ".join(parts[:-1])
        link = parts[-1]
        channel_data.append((name, link))
        
    await state.update_data(channels=channel_data)
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
        await message.answer("Некорректный формат. Введите в формате HH:MM-HH:MM.")
        return
    time_start, time_end = time_range.split("-")
    user_data = await state.get_data()
    
    await save_post(user_data["post_text"], time_start.strip(), time_end.strip(), user_data['channels'])
    await message.answer("Данные сохранены! Бот начнет мониторинг в указанное время.")
    
    asyncio.create_task(monitoring())
    
    await state.clear()
    