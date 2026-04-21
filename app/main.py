from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import asc, func
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, EmailStr

from app.config import settings
from app.database import get_db, add_and_refresh, commit_and_refresh
from app.models import Task, User
from app.auth import (
    create_access_token, get_password_hash, authenticate_user, create_access, token,
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES, verify_password
)

# ========== PYDANTIC СХЕМЫ ==========
class TaskCreate(BaseModel):
    # Схема для создания задачи / Scheme for building a task
    title: str
    content: Optional[str] = None
    deadline: Optional[datetime] = None

class TaskResponse(BaseModel):
    # Схема для ответа с задачей / Scheme for answer with a task
    id: int
    title: str
    content: Optional[str]
    deadline: Optional[datetime]
    is_done: bool
    created_at: datetime

    class Config:
        from_attributes = True 

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    created_At: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token = set
    token_type: str

# ========== СОЗДАНИЕ ПРИЛОЖЕНИЯ ==========
app = FastAPI(
    title=settings.APP_NAME,
    description="Task tracker with progress bar",
    debug=settings.DEBUG
)

# # Создание таблиц при старте
# @app.on_event("startup")
# def startup():
#     Base.metadata.create_all(bind=engine)


# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ЭНДПОИНТОВ ==========  /   Auxiliary functions for endpoints 

def get_task_or_404(db: Session, task_id: int, user_id: int) -> Task:
    # Находим задачу по ID и проверяет, принадлежит ли она пользователю
    # Если не найдена - возвращаем ошибку 404
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == user_id
    ).first()
    if not task:
        raise HTTPException(status_code = 404, detail = 'Task not found')
    return task

def get_user_by_email_or_404(db: Session, email: str) -> User:
    # Находим пользователя по email -> Если не найден - возвращаем 404
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = 'Incorrect email or password',
            headers = {'WWW-Authenticate': 'Bearer'}
        )
    return user

# ========== ЭНДПОИНТЫ АВТОРИЗАЦИИ ==========    /  Authorization endpoints

@app.post('/auth/register', response_model = UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Регистрация нового пользователя
    # - email: адрес электронной почты (должен быть уникальным)
    # - password: пароль (будет сохранен в хешированном виде)
    # Проверяем, не существуют ли пользователи с таким email
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = 'Email already registered'
        )
    # Создаем и сохраняем нового пользователя
    
    new_user = User(
        email = user_data.email,
        hashed_password = get_password_hash(user_data.password)
    )
    # Старый вариант:
    # db.add(new_user)
    # db.commit()
    # db.refresh(new_user)
    # return new_user

    return add_and_refresh(db, new_user)

@app.post('/auth/login', response_model = Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Логин возвращает JWT токен
    # Находим пользователя
    user = get_user_by_email_or_404(db, form_data.username)

    # Проверяем пароль
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            stasus_code = status.HTTP_401_UNAUTHORIZED,
            detail = 'Incorrect email or password',
            headers = {'WWW-Authenticate': 'Beare'}
        )
    
    # Создаем и возвращаем токен
    access_token_expires = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data = {'sub': user.email}, expires_delta = access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}

@app.get('/auth/me', response_model = UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    # Получить информацию о текущем пользователе
    return current_user

# ========== ЭНДПОИНТЫ ========== /  endpoints

@app.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Создаем новую задачу
    new_task = Task(
        title = task.title,
        content = task.content,
        deadline = task.deadline,
        is_done = False,
        owner_id = current_user.id
    )
    
    return add_and_refresh(db, new_task)

@app.get("/tasks", response_model=List[TaskResponse])
def get_all_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Получить все задачи текущего пользователя 
    tasks = db.query(Task).filter(Task.owner_id == current_user.id).order_by(Task.created_at.desc()).all()
    return tasks

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Получить задачу по ID
    return get_task_or_404(db, task_id, current_user.id)

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Обновить задачу
    task = get_task_or_404(db, task_id, current_user.id)
    
    task.title = task_update.title
    task.content = task_update.content
    task.deadline = task_update.deadline
    
    return commit_and_refresh(db, task)

@app.patch("/tasks/{task_id}/done")
def mark_done(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Отметить задачу выполненной
    task = get_task_or_404(db, task_id, current_user.id)
    
    task.is_done = True
    db.commit()
    return {"message": f"Task {task_id} marked as done"}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Удалить задачу
    task = get_task_or_404(db, task_id, current_user.id)
    
    db.delete(task)
    db.commit()
    return {"message": f"Task {task_id} successfully deleted"}

@app.get("/stats")
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    # Статистика прогресса для текущего пользователя
    # Количество всех задач пользователя:
    tasks_quantity = db.query(Task).filter(Task.owner_id == current_user.id).count()

    # Количество выполненных задач:
    done_tasks = db.query(Task).filter(
        Task.owner_id == current_user.id,
        Task.is_done == True
    ).count()

    # Процент выполнения
    percent = (done_tasks / tasks_quantity * 100) if tasks_quantity > 0 else 0 

    # Задача с ближайшим дедлайном
    most_priority = db.query(Task).filter(
        Task.owner_id == current_user.id,
        Task.deadline.isnot(None)
    ).order_by(asc(Task.deadline)).first()

    return {
        'tasks_quantity': tasks_quantity,
        'done_tasks': done_tasks,
        'pending_tasks': tasks_quantity - done_tasks,
        'percent': f'{round(percent, 1)}%',
        'most_priority': most_priority
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)