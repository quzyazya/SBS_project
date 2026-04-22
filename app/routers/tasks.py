from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import asc
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db, add_and_refresh, commit_and_refresh
from app.models import User, Task
from app.auth import get_current_user, decode_access_token

router = APIRouter(prefix="/api", tags=["Tasks API"])


# ========== PYDANTIC СХЕМЫ ==========

class TaskCreate(BaseModel):
    title: str
    content: Optional[str] = None
    deadline: Optional[datetime] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    content: Optional[str]
    deadline: Optional[datetime]
    is_done: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

def get_task_or_404(db: Session, task_id: int, user_id: int) -> Task:
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


def get_user_from_token(db: Session, request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    return db.query(User).filter(User.email == payload.get("sub")).first()


# ========== API ЭНДПОИНТЫ (JSON) ==========

@router.post("/tasks", response_model=TaskResponse)
def api_create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_task = Task(
        title=task.title,
        content=task.content,
        deadline=task.deadline,
        is_done=False,
        owner_id=current_user.id
    )
    return add_and_refresh(db, new_task)


@router.get("/tasks", response_model=List[TaskResponse])
def api_get_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tasks = db.query(Task).filter(Task.owner_id == current_user.id).order_by(Task.created_at.desc()).all()
    return tasks


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def api_get_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_task_or_404(db, task_id, current_user.id)


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def api_update_task(task_id: int, task_update: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = get_task_or_404(db, task_id, current_user.id)
    task.title = task_update.title
    task.content = task_update.content
    task.deadline = task_update.deadline
    return commit_and_refresh(db, task)


@router.patch("/tasks/{task_id}/done")
def api_mark_done(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = get_task_or_404(db, task_id, current_user.id)
    task.is_done = True
    db.commit()
    return {"message": f"Task {task_id} marked as done"}


@router.delete("/tasks/{task_id}")
def api_delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = get_task_or_404(db, task_id, current_user.id)
    db.delete(task)
    db.commit()
    return {"message": f"Task {task_id} successfully deleted"}


@router.get("/stats")
def api_get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tasks_quantity = db.query(Task).filter(Task.owner_id == current_user.id).count()
    done_tasks = db.query(Task).filter(Task.owner_id == current_user.id, Task.is_done == True).count()
    percent = (done_tasks / tasks_quantity * 100) if tasks_quantity > 0 else 0
    most_priority = db.query(Task).filter(Task.owner_id == current_user.id, Task.deadline.isnot(None)).order_by(asc(Task.deadline)).first()
    return {
        'tasks_quantity': tasks_quantity,
        'done_tasks': done_tasks,
        'pending_tasks': tasks_quantity - done_tasks,
        'percent': round(percent, 1),
        'most_priority': most_priority
    }


# ========== HTML ФОРМЫ (для фронтенда) ==========

@router.post("/tasks-form")
def create_task_frontend(title: str = Form(...), deadline: Optional[str] = Form(None), db: Session = Depends(get_db), request: Request = None):
    user = get_user_from_token(db, request)
    if not user:
        return RedirectResponse(url="/auth/login-page", status_code=303)
    deadline_dt = datetime.fromisoformat(deadline) if deadline else None
    new_task = Task(title=title, deadline=deadline_dt, is_done=False, owner_id=user.id)
    add_and_refresh(db, new_task)
    return RedirectResponse(url="/", status_code=303)


@router.post("/tasks/{task_id}/done-form")
def mark_done_frontend(task_id: int, db: Session = Depends(get_db), request: Request = None):
    user = get_user_from_token(db, request)
    if not user:
        return RedirectResponse(url="/auth/login-page", status_code=303)
    task = get_task_or_404(db, task_id, user.id)
    task.is_done = True
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@router.post("/tasks/{task_id}/delete-form")
def delete_task_frontend(task_id: int, db: Session = Depends(get_db), request: Request = None):
    user = get_user_from_token(db, request)
    if not user:
        return RedirectResponse(url="/auth/login-page", status_code=303)
    task = get_task_or_404(db, task_id, user.id)
    db.delete(task)
    db.commit()
    return RedirectResponse(url="/", status_code=303)