from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.config import settings


# Настройки JWT / JWT configuration
SECRET_KEY = "3827i984oty5w9ep6uhtrlvo9wjf495y8u6e5o89jprtyy9eo5u68y99owt48"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Настройки хеширования (pwdlib) / Hash configuration
password_hash = PasswordHash.recommended()

# Схема авторизации / Authorization scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = 'auth/login')

# Функции для работы с паролями / Functions for working with passwords
def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Проверяет, совпадает ли пароль с хешем / Checks whether the password matches the hash
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    # Хеширует пароль
    return password_hash.hash(password)

# Функции для работы с JWT / Functions for working with JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    # Создает JWT токен / Creates JWT token
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes = 15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    # Декодирует JWT токен / Decode JWT token 
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        return payload
    except JWTError:
        return None
    
# Функции для получения пользователя / Functions for getting the user
def get_user_by_email(db: Session, email: str):
    # Находит пользователя по email / Find user by email
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    # Проверяет email и пароль / Checks email and password
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Получает текущего пользователя из токена / Checks current user from token
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = 'Could not validate credentials',
        headers = {'WWW-Authenticate': 'Bearer'}
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    email: str = payload.get('sub')
    if email is None:
        raise credentials_exception
    user = get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    return user

















