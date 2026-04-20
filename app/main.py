from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import asc, func
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from app.config import settings
from app.database import get_db, engine, Base
from app.models import Task

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

# ========== ЭНДПОИНТЫ ==========

@app.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = Task(
        title=task.title,
        content=task.content,
        deadline=task.deadline,
        is_done=False
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.get("/tasks", response_model=List[TaskResponse])
def get_all_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).order_by(Task.created_at.desc()).all()
    return tasks

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskCreate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.title = task_update.title
    task.content = task_update.content
    task.deadline = task_update.deadline
    
    db.commit()
    db.refresh(task)
    return task

@app.patch("/tasks/{task_id}/done")
def mark_done(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.is_done = True
    db.commit()
    return {"message": f"Task {task_id} marked as done"}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"message": f"Task {task_id} successfully deleted"}

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    tasks_quantity = db.query(Task).count()
    done_tasks = db.query(Task).filter(Task.is_done == True).count()
    percent = (done_tasks / tasks_quantity * 100) if tasks_quantity > 0 else 0
    
    most_priority = db.query(Task).filter(Task.deadline.isnot(None)).order_by(asc(Task.deadline)).first()
    
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