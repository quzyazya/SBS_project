from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Task, User
from app.auth import get_current_user

# Depends - механизм внедрения зависимостей FastAPI. Позволяет FastAPI автоматически вызывать функции и передавать их результат в эндпоинт.

def require_vip(current_user: User = Depends(get_current_user)) -> User: # функция гарантированно возвращает объект User
    # Проверяет, что пользователь VIP
    if current_user.role != 'vip':
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail='VIP access required. Upgrade your plan.'
        )
    return current_user 

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    # Проверяет, что пользователь - администратор
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Admin access required.'
        )
    return current_user

def can_create_task(current_user: User, db: Session) -> bool:
    # Обычные пользователи и VIP не ограничены в создании задач
    return True

def can_star_task(current_user: User, db: Session) -> bool:
    # Нет Depends в параметрах, потому что это вспомогательная функция, 
    # не предназначенная для прямого использования в эндпоинтах как зависимость. 
    # Ее нужно вызывать внутри других функций, передавая db и user явно.
    # Проверяет, может ли пользователь закрепить новую задачу
    if current_user.role == 'vip':
        return True  # VIP без ограничений
    
    # Обыный пользователь: максимум 3 задачи
    starred_count = db.query(Task).filter(
        Task.owner_id == current_user.id,
        Task.is_starred == True
        ).count()
    return starred_count < 3