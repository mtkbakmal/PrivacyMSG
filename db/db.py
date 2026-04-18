from datetime import datetime as dt
from sqlalchemy import String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# ? DATABASE_URL = {URL базы данных (лучше импортировать с переменных окружения)}

# ? engine = create_async_engine(DATABASE_URL, echo=True)
# ? async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

# Создание таблицы для пользователей
class User(Base):
    __tablename__ = "users" # Название таблицы

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # id в БД и приложении
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False) # имя пользователя
    description: Mapped[str] = mapped_column(String(100), unique=False, nullable=True) # Описание профиля
    created_at: Mapped[dt] = mapped_column(server_default=func.now()) # Дата создания аккаунта

#TODO: Нужно создать также таблицы для чатов и сообщений
#TODO: Написать функции для добавления/удаления пользователя в/из таблиц(у/ы)
