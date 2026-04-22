from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.routers import auth, tasks, pages

# Создаем приложение 
app = FastAPI(
    title = settings.APP_NAME,
    description = 'Task tracker with progress bar + JWT auth',
    debug = settings.DEBUG
)

# Подключаем статистические файлы (CSS)
app.mount('/static', StaticFiles(directory = 'app/static'), name = 'static')

# Подключаем роутеры 
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(pages.router)

# Запуск
if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', reload = True)


