from datetime import datetime
import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, nulls_last
from app.database import get_db
from app.models import ArchivedTask, Task
from app.auth import get_current_user_from_cookie
from app.templating import render_template

router = APIRouter(tags=["Pages"])


@router.get("/")
async def home(
    request: Request,
    search: str = None,
    year: int = None,
    month: int = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return render_template("login.mako", request=request, error="Пожалуйста, войдите в систему")
    
    # Получаем все задачи для создания словаря номеров (без поиска)
    all_tasks_for_numbers = db.query(Task).filter(
        Task.owner_id == current_user.id
    ).order_by(
        desc(Task.is_starred),
        nulls_last(asc(Task.deadline))
    ).all()

    # Создаем словарь: ID задачи: порядковый номер
    task_number_map = {}
    for idx, task in enumerate(all_tasks_for_numbers, 1):
        task_number_map[task.id] = idx

    # Базовый запрос
    query = db.query(Task).filter(Task.owner_id == current_user.id)

    # Поиск по названию
    if search:
        query = query.filter(Task.title.ilike(f'%{search}%'))

    tasks_db = query.order_by(
        desc(Task.is_starred),
        nulls_last(asc(Task.deadline))
    ).all()

    # Создаем список задач с порядковыми номерами (для календаря)
    tasks_with_numbers = []
    for task in tasks_db:
        tasks_with_numbers.append({
            'id': task.id,
            'number': task_number_map.get(task.id, 0), # номер из полного списка
            'title': task.title,
            'content': task.content,
            'deadline': task.deadline,
            'deadline_color': task.deadline_color,
            'deadline_text': task.deadline_text,
            'is_done': task.is_done,
            'is_starred': task.is_starred,
            'created_at': task.created_at,
            'progress_percent': task.progress_percent,
            'checkpoints': sorted(task.checkpoints, key=lambda cp: cp.created_at)
        })

    total_checkpoints, done_checkpoints = 0, 0
    
    for task in tasks_db:
        total_checkpoints += len(task.checkpoints)
        done_checkpoints += sum(1 for cp in task.checkpoints if cp.is_done)

    # Считаем количество выполненных задач и пунктов
    total_tasks = len(tasks_db)
    done_tasks = sum(1 for task in tasks_db if task.is_done)
    active_tasks = total_tasks - done_tasks
    active_checkpoints = total_checkpoints - done_checkpoints
    # Считаем количество закрепленных задач
    starred_count = sum(1 for task in tasks_db if task.is_starred)

    # Глобальный прогресс = процент выполненных задач
    global_percent = (done_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    from datetime import datetime, timedelta
    
    overdue_tasks_count = 0

    for task in tasks_db:
        if task.deadline and not task.is_done:
            if task.deadline.date() < datetime.utcnow().date():
                overdue_tasks_count += 1

    #  КАЛЕНДАРЬ

    calendar_data, calendar_year, calendar_month = None, None, None
    can_use_calendar = False

    # Проверка доступа к календарю
    days_since_reg = (datetime.utcnow() - current_user.created_at).days

    if current_user.role == 'vip':
        can_use_calendar = True
    elif days_since_reg <= 7 and not current_user.trial_used:
        can_use_calendar = True
        if days_since_reg > 0:
            current_user.trial_used = True
            db.commit()
    
    if can_use_calendar:
        # Определяем текущий месяц для календаря
        now = datetime.utcnow()
        if year is None or month is None:
            calendar_year = now.year
            calendar_month = now.month
        else:
            calendar_year = year
            calendar_month = month

        # Данные для календаря (только для VIP)
        calendar_data = []
        for task in tasks_db:
            if task.deadline:
                days_left = (task.deadline.date() - datetime.utcnow().date()).days
                if days_left <= 0:
                    color = 'red'
                elif days_left <= 3:
                    color = 'orange'
                else:
                    color = 'green'
                
                calendar_data.append({
                    'id': task.id,
                    'number': task_number_map.get(task.id, 0),
                    'date': task.deadline.strftime('%Y-%m-%d'),
                    'color': color,
                    'is_archived': False
                })
        
        # Архивные задачи (последний месяц)
        one_month_ago = datetime.utcnow() - timedelta(days = 30)
        archived_tasks = db.query(ArchivedTask).filter(
            ArchivedTask.user_id == current_user.id,
            ArchivedTask.completed_at >= one_month_ago
        ).all()

        for task in archived_tasks:
            if task.deadline:
                calendar_data.append({
                    'id': task.original_id,
                    'number': None,  # Архивыне задачи не имеют номера в текущем списке
                    'date': task.deadline.strftime('%Y-%m-%d'),
                    'title': task.title[:20] + ' (выполнена)',
                    'color': 'secondary',
                    'is_archived': True
                })
    # Ближайший дедлайн
    '''from datetime import datetime
    nearest_deadline = None
    tasks_with_deadline = [task for task in tasks_db if task.deadline is not None]
    if tasks_with_deadline:
        nearest_task = min(tasks_with_deadline, key=lambda t: t.deadline)
        days_left = (nearest_task.deadline - datetime.utcnow()).days
        if days_left < 0:
            nearest_deadline = f"⚠️ Просрочена: {nearest_task.title[:20]}"
        elif days_left == 0:
            nearest_deadline = f"🔥 Сегодня: {nearest_task.title[:20]}"
        elif days_left == 1:
            nearest_deadline = f"📅 Завтра: {nearest_task.title[:20]}"
        else:
            nearest_deadline = f"📅 Через {days_left} дн.: {nearest_task.title[:20]}"'''

    return render_template('tasks.mako',
        request=request,
        current_user=current_user,
        tasks=tasks_with_numbers,
        task_number_map=task_number_map,
        stats={
            'total_tasks': total_tasks,
            'done_tasks': done_tasks,
            'active_tasks': active_tasks,
            'total_checkpoints': total_checkpoints,
            'done_checkpoints': done_checkpoints,
            'active_checkpoints': active_checkpoints,
            'starred_count': starred_count,
            'overdue_tasks_count': overdue_tasks_count,
            'percent': round(global_percent, 1),
            # 'nearest_deadline': nearest_deadline
        },
        search_query=search,
        calendar_year=calendar_year if can_use_calendar else datetime.utcnow().year,
        calendar_month=calendar_month if can_use_calendar else datetime.utcnow().month,
        calendar_data=calendar_data,
        can_use_calendar=can_use_calendar,
        days_left_trial=(7 - days_since_reg) if days_since_reg <= 7 else 0
    )

@router.get('/create-task')
def create_task_page(
    request: Request,
    deadline: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return render_template('login.mako', request=request, error='Пожалуйста, войдите в систему')

    today = datetime.now().date().isoformat()

    return render_template('create_task.mako', request=request, deadline=deadline, today=today)

@router.get('/upgrade-page')
def upgrade(request: Request):
    # Страница выбора VIP подписки
    return render_template('upgrade.mako', request=request)

@router.get('/profile')
def profile_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return render_template('login.mako', request=request, error='Пожалуйста, войдите в систему')
    return render_template('profile.mako', request=request, current_user=current_user)

@router.post('/profile/enable-2fa')
def enable_2fa(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return RedirectResponse(url='/auth/login-page', status_code=303)
    
    if not current_user.phone:
        return RedirectResponse(url='/profile?error=no_phone', status_code=303)
    
    current_user.is_2fa_enabled = True
    db.commit()
    
    return RedirectResponse(url='/profile?success=2fa_enabled', status_code=303)

@router.post('/profile/disable-2fa')
def disable_2fa(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return RedirectResponse(url='/auth/login-page', status_code=303)
    
    current_user.is_2fa_enabled = False
    db.commit()

    return RedirectResponse(url='/profile?success=2fa_disabled', status_code=303)