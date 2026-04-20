import bcrypt

def hash_password(password: str) -> str:
    # Превращаем строку в байты
    pwd_bytes = password.encode('utf-8')
    # Генерируем соль и хешируем
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    # Возвращаем как строку для базы данных
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Сравниваем пришедший пароль с хешем из БД
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )