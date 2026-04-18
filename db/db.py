from datetime import datetime as dt
from sqlalchemy import String, func, select, update, delete
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from security import hash_password #*Импортирую функцию хэширования пароля из security.py

import config.config as cfg

DATABASE_URL = cfg.get_db_url()

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

# Создание таблицы для пользователей
class User(Base):
    __tablename__ = "users" # Название таблицы

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # id в БД и приложении
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False) # имя пользователя
    email: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False) #! Колонка хэшированного пароля
    description: Mapped[str] = mapped_column(String(100), unique=False, nullable=True) # Описание профиля
    created_at: Mapped[dt] = mapped_column(server_default=func.now()) # Дата создания аккаунта

#TODO: Написать функции для удаления пользователя из таблицы

# Функция добавления нового пользователя в БД
async def add_new_user(username: str, description: str | None, email: str, password: str):
    async with async_session() as session:
        exist = await session.scalar(select(User).where(User.username==username))
        if exist: # Проверка, существует ли пользователь с таким username. Если да, то возвращает ничего
            return
        #!Хэшируем пароль перед сохранением
        hashed_pwd = hash_password(password)

        new_user = User(username=username, description=description, email=email, hashed_password=hashed_pwd) # ! Пароль нужно хэшировать #! Хэшировал
        session.add(new_user)
        await session.commit()

#TODO: Когда делаем авторизацию нужно доставать пользователя по username и сравнивать введенный пароль с помощью функции verify_password из security.py

# Функция удаления пользователя из БД
async def delete_user(id: int):
    async with async_session() as session:
        exist = await session.scalar(select(User).where(User.id==id))
        if not exist: # Если пользователя не существует то функция ничего не возвращет
            return
        delete_stmt = delete(User).where(User.id==id)
        await session.execute(delete_stmt)
        await session.commit()
