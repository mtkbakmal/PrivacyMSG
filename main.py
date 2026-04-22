import uvicorn
from fastapi import FastAPI, Request, HTTPException, status, Response, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from authx import AuthX, AuthXConfig # Библиотека для JWT tokens
from authx.exceptions import MissingTokenError as ThereIsNoAccessError # Получение ошибки отсутсвия токена доступа
from contextlib import asynccontextmanager

from app.db.db import login_user, add_new_user, init_db, get_users_list, delete_user_from_db
from app.config.config import settings as cfg
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    print("Shutting down...")

app = FastAPI(
    title="PrivacyMSG API",
    version="1.0.0",
    responses=common_responses,
    lifespan=lifespan
)

JWT_config = AuthXConfig()
JWT_config.JWT_SECRET_KEY = cfg.get_jwt_key # JWT код
JWT_config.JWT_ACCESS_COOKIE_NAME = "access_token" # Название токенов куки
# ! ПОКА ЧТО БУДЕМ ХРАНИТЬ В КУКАХ, ПОТОМ НАДО ПЕРЕХОДИТЬ НА СЕССИИ ИЛИ ЗАГОЛОВКИ
JWT_config.JWT_TOKEN_LOCATION = ["cookies"] # Указываем что токены будут находиться в куках

security = AuthX(config=JWT_config)

# TODO: Нужно добавить проверку наличия токена на хэндлер чата

# Подключение статических файлов (CSS, JS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Подключение html
templates = Jinja2Templates(directory="app/templates")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Здесь мы берем первую ошибку из списка и превращаем её в строку
    err_msg = exc.errors()[0].get("msg")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"status": "error", "detail": f"Ошибка валидации: {err_msg}"},
    )

@app.exception_handler(ThereIsNoAccessError)
async def theres_no_access_exception_handler(request: Request, exc: ThereIsNoAccessError):
    # Перенаправляем на страницу для входа в учетную запись
    return RedirectResponse(url="/auth")

@app.get("/admin", response_class=HTMLResponse)
async def admin_handler(request: Request):
    users = await get_users_list()
    return templates.TemplateResponse(
        request=request,
        name="admin.html", 
        context={"request": request, "users": users}
    )

@app.post("/users/delete/{user_id}")
async def delete_user(user_id: int):
    await delete_user_from_db(user_id)
    return RedirectResponse(url="/admin")

@app.get("/", response_class=HTMLResponse, dependencies=[Depends(security.access_token_required)])
@app.get("/chat", response_class=HTMLResponse, dependencies=[Depends(security.access_token_required)])
async def chat_handler(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="chat.html",
        context={"title": "Главная"}
    )

@app.get("/auth", response_class=HTMLResponse)
async def auth_panel_handler(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth.html",
        context={"title": "Главная"}
    )

@app.post("/register")
async def register_handler(data: RegisterSchema):
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
async def login_handler(data: LoginSchema, response: Response):
    # Вызываем функцию из db.py
    success = await login_user(username=data.username, password=data.password)

    if not success:
        # Если пароль неверный или пользователя нет кидаем 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль"
        )
    
    # Выдача токена при успешной аутентификации
    token = security.create_access_token(uid=data.username) # ! Нельзя передавать пароли и т.д.
    response.set_cookie(JWT_config.JWT_ACCESS_COOKIE_NAME, token)

    return {"status": "ok", "message": "Успешная авторизация", "access_token": token}

@app.post("/logout")
async def logout_handler(response: Response):
    response.delete_cookie(JWT_config.JWT_ACCESS_COOKIE_NAME)
    return {"status": "ok", "message": "Вы вышли из системы"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)