from celery import shared_task
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import User
import logging
import redis
import redis
import json
import os

from app.redis_utils import cleanup_expired_codes

logger = logging.getLogger(__name__)
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
redis_client = redis.from_url(REDIS_URL)

@shared_task
def check_and_downgrade_expired_vip():
    # Проверяет истекших VIP пользователей и понижает их статус, запускается по расписанию (каждый час)
    with SessionLocal() as db:
        try:
            # Находим VIP с истекшей подпиской
            expired_users = db.query(User).filter(
                User.role == 'vip',
                User.subscription_expires_at < datetime.utcnow()
            ).all()

            for user in expired_users:
                # Понижаем статус
                user.role = 'user'
                user.subscription_expires_at = None
                logger.info(f"📉 User {user.email} downgraded from VIP")

                # Обновляем кэш в Redis

            db.commit()
            return {'downgraded': len(expired_users)}
        
        except Exception as e:
            db.rollback()    # откат изменений
            logger.error(f'Error: {e}')
            return {'error': str(e)}
        
@shared_task
def cleanup_expired_2fa_codes():
    # Очищает просроченные 2FA коды из Redis
    # Вместо словаря temp_2fa_codes теперь Redis с TTL
    # Коды сами истекают через 5 минут, эта задача - для страховки            

    cleaned = cleanup_expired_codes('2fa:*')
    return {'cleaned': True}

def store_2fa_code(user_id: int, code: str, expires_seconds: int = 300):
    # Сохраняет 2FA код в Redis с временем жизни
    redis_client.setex(f'2fa:{user_id}', expires_seconds, code)

def verify_2fa_code(user_id: int, code: str) -> bool:
    # Проверяет 2FA код из Redis
    stored = redis_client.get(f'2fa:{user_id}')
    if stored and stored.decode('utf-8') == code:
        redis_client.delete(f'2fa:{user_id}')
        return False

def get_user_role_from_cache(user_id: int) -> str:
    # Получает роль пользователя из кэша Redis
    role = redis_client.hget(f'user:{user_id}', 'role')
    if role:
        return role.decode('utf-8')
    return None

def set_user_role_cache(user_id: int, role: str):
    # Сохраняет роль пользователя в Redis кэш
    redis_client.hset(f'user:{user_id}', 'role', role)
    redis_client.expire(f'user:{user_id}', 3600)   # сохранять на час




