import types
from datetime import datetime, timedelta

from aiogram.dispatcher import router
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.database import Session, User, Word


@router.message(Command("review"))
async def start_review(message: types.Message):
    with Session() as session:
        user = session.query(User).filter_by(chat_id=message.chat.id).first()
        word = session.query(Word).filter(
            Word.user_id == user.id,
            Word.next_review <= datetime.now()
        ).first()

        if not word:
            await message.answer("🎉 Все слова повторены!")
            return

        # Создаем кнопки с вариантами
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Знаю",
            callback_data=f"know_{word.id}")
        )
        builder.add(types.InlineKeyboardButton(
            text="Не помню",
            callback_data=f"forgot_{word.id}")
        )

        await message.answer(
            f"🔍 Переведите: *{word.word}*",
            reply_markup=builder.as_markup()
        )

@router.callback_query(lambda c: c.data.startswith("know_") or c.data.startswith("forgot_"))
async def handle_review(callback: types.CallbackQuery):
    word_id = int(callback.data.split("_")[1])
    is_correct = callback.data.startswith("know_")

    with Session() as session:
        word = session.query(Word).get(word_id)
        if is_correct:
            word.level = min(word.level + 1, 4)
        else:
            word.level = max(word.level - 1, 0)

        word.next_review = datetime.now() + timedelta(days=INTERVALS[word.level])
        session.commit()

    await callback.message.edit_text(
        f"✅ Правильно! Следующее повторение через {INTERVALS[word.level]} дней."
        if is_correct else
        f"❌ Нужно повторить. Правильный ответ: {word.translation}"
    )