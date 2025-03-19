from aiogram import Router, F
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


router = Router()


@router.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Привет! Я бот для аналитики каналов и сбора статистики постов.")