from aiogram import Router, types
from aiogram.filters import Command
from datetime import datetime, timedelta

from config import INTERVALS
from db.database import Session, User, Word
import logging

router = Router()

from datetime import datetime, timedelta
from aiogram import Router, types
from aiogram.filters import Command
from db.database import Session, User, Word
from config import INTERVALS  # <-- Импортируем интервалы

router = Router()

@router.message(Command("add"))
async def add_word(message: types.Message):
    try:
        args = message.text.split(" ", 1)
        if len(args) < 2:
            raise ValueError("Не указаны аргументы")

        word_part = args[1].split(";", 1)
        word = word_part[0].strip()
        translation = word_part[1].strip() if len(word_part) > 1 else ""

        if not translation:
            raise ValueError("Нет перевода")

        with Session() as session:
            user = session.query(User).filter_by(chat_id=message.chat.id).first()
            if not user:
                await message.answer("❌ Сначала выберите язык (/english или /german)")
                return

            new_word = Word(
                user_id=user.id,
                word=word,
                translation=translation,
                next_review=datetime.now() + timedelta(days=INTERVALS[0])  # <-- Используем INTERVALS
            )
            session.add(new_word)
            session.commit()

        await message.answer(f"✅ Добавлено: {word} - {translation}")

    except ValueError as ve:
        await message.answer(f"❌ Ошибка: {ve}\nФормат: /add слово;перевод")
    except Exception as e:
        await message.answer("❌ Произошла внутренняя ошибка")

@router.message()
async def check_translation(message: types.Message):
    with Session() as session:
        user = session.query(User).filter_by(chat_id=message.chat.id).first()
        word = session.query(Word).filter(
            Word.user_id == user.id,
            Word.next_review <= datetime.now()
        ).first()

        if not word:
            return

        if message.text.lower() == word.translation.lower():
            word.level = min(word.level + 1, 4)
            await message.answer(f"✅ Правильно! Следующее повторение через {INTERVALS[word.level]} дней.")
        else:
            word.level = max(word.level - 1, 0)
            await message.answer(f"❌ Неправильно. Правильный ответ: {word.translation}")

        # Обновляем дату следующего повторения
        word.next_review = datetime.now() + timedelta(days=INTERVALS[word.level])  # <-- Используем INTERVALS
        session.commit()


@router.message(Command("mywords"))
async def show_words(message: types.Message):
    with Session() as session:
        user = session.query(User).filter_by(chat_id=message.chat.id).first()
        if not user:
            await message.answer("❌ Сначала выберите язык.")
            return

        words = session.query(Word).filter_by(user_id=user.id).all()
        if not words:
            await message.answer("📝 Список слов пуст.")
            return

        response = "📚 Ваши слова:\n\n"
        for word in words:
            response += f"• {word.word} — {word.translation}\n"
            if word.definition:
                response += f"  📖 {word.definition}\n"
            if word.example:
                response += f"  ✍️ Пример: {word.example}\n"
            response += "\n"

        await message.answer(response)