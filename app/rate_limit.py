from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request, HTTPException
import redis
import os

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Настройка лимитера с использованием Redis
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=REDIS_URL,
    strategy='fixed-window',
    default_limits=['100/minute']
)

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return HTTPException(
        status_code=429,
        detail=f'Слишком много запросов. Попробуйте позже.'
    )