# database.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, timedelta

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    language = Column(String, default="english")
    current_word_id = Column(Integer, nullable=True)  # Новое поле
    words = relationship("Word", back_populates="user")

class Word(Base):
    __tablename__ = "words"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    word = Column(String)       # Слово на иностранном языке
    translation = Column(String) # Перевод
    definition = Column(String)  # Новое поле: определение
    example = Column(String)  # Пример использования
    source = Column(String)  # Источник (например, "WordsAPI")
    next_review = Column(DateTime, default=datetime.now())
    level = Column(Integer, default=0)  # Уровень прогресса (0-4)
    user = relationship("User", back_populates="words")

# Подключение к SQLite
engine = create_engine("sqlite:///words.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)