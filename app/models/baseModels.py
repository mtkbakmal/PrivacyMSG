from datetime import datetime as dt
from sqlalchemy import String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal

# * --DATABASE--

class Base(DeclarativeBase):
    pass

# Создание таблицы для пользователей
class User(Base):
    __tablename__ = "users" # Название таблицы

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # id в БД и приложении
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False) # имя пользователя
    email: Mapped[str] = mapped_column(String(64), unique=True, nullable=False) # Email пользователя
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False) # Колонка хэшированного пароля
    description: Mapped[str] = mapped_column(String(100), unique=False, nullable=True) # Описание профиля
    created_at: Mapped[dt] = mapped_column(server_default=func.now()) # Дата создания аккаунта

# * --SCHEMAS--

class RegisterSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr = Field(..., max_length=64)
    password: str = Field(..., min_length=8)
    description: Optional[str] = Field(None, max_length=100)

class LoginSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8)

class MessageSchema(BaseModel):
    from_user: str
    to_user: str
    send_data: dt = dt.now()
    type: Literal["txt", "img", "vid"]
