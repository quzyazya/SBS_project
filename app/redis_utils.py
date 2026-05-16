import redis
import os
from typing import Optional

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
redis_client = redis.from_url(REDIS_URL)


# ========== ОБЩИЕ ФУНКЦИИ ДЛЯ КОДОВ (string) ==========

def store_code(key_prefix: str, identifier: str, code: str, expires_seconds: int = 300) -> None:
    """Сохраняет код подтверждения в Redis"""
    redis_client.setex(f'{key_prefix}:{identifier}', expires_seconds, code)


def verify_code(key_prefix: str, identifier: str, code: str) -> bool:
    """Проверяет код, удаляет его после проверки"""
    stored = redis_client.get(f'{key_prefix}:{identifier}')
    if stored and stored.decode('utf-8') == code:
        redis_client.delete(f'{key_prefix}:{identifier}')
        return True
    return False


def delete_code(key_prefix: str, identifier: str) -> None:
    """Удаляет код из Redis"""
    redis_client.delete(f'{key_prefix}:{identifier}')


# ========== 2FA КОДЫ (для входа) ==========

def store_2fa_code(user_id: int, code: str, expires_seconds: int = 300) -> None:
    """Сохраняет 2FA код для входа"""
    store_code('2fa', str(user_id), code, expires_seconds)


def verify_2fa_code(user_id: int, code: str) -> bool:
    """Проверяет 2FA код для входа"""
    return verify_code('2fa', str(user_id), code)


# ========== КОДЫ ПОДТВЕРЖДЕНИЯ (для включения 2FA) ==========

def store_verification_code(user_id: int, code: str, expires_seconds: int = 300) -> None:
    """Сохраняет код подтверждения для включения 2FA"""
    store_code('verify', str(user_id), code, expires_seconds)


def verify_verification_code(user_id: int, code: str) -> bool:
    """Проверяет код подтверждения для включения 2FA"""
    return verify_code('verify', str(user_id), code)


# ========== КОДЫ ПОДТВЕРЖДЕНИЯ ТЕЛЕФОНА ==========

def store_phone_verification_code(phone: str, code: str, expires_seconds: int = 300) -> None:
    """Сохраняет код подтверждения телефона"""
    store_code('phone_verify', phone, code, expires_seconds)


def verify_phone_code(phone: str, code: str) -> bool:
    """Проверяет код подтверждения телефона"""
    return verify_code('phone_verify', phone, code)


# ========== КЭШ РОЛЕЙ ПОЛЬЗОВАТЕЛЕЙ ==========

def get_user_role_from_cache(user_id: int) -> Optional[str]:
    """Получает роль пользователя из кэша Redis"""
    role = redis_client.get(f'user_role:{user_id}')
    if role:
        return role.decode('utf-8')
    return None


def set_user_role_cache(user_id: int, role: str) -> None:
    """Сохраняет роль пользователя в Redis кэш на 1 час"""
    redis_client.setex(f'user_role:{user_id}', 3600, role)


def delete_user_role_cache(user_id: int) -> None:
    """Удаляет кэш роли пользователя"""
    redis_client.delete(f'user_role:{user_id}')


# ========== ОЧИСТКА ПРОСРОЧЕННЫХ КОДОВ ==========

def cleanup_expired_codes(pattern: str = '2fa:*') -> int:
    """Очищает просроченные коды из Redis"""
    cleaned = 0
    for key in redis_client.scan_iter(match=pattern):
        if redis_client.ttl(key) <= 0:
            redis_client.delete(key)
            cleaned += 1
    return cleaned