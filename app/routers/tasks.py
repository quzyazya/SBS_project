from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import asc
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db, add_and_refresh, commit_and_refresh
from app.models import User, Task, CheckPoint
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


class CheckpointCreate(BaseModel):
    title: str


class CheckpointResponse(BaseModel):
    id: int
    title: str
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


def get_checkpoint_or_404(db: Session, checkpoint_id: int, user_id: int) -> CheckPoint:
    checkpoint = db.query(CheckPoint).join(Task).filter(
        CheckPoint.id == checkpoint_id,
        Task.owner_id == user_id
    ).first()
    if not checkpoint:
        raise HTTPException(status_code=404, detail='Чекпоинт не найден')
    return checkpoint


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


@router.get('/tasks/{task_id}/checkpoints', response_model=List[CheckpointResponse])
def api_get_checkpoints(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = get_task_or_404(db, task_id, current_user.id)
    return task.checkpoints


@router.post('/tasks/{task_id}/checkpoints', response_model=CheckpointResponse)
def api_create_checkpoint(task_id: int, checkpoint: CheckpointCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = get_task_or_404(db, task_id, current_user.id)
    new_checkpoint = CheckPoint(title=checkpoint.title, task_id=task.id)
    return add_and_refresh(db, new_checkpoint)


@router.patch('/checkpoints/{checkpoint_id}/done')
def api_checkpoint_done(checkpoint_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    checkpoint = get_checkpoint_or_404(db, checkpoint_id, current_user.id)
    checkpoint.is_done = True
    db.commit()
    checkpoint.task.update_status_from_checkpoints(db)
    return {'message': f'Чекпоинт {checkpoint_id} отмечен как выполненный'}


@router.patch('/checkpoints/{checkpoint_id}/undo')
def api_checkpoint_undo(checkpoint_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    checkpoint = get_checkpoint_or_404(db, checkpoint_id, current_user.id)
    checkpoint.is_done = False
    db.commit()
    checkpoint.task.update_status_from_checkpoints(db)
    return {'message': f'Чекпоинт {checkpoint_id} отмечен как невыполненный'}


@router.delete('/checkpoints/{checkpoint_id}')
def api_delete_checkpoint(checkpoint_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    checkpoint = get_checkpoint_or_404(db, checkpoint_id, current_user.id)
    task = checkpoint.task
    db.delete(checkpoint)
    db.commit()
    task.update_status_from_checkpoints(db)
    return {'message': f'Чекпоинт {checkpoint_id} удален'}


# ========== HTML ФОРМЫ ==========

@router.post("/tasks-form")
def create_task_frontend(
    title: str = Form(...),
    content: str = Form(None),
    deadline: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    request: Request = None
):
    user = get_user_from_token(db, request)
    if not user:
        return RedirectResponse(url="/auth/login-page", status_code=303)
    
    deadline_dt = None
    if deadline:
        deadline_dt = datetime.strptime(deadline, '%Y-%m-%d')
    
    new_task = Task(
        title=title,
        content=content,
        deadline=deadline_dt,
        is_done=False,
        owner_id=user.id
    )
    add_and_refresh(db, new_task)
    return RedirectResponse(url="/", status_code=303)


@router.post("/tasks/{task_id}/done-form")
def mark_done_frontend(task_id: int, db: Session = Depends(get_db), request: Request = None):
    user = get_user_from_token(db, request)
    if not user:
        return RedirectResponse(url="/auth/login-page", status_code=303)
    task = get_task_or_404(db, task_id, user.id)
    task.is_done = True

    for cp in task.checkpoints:
        cp.is_done = True
        
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@router.post("/tasks/{task_id}/undo-form")
def undo_task_frontend(task_id: int, db: Session = Depends(get_db), request: Request = None):
    user = get_user_from_token(db, request)
    if not user:
        return RedirectResponse(url="/auth/login-page", status_code=303)
    task = get_task_or_404(db, task_id, user.id)
    task.is_done = False
    for cp in task.checkpoints:
        cp.is_done = False
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


@router.post('/tasks/{task_id}/checkpoints-form')
def create_checkpoint_form(
    task_id: int, 
    title: str = Form(...), 
    db: Session = Depends(get_db), 
    request: Request = None
):
    user = get_user_from_token(db, request)
    if not user:
        return RedirectResponse(url='/auth/login-page', status_code=303)
    
    task = get_task_or_404(db, task_id, user.id)
    new_checkpoint = CheckPoint(title=title, task_id=task.id)
    add_and_refresh(db, new_checkpoint)
    return RedirectResponse(url='/', status_code=303)


@router.post('/checkpoints/{checkpoint_id}/done-form')
def checkpoint_done_form(
    checkpoint_id: int, 
    db: Session = Depends(get_db), 
    request: Request = None
):
    user = get_user_from_token(db, request)
    if not user:
        return RedirectResponse(url='/auth/login-page', status_code=303)
    
    checkpoint = get_checkpoint_or_404(db, checkpoint_id, user.id)
    checkpoint.is_done = True
    db.commit()
    checkpoint.task.update_status_from_checkpoints(db)
    return RedirectResponse(url='/', status_code=303)


@router.post('/checkpoints/{checkpoint_id}/undo-form')
def checkpoint_undo_form(
    checkpoint_id: int, 
    db: Session = Depends(get_db), 
    request: Request = None
):
    user = get_user_from_token(db, request)
    if not user:
        return RedirectResponse(url='/auth/login-page', status_code=303)

    checkpoint = get_checkpoint_or_404(db, checkpoint_id, user.id)
    checkpoint.is_done = False
    db.commit()
    checkpoint.task.update_status_from_checkpoints(db)
    return RedirectResponse(url='/', status_code=303)


@router.post('/checkpoints/{checkpoint_id}/delete-form')
def checkpoint_delete_form(
    checkpoint_id: int, 
    db: Session = Depends(get_db), 
    request: Request = None
):
    user = get_user_from_token(db, request)
    if not user:
        return RedirectResponse(url='/auth/login-page', status_code=303)
    
    checkpoint = get_checkpoint_or_404(db, checkpoint_id, user.id)
    task = checkpoint.task
    db.delete(checkpoint)
    db.commit()
    task.update_status_from_checkpoints(db)
    return RedirectResponse(url='/', status_code=303)


# ========== СТАТИСТИКА ==========

@router.get('/stats')
def api_get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tasks = db.query(Task).filter(Task.owner_id == current_user.id).all()

    total_checkpoints = 0
    done_checkpoints = 0

    for task in tasks:
        total_checkpoints += len(task.checkpoints)
        done_checkpoints += sum(1 for cp in task.checkpoints if cp.is_done)

    percent = (done_checkpoints / total_checkpoints * 100) if total_checkpoints > 0 else 0

    return {
        'total_tasks': len(tasks),
        'total_checkpoints': total_checkpoints,
        'done_checkpoints': done_checkpoints,
        'percent': round(percent, 1)
    }