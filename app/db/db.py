from datetime import datetime as dt
from sqlalchemy import String, func, select, delete
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.db.security import hash_password, verify_password
from app.config.config import settings as cfg

DATABASE_URL = cfg.get_db_url

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

# Функция для инициализации самой БД
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Функция добавления нового пользователя в БД
async def add_new_user(username: str, description: str | None, email: str, password: str):
    async with async_session() as session:
        # Проверка, существует ли пользователь с таким username. Если да, то возвращает ничего
        exist = await session.scalar(select(User).where(User.username==username))
        if exist: 
            return
        #! Хэшируем пароль перед сохранением
        hashed_pwd = hash_password(password)

        new_user = User(username=username, description=description, email=email, hashed_password=hashed_pwd) # ! Пароль нужно хэшировать #! Хэшировал
        session.add(new_user)
        await session.commit()

#TODO: Когда делаем авторизацию нужно доставать пользователя по username и сравнивать введенный пароль с помощью функции verify_password из security.py

# Функция удаления пользователя из БД
async def delete_user(id: int):
    async with async_session() as session:
        # Если пользователя не существует, то функция ничего не возвращает
        exist = await session.scalar(select(User).where(User.id==id))
        if not exist: 
            return
        delete_stmt = delete(User).where(User.id==id)
        await session.execute(delete_stmt)
        await session.commit()

# Функция авторизации пользователя
# * Скорей всего будет меняться в будущем, пока что рабочий по своему прототип
async def login_user(username: str, password: str) -> bool:
    async with async_session() as session:
        # Проверяет, существует ли пользователь с таким username и возвращает False если нет
        exist = await session.scalar(select(User).where(User.username==username)) 
        if not exist: 
            return False
        hashed_password = await session.scalar(select(User.hashed_password).where(User.username==username))
        # Ели совпадает хэшированный пароль из БД с полученным паролем - возвращает True, иначе - False
        if verify_password(plain_password=password, hashed_password=hashed_password):
            return True
        else: return False

# Функции для проверок, существует ли уже в базе пользователь с каким-либо username | email
async def is_there_user_with_username(username: str) -> bool:
    async with async_session() as session:
        exist = await session.scalar(select(User).where(User.username==username))
        return True if exist else False
    
async def is_there_user_with_email(email: str) -> bool:
    async with async_session() as session:
        exist = await session.scalar(select(User).where(User.email==email))
        return True if exist else False

