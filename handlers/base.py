from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(Command("start"))
async def start_command(message: Message):
    await message.answer(
        "Привет! Я помогу тебе учить слова.\n"
        "Выбери язык: /english или /german"
    )