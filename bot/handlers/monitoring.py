from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


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