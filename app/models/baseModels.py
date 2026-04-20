from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class RegisterSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr = Field(..., max_length=64)
    password: str = Field(..., min_length=8)
    description: Optional[str] = Field(None, max_length=100)

class LoginSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8)
