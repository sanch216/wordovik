import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.client import bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.sql.functions import user

from config import bot_token
from db.database import Session, User, Word
from handlers.base import router as base_router
from handlers.lang import router as lang_router
from handlers.words import router as words_router
from wordapis import get_random_word
scheduler = AsyncIOScheduler()

async def send_new_word(chat_id: int):
    word_data = get_random_word()  # Функция из п.1
    if not word_data:
        return

    with Session() as session:
        user = session.query(User).filter_by(chat_id=chat_id).first()
        new_word = Word(
            user_id=user.id,
            word=word_data["word"],
            definition=word_data["definition"],
            source="WordsAPI"
        )
        session.add(new_word)
        session.commit()

    await bot.send_message(
        chat_id,
        f"🎉 Новое слово!\n"
        f"*{word_data['word']}*\n"
        f"_{word_data['definition']}_"
    )

# Добавляем задачу (каждый день в 12:00)
scheduler.add_job(
    send_new_word,
    'cron',
    hour=12,
    args=(user.chat_id,)  # Для всех пользователей циклом
)
async def send_review_word(chat_id: int):
    with Session() as session:
        user = session.query(User).filter_by(chat_id=chat_id).first()
        if not user:
            return # Пользователь не найден

        word = session.querry(Word).filter(
            Word.user_id == user.id,
            Word.next_review <= datetime.now()
        ).first()

        if word:
            await bot.send_message(chat_id, f"Повтори слово: {word.word}")

            user.current_word_id = word.id
            session.commit()

async def main() -> None:
    bot = Bot(token=bot_token)
    dp = Dispatcher()

    # Подключаем роутеры
    dp.include_router(base_router)
    dp.include_router(lang_router)
    dp.include_router(words_router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот остановлен')