from passlib.context import CryptContext #* passlib делает даже одинаковые пароли разными в хэшированном виде

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") #*Криптография крч

def hash_password(password: str) -> str:
    #!Хеширует пароль
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    #!Проверяет тот же пароль или нет
    return pwd_context.verify(plain_password, hashed_password)