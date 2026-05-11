from celery import Celery
import os

# URL для подключения к Redis
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Создаем приложение Celery
celery_app = Celery(
    'sbs_tasks',
    broker=REDIS_URL,       # Redis как брокер сообщений
    backend=REDIS_URL,      # Redis для хранения результатов
    include=['app.tasks']   # Где искать задачи
)

# Настройки
celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,        # 30 минут
    task_soft_time_limit=25 * 60,   # 25 минут
)