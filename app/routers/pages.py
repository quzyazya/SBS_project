from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Task
from app.auth import get_current_user
from app.templating import render_template

router = APIRouter(tags=["Pages"])


@router.get("/")
async def home(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tasks_db = db.query(Task).filter(Task.owner_id == current_user.id).order_by(Task.created_at.desc()).all()
    
    tasks = []
    for task in tasks_db:
        tasks.append({
            "id": task.id,
            "title": task.title,
            "is_done": task.is_done,
            "deadline": task.deadline.isoformat() if task.deadline else None,
            "created_at": task.created_at.isoformat()
        })
    
    tasks_quantity = len(tasks)
    done_tasks = sum(1 for t in tasks if t["is_done"])
    percent = (done_tasks / tasks_quantity * 100) if tasks_quantity > 0 else 0
    
    return render_template("tasks.mako", request=request, current_user=current_user, tasks=tasks, stats={
        "tasks_quantity": tasks_quantity,
        "done_tasks": done_tasks,
        "pending_tasks": tasks_quantity - done_tasks,
        "percent": round(percent, 1)
    })