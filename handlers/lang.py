from aiogram import Router, types
from aiogram.filters import Command
from db.database import Session, User

router = Router()


@router.message(Command("english", "german"))
async def set_language(message: types.Message):
    lang = "english" if message.text == "/english" else "german"

    with Session() as session:
        user = session.query(User).filter_by(chat_id=message.chat.id).first()
        if not user:
            user = User(chat_id=message.chat.id, language=lang)
            session.add(user)
        else:
            user.language = lang
        session.commit()

    await message.answer(f"🌍 Язык установлен: {lang.capitalize()}!")