import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(
    title="PrivacyMSG API",
    version="1.0.0"
)
# Подключение статических файлов (CSS, JS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
# Подключение html
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title":"Главная"})

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.67", port=8080)