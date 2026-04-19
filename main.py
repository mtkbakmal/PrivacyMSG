import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

common_responses = {
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

@app.post("/login")
async def login(data: dict):
    pass

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)