from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Task
from app.auth import get_current_user_from_cookie
from app.templating import render_template

router = APIRouter(tags=["Pages"])


@router.get("/")
async def home(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return render_template("login.mako", request=request, error="Пожалуйста, войдите в систему")
    
    tasks_db = db.query(Task).filter(
        Task.owner_id == current_user.id
    ).order_by(Task.created_at.desc()).all()
    
    # ========== НОВАЯ ЛОГИКА ==========
    # Считаем количество выполненных задач
    total_tasks = len(tasks_db)
    done_tasks = sum(1 for task in tasks_db if task.is_done)
    
    # Глобальный прогресс = процент выполненных задач
    global_percent = (done_tasks / total_tasks * 100) if total_tasks > 0 else 0
    # =================================
    
    return render_template('tasks.mako',
        request=request,
        current_user=current_user,
        tasks=tasks_db,
        stats={
            'total_tasks': total_tasks,
            'total_checkpoints': total_tasks,  # можно убрать или оставить для совместимости
            'done_checkpoints': done_tasks,    # можно убрать или оставить для совместимости
            'percent': round(global_percent, 1)
        }
    )