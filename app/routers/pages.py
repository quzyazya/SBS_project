from datetime import datetime, timedelta
import json
import uuid
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, nulls_last, text
from app.database import get_db
from app.email_utils import send_password_changed_email, send_verification_email
from app.models import ArchivedTask, Task, User
from app.quotes import get_quote_of_the_day
from app.auth import get_current_user_from_cookie, get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES  # ← добавить сюда
from app.redis_utils import (
    store_verification_code, verify_verification_code, 
    get_user_role_from_cache, set_user_role_cache, delete_user_role_cache,
    store_phone_verification_code, verify_phone_code
)
from app.templating import render_template
from app.redis_utils import redis_client
import random
from app.sms_utils import send_verification_code
from app.rate_limit import limiter

router = APIRouter(tags=["Pages"])

# Временное хранилище для кодов подтверждения (с Redis)



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
    
    # Получаем цитату дня
    quote = get_quote_of_the_day()

    cached_role = get_user_role_from_cache(current_user.id)
    if cached_role:
        user_role = cached_role
    else:
        user_role = current_user.role
        set_user_role_cache(current_user.id, user_role)

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
    
    overdue_tasks_count = 0

    for task in tasks_db:
        if task.deadline and not task.is_done:
            if task.deadline.date() < datetime.utcnow().date():
                overdue_tasks_count += 1

    #  КАЛЕНДАРЬ

    calendar_data = []
    calendar_year = datetime.utcnow().year
    calendar_month = datetime.utcnow().month
    can_use_calendar = False

    # Проверка доступа к календарю
    days_since_reg = (datetime.utcnow() - current_user.created_at).days

    if current_user.role == 'vip':
        can_use_calendar = True
    
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
        days_left_trial=(7 - days_since_reg) if days_since_reg <= 7 else 0,
        quote=quote
    )

@router.get('/welcome')
def welcome_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return RedirectResponse(url='/auth/login-page', status_code=303)
    
    return render_template('welcome_page.mako', request=request)

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
def upgrade(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return RedirectResponse(url='/auth/login-page')

    # Страница выбора VIP подписки
    return render_template('upgrade.mako', request=request, current_user=current_user)

@router.post('/activate-trial-vip')
def activate_trial_vip(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return RedirectResponse(url='/auth/login-page', status_code=303)
    
    # Обновляем роль до VIP
    current_user.role = 'vip'
    db.commit()

    # Обновляем кэш в Redis 
    set_user_role_cache(current_user.id, 'vip')     

    # Создаем новый токен с обновленной ролью
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={'sub': current_user.email}, expires_delta=access_token_expires
    )

    # Перенаправляем с новым токеном
    response = RedirectResponse(url='/profile?success=vip_activated', status_code=303)
    response.set_cookie(key='access_token', value=new_access_token, httponly=True)

    return response

@router.get('/vip-success')
def vip_success(request:Request):
    return render_template('vip_success.mako', request=request)

@router.get('/profile')
def profile_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return render_template('login.mako', request=request, error='Пожалуйста, войдите в систему')
    return render_template('profile.mako', request=request, current_user=current_user)

@router.post('/profile/change-username')
@limiter.limit('5/hour')
def change_username(
    request: Request,
    new_username: str = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie),
):
    if not current_user:
        return RedirectResponse(url='/auth/login-page', status_code=303)
    
    # VIP могут менять никнейм неограниченное количество раз
    if current_user.role != 'vip':
        if current_user.nickname_changed:
            return RedirectResponse(url='/profile?error=nickname_already_changed', status_code=303)
    
    # Проверка: никнейм не занят
    existing = db.query(User).filter(User.username == new_username).first()
    if existing and existing.id != current_user.id:
        return RedirectResponse(url='/profile?error=nickname_taken', status_code=303)
    
    # Меняем никнейм
    current_user.username = new_username

    # Отмечаем, что никнейм менялся (только для Free)
    if current_user.role != 'vip':
        current_user.nickname_changed = True
    
    db.commit()
    set_user_role_cache(current_user.id, current_user.role)

    return RedirectResponse('/profile?success=nickname_changed', status_code=303)

@router.get('/profile/change-password')
def change_password_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return render_template('login.mako', request=request, error='Пожалуйста, войдите в систему')
    return render_template('change_password.mako', request=request)
    
@router.post('/profile/change-password')
async def change_password(
    request: Request,
    old_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return RedirectResponse(url='/auth/login-page', status_code=303)
    
    # Проверяем старый пароль
    if not verify_password(old_password, current_user.hashed_password):
        return render_template('change_password.mako', request=request, error='Неверный пароль')
    
    # Проверяем, что новый пароль введен
    if not new_password or len(new_password) < 6:
        return render_template('change_password.mako', request=request, error='Новый пароль должен содержать минимум 6 символов')
    
    # Проверяем, что пароли совпадают
    if new_password != confirm_password:
        return render_template('change_password.mako', request=request, error='Пароль не совпадает с новым')

    # Меняем пароль
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()

    # Отправляем уведомление на Email
    await send_password_changed_email(current_user.email, current_user.username)

    # Выходим из системы на страницу входа
    response = RedirectResponse(url='/auth/login-page?success=password_changed', status_code=303)
    response.delete_cookie('access_token')
    return response

@router.post('/profile/add-phone')
def add_phone(
    request: Request,
    phone: str = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return RedirectResponse(url='/auth/login-page', status_code=303)
    
    if not phone or len(phone) < 10:
        return RedirectResponse(url='/profile?error=invalid_phone', status_code=303)
    
    current_user.phone = phone
    db.commit()

    return RedirectResponse(url='/profile?success=phone_added', status_code=303)

'''@router.post('/profile/enable-2fa-request')
def enable_2fa_request(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return RedirectResponse(url='/auth/login-page', status_code=303)

    if not current_user.phone:
        return RedirectResponse(url='/profile?error=no_phone_first', status_code=303)
    
    code = str(random.randint(100000, 999999))
    store_verification_code(current_user.id, code, 300)

    print(f"📱 SMS на {current_user.phone}: Ваш код подтверждения для включения 2FA: {code}")

    return RedirectResponse(url='/profile/verify-2fa-page', status_code=303)'''

@router.get('/profile/verify-2fa-page')
def verify_2fa_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return render_template('login.mako', request=request, error='Пожалуйста, войдите в систему')
    return render_template('verify_2fa.mako', request=request, user_id=current_user.id)

@router.post('/profile/verify-2fa')
def verify_2fa(
    request: Request,
    code: str = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return RedirectResponse(url='/auth/login-page', status_code=303)
    
    if not verify_verification_code(current_user.id, code):
        return RedirectResponse(url='/profile/verify-2fa-page?error=invalid_code', status_code=303)
    
    current_user.is_2fa_enabled = True
    db.commit()
    
    set_user_role_cache(current_user.id, current_user.role)
    
    return RedirectResponse(url='/profile?success=2fa_enabled', status_code=303)


'''@router.post('/profile/disable-2fa')
def disable_2fa(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return RedirectResponse(url='/auth/login-page', status_code=303)
    
    current_user.is_2fa_enabled = False
    db.commit()
    
    set_user_role_cache(current_user.id, current_user.role)

    return RedirectResponse(url='/profile?success=2fa_disabled', status_code=303)'''

@router.post('/profile/send-phone-code')
@limiter.limit('3/minute')
def send_phone_code(
    request: Request,
    phone: str = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    # Отправляет код подтверждения на указанный телефон
    if not current_user:
        return RedirectResponse(url='/auth/login-page', status_code=303)
    
    # Простая валидация телефона
    if not phone or len(phone) < 10:
        return RedirectResponse(url='/profile?error=invalid_phone', status_code=303)
    
    # Генерируем код
    # code = str(random.randint(100000, 999999))   пока не подключены SMS нужно убрать
    code = '123456'

    # Сохраняем код в Redis (связываем с номером телефона)
    store_phone_verification_code(phone, code, 300)

    # Отправляем SMS
    if send_verification_code(phone, code):
        # Временно сохраняем телефон в сессии/cookie для следующего шага
        response = RedirectResponse(url='/profile/verify-phone-page', status_code=303)
        response.set_cookie(key='pending_phone', value=phone, httponly=True, max_age=300)
        return response
    else:
        return RedirectResponse(url='/profile?error=sms_failed', status_code=303)
    
@router.get('/profile/verify-phone-page')
def verify_phone_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    # Страница ввода кода подтверждения телефона
    if not current_user:
        return render_template('login.mako', request=request, error='Пожалуйста войдите в систему')
    
    # Получаем телефон из cookie
    pending_phone = request.cookies.get('pending_phone')
    if not pending_phone:
        return RedirectResponse(url='/profile?error=no_pending_phone', status_code=303)
    
    return render_template('verify_phone.mako', request=request, phone=pending_phone)

@router.post('/profile/verify-phone')
@limiter.limit('10/minute')
def verify_phone(
    request: Request,
    code: str = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    # Подтверждает код и сохраняет телефон
    if not current_user:
        return RedirectResponse(url='/auth/login-page', status_code=303)
    
    # Получаем телефон из cookie
    pending_phone = request.cookies.get('pending_phone')
    if not pending_phone:
        return RedirectResponse(url='/profile?error=no_pending_phone', status_code=303)
    
    # Проверяем код
    if not verify_phone_code(pending_phone, code):
        return RedirectResponse(url='/profile/verify-phone-page?error=invalid_code', status_code=303)
    
    # Код верный -> сохраняем телефон
    current_user.phone = pending_phone
    db.commit()

    # Удаяляем временную cookie
    response = RedirectResponse(url='/profile?succes-phone_added', status_code=303)
    response.delete_cookie('pending_phone')

    return response

# Удаление номера телефона 

@router.post('/profile/remove-phone')
def remove_phone(
    request: Request,
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return RedirectResponse(url='/auth/login-page', status_code=303)
    
    # Если 2FA включена, сначала нужно ее отключить
    if current_user.is_2fa_enabled:
        return RedirectResponse(url='/profile?error=disable_2fa_first', status_code=303)
    
    current_user.phone = None
    db.commit()

    return RedirectResponse(url='/profile?success=phone_removed', status_code=303)

@router.post('/profile/send-verification-email')
async def send_verification_email_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return RedirectResponse(url='/auth/login-page', status_code=303)
    
    # Если email уже подтвержден
    if current_user.is_email_verified:
        return RedirectResponse(url='/profile?error=already_verified', status_code=303)
    
    # Генерируем новый токен
    verification_token = str(uuid.uuid4())
    current_user.email_verification_token = verification_token
    db.commit()

    # Отправляем письмо
    from app.email_utils import send_verification_email
    await send_verification_email(current_user.email, current_user.username, verification_token)

    # Передаем время отправки в URL
    send_time = datetime.utcnow().isoformat()
    return RedirectResponse(url='/profile/email-verification-pending?send_time={send_time}', status_code=303)

@router.get('/profile/email-verification-pending')
def email_verification_pending(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return RedirectResponse(url='/auth/login-page', status_code=303)
    
    if current_user.is_email_verified:
        return RedirectResponse(url='/profile?success=email_verified', status_code=303)
    
    return render_template('email_verification_pending.mako', request=request, email=current_user.email)

@router.post('/profile/resend-verification-email')
async def resend_verification_email(
    request = Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return RedirectResponse(url='/auth/login-page', status_code=303)
    
    if current_user.is_email_verified:
        return RedirectResponse(url='/profile?error=already_verified', status_code=303)
    
    # Генерируем новый токен
    verification_token = str(uuid.uuid4())
    current_user.email_verification_token = verification_token
    db.commit()

    # Отправляем письмо
    await send_verification_email(current_user.email, current_user.username, verification_token)

    send_time = datetime.utcnow().isoformat()
    return RedirectResponse(url='/profile/email-verification-pending?send_time={send_time}', status_code=303)

@router.post('/activate-trial-vip-temporary')
def activate_trial_vip_temporary(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return RedirectResponse(url='/auth/login-page', status_code=303)
    
    # Даем пробный VIP на 7 дней
    current_user.role = 'vip'
    current_user.subscription_expires_at = datetime.utcnow() + timedelta(days=7)
    current_user.trial_used = True
    db.commit()

    # Обновляем кэш
    delete_user_role_cache(current_user.id)
    set_user_role_cache(current_user.id, 'vip')

    # Создаем новый токен с обновленной ролью
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={'sub': current_user.email, 'role': 'vip'}, expires_delta=access_token_expires
    )

    response = RedirectResponse(url='/vip-success-temporary', status_code=303)
    response.set_cookie(key='access_token', value=new_access_token, httponly=True)

    return response

@router.get('/vip-success-temporary')
def vip_success_temporary(request: Request):
    return render_template('vip_success_temporary.mako', request=request)

@router.get('/coming-soon')
def coming_soon_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    return render_template('coming_soon.mako', request=request)

@router.post('/activate-paid-vip')
def activate_paid_vip(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_cookie)
):
    if not current_user:
        return RedirectResponse(url='/auth/login-page', status_code=303)
    
    # Получаем выбранный интервал из cookie
    interval = request.cookies.get('pending_vip_interval', 'month')

    # Устанавливаем срок подписки
    if interval == 'month':
        current_user.subscription_expires_at = datetime.utcnow() + timedelta(days=30)
    else:
        current_user.subscription_expires_at = datetime.utcnow() + timedelta(days=365)

    current_user.role = 'vip'
    db.commit()

    # Обновляем кэш
    delete_user_role_cache(current_user.id)
    set_user_role_cache(current_user.id, 'vip')

    # Создаем новый токен с обновленной ролью
    acces_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={'sub': current_user.email, 'role': 'vip'},
        expires_delta=acces_token_expires
    )

    # Удаляем cookie с интервалом
    response = RedirectResponse(url='/vip-success', status_code=303)
    response.delete_cookie('pending_vip_interval')
    response.set_cookie(key='access_token', value=new_access_token, httponly=True)

    return response

@router.get('/health')
def health_check(db: Session = Depends(get_db)):
    # Проверка работоспособности сервера
    try:
        # Проверяем подключение к БД
        db.execute(text("SELECT 1"))
        db_status = 'ok'
    except Exception as e:
        db_status = str(e)

    return {
        'status': 'healthy',
        'database': db_status,
        'redis': 'ok' if redis_client.ping() else 'error',
        'version': '1.0.0'
    }