from pydantic import BaseModel

class RegisterSchema(BaseModel):
    username: str
    email: str
    password: str
    description: str = None

class LoginSchema(BaseModel):
    username: str
    password: str