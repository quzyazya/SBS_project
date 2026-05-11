from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.routers import auth, tasks, pages, payments
from celery_app import celery_app
from celery.schedules import crontab
import app.tasks

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
app.include_router(payments.router)

# Настройка периодических задач
celery_app.conf.beat_schedule = {
    'check-vip-expiry': {
        'task': 'app.tasks.check_and_downgrade_expired_vips',
        'schedule': crontab(minute=0, hour='*/1')   # каждый час
    },
    'cleanup-2fa-codes': {
        'task': 'app.tasks.cleanup_expired_2fa_codes',
        'schedule': crontab(minute='*/30'),         # каждые 30 минут
    }
}

# Запуск
if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', reload = True)


