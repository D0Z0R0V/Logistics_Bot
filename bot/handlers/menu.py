from aiogram import Router, F
from aiogram.filters.command import Command
from aiogram.types import Message


router = Router()


@router.message(Command("start"))
async def start_command(message: Message):
    text = (
        "👋 Привет! Я бот для мониторинга постов в Telegram-каналах.\n\n"
        "📌 <b>Я умею:</b>\n"
        " <b>-</b> Следить за появлением нужного поста в каналах\n"
        " <b>-</b> Отправлять уведомления, если пост найден\n"
        " <b>-</b> Работать в заданных временных рамках\n\n"
        "- Чтобы добавить проверку, используй команду <b>/add_check</b>\n"
        "- Если нужна помощь, введи <b>/help</b>\n\n"
        "Давай начнем! 🚀"
    )
    await message.answer(text, parse_mode="HTML")
    
    
@router.message(Command("help"))
async def help_command(message: Message):
    text = (
        "🆘 <b>Помощь по боту</b>\n\n"
        " <b>/add_check</b> – Добавить задачу на мониторинг постов\n"
        " <b>/list_checks</b> – Посмотреть текущие проверки\n"
        " <b>/delete_check</b> – Удалить проверку\n\n"
        "📌 <b>Как добавить проверку:</b>\n"
        "1️⃣ Введите команду <b>/add_check</b>\n"
        "2️⃣ Отправьте список каналов в формате 'Название (ссылка)'\n"
        "3️⃣ Отправьте текст поста, который нужно искать\n"
        "4️⃣ Укажите временной интервал (например, 08:00-10:00)\n\n"
    )
    await message.answer(text, parse_mode="HTML")
    
@router.message(Command("list_checks"))
async def help_command(message: Message):
    await message.answer("Функционал в доработке")
    
@router.message(Command("file_check"))
async def help_command(message: Message):
    await message.answer("На данный момент отчет придет Вам автоматически после всех проверок)")
    
@router.message(Command("delete_check"))
async def help_command(message: Message):
    await message.answer("Функционал в доработке")
