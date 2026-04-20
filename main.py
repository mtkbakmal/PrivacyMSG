import uvicorn
import asyncio
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.db.db import login_user, add_new_user, init_db

from app.models.baseModels import RegisterSchema, LoginSchema # * Перенёс все схемы/модели в отдельный каталог

common_responses = {
    # --- 2xx Success (Успех) ---
    200: {"description": "Запрос выполнен успешно"},
    201: {"description": "Ресурс успешно создан"},
    204: {"description": "Запрос выполнен успешно, контент отсутствует"},

    # --- 4xx Client Errors (Ошибки клиента) ---
    400: {"description": "Некорректный запрос (ошибка валидации или регистрации)"},
    401: {"description": "Пользователь не авторизован (требуется вход)"},
    403: {"description": "Доступ запрещен (недостаточно прав)"},
    404: {"description": "Ресурс не найден"},
    405: {"description": "Метод не поддерживается"},
    409: {"description": "Конфликт состояния ресурса (например, такой email уже занят)"},
    422: {"description": "Необрабатываемая сущность (ошибки бизнес-логики)"},
    429: {"description": "Слишком много запросов (превышен лимит)"},

    # --- 5xx Server Errors (Ошибки сервера) ---
    500: {"description": "Внутренняя ошибка сервера"},
    502: {"description": "Плохой шлюз (ошибка прокси или основного сервера)"},
    503: {"description": "Сервис временно недоступен (техработы)"},
    504: {"description": "Шлюз не отвечает (тайм-аут)"},
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

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Здесь мы берем первую ошибку из списка и превращаем её в строку
    err_msg = exc.errors()[0].get("msg")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"status": "error", "detail": f"Ошибка валидации: {err_msg}"},
    )

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
    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(status_code=400, detail="Возникли проблемы во время регистрации")
    
    if user is None:
        raise HTTPException(status_code=409, detail="Пользователь с таким username или email уже зарегестрирован")
    return {"status": "ok", "message": "Пользователь создан"}

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