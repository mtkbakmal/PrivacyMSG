import uvicorn
import asyncio
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app.db.db import login_user, add_new_user, init_db

from app.models.baseModels import RegisterSchema, LoginSchema # * Перенёс все схемы/модели в отдельный каталог

common_responses = {
    400: {"description": "Ошибка при регистрации"},
    401: {"description": "Пользователь не авторизован"},
    500: {"description": "Внутренняя ошибка сервера"},
}

app = FastAPI(
    title="PrivacyMSG API",
    version="1.0.0",
    responses=common_responses
)
# Подключение статических файлов (CSS, JS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
# Подключение html
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "Главная"}
    )

@app.post("/register")
async def register(data: RegisterSchema):
    # немного адаптируем логику вызова
    try:
        user = await add_new_user(
                username=data.username,
                email=data.email,
                password=data.password,
                description=data.description
            )
        if user is None:
            raise HTTPException(status_code=409, detail="Пользователь с таким username или email уже зарегестрирован")
        return {"status": "ok", "message": "Пользователь создан"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Возникли проблемы во время регитрации")

@app.post("/login")
async def login(data: LoginSchema):
    # Вызываем функцию из db.py
    success = await login_user(username=data.username, password=data.password)

    if not success:
        # Если пароль неверный или пользователя нет кидаем 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль"
        )

    return {"status": "ok", "message": "Успешная авторизация"}

async def main():
    await init_db()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
    asyncio.run(main())