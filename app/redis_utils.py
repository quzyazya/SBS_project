import redis
import os
from typing import Optional

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
redis_client = redis.from_url(REDIS_URL)

# Общие функции для кодов 

def store_code(key_prefix: str, user_id: int, code: str, expires_seconds: int = 300) -> None:
    # Сохраняет код подтверждения в Redis с указанным префиксом и времиенем жизни
    redis_client.setex(f'{key_prefix}:{user_id}', expires_seconds, code)

def verify_code(key_prefix: str, user_id: int, code: str) -> bool:
    # Проверяет код, удаляет его после проверки
    stored = redis_client.get(f'{key_prefix}:{user_id}')
    if stored and stored.decode('utf-8') == code:
        redis_client.delete(f'{key_prefix}:{user_id}')
        return True
    return False

def delete_code(key_prefix: str, user_id: int) -> None:
    # Удаляет код из Redis
    redis_client.delete(f'{key_prefix}:{user_id}')


# 2FA коды (для входа)

def store_2fa_code(user_id: int, code: str, expires_seconds: int = 300) -> None:
    # Сохраняет 2FA для входа
    store_code('2fa', user_id, code, expires_seconds)

def verify_2fa_code(user_id: int, code: str) -> bool:
    # Проверяет 2FA код для входа
    return verify_code('2fa', user_id, code)

# Коды подтверждения (для включения 2FA)

def store_verification_code(user_id: int, code: str, expires_seconds: int = 300) -> None:
    # Сохраняет код подтверждения для включения 2FA
    store_code('verify', user_id, code, expires_seconds)

def verify_verification_code(user_id: int, code: str) -> bool:
    # Проверяет код подтверждения для включения 2FA
    return verify_code('verify', user_id, code)

# Кэш ролей пользователей

def get_user_role_from_cache(user_id: int) -> Optional[str]:
    # Получает роль пользователя из кэша Redis
    role = redis_client.hget(f'user:{user_id}', 'role')
    if role:
        return role.decode('utf-8')
    return None

def set_user_role_cache(user_id: int, role: str) -> None:
    # Сохраняет роль пользователя в Redis кэш на 1 час
    redis_client.hset(f'user:{user_id}', 'role', role)
    redis_client.expire(f'user:{user_id}', 3600)

# Очистка просроченных кодов

def cleanup_expired_codes(pattern: str = '2fa:*') -> int:
    # Очищает просроченные коды из Redis
    cleaned = 0 
    for key in redis_client.scan_iter(match=pattern):
        if redis_client.ttl(key) <= 0:
            redis_client.delete(key)
            cleaned += 1
    return cleaned

# Коды подтверждения телефона

def store_phone_verification_code(phone: str, code: str, expires_seconds: int = 300) -> None:
    # Сохраняет код подтверждения телефона
    redis_client.setex(f'phone_verify:{phone}', expires_seconds, code)

def verify_phone_code(phone: str, code: str) -> bool:
    # Проверяет код подтверждения телефона
    stored = redis_client.get(f'phone_verify:{phone}')
    if stored and stored.decode('utf-8') == code:
        redis_client.delete(f'phone_verify:{phone}')
        return True
    return False