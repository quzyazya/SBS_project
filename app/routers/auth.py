from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
import requests
from app.rate_limit import limiter

from app.redis_utils import delete_user_role_cache, set_user_role_cache, store_2fa_code, verify_2fa_code, redis_client, store_phone_verification_code, verify_phone_code

from app.database import get_db, add_and_refresh
from app.models import User
from app.auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, get_user_by_email, authenticate_user,  
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.sms_utils import send_verification_code
from app.templating import render_template
from app.email_utils import send_verification_email, send_password_reset_email, send_welcome_email
import uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Простая залушка
def send_sms(phone: str, code: str) -> bool:
    print(f'[Тест] SMS на номер {phone}: Ваш код подтверждения: {code}')
    return True

# ========== HTML ЭНДПОИНТЫ (страницы для браузера) ==========

@router.get("/register-page")
def register_page(request: Request):
    """Страница регистрации HTML"""
    return render_template("register.mako", request=request, error=None)


@router.post("/register-page")
@limiter.limit('3/minute')
async def register_page_submit(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    phone: str = Form(None),
    password: str = Form(...),
    action: str = Form('register'),
    db: Session = Depends(get_db)
):
    # Если телефон указан и это первый шаг -> отправляем код
    if phone and len(phone) >= 10 and action == 'register':
        # Проверяем, не занят ли email или никнейм
        existing_user = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        if existing_user:
            return render_template('register.mako', request=request, error='Email или никнейм уже занят')

        # Сохраняем данные в сессии (временное хранилище)
        request.session['pending_registration'] = {
            'email': email,
            'username': username,
            'phone': phone,
            'password': password
        }

        # Генерируем и отправляем код
        code = str(random.randint(100000, 999999))
        store_phone_verification_code(phone, code, 300)
        send_verification_code(phone, code)

        # Перенаправляем на страницу подтверждения
        return RedirectResponse(url='/auth/verify-registration-page', status_code=303)

    # Если телефон не указан -> сразу регистрируем
    if not phone:
        existing_user = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        if existing_user:
            return render_template('register.mako', request=request, error='Email или никнейм уже занят')

        # Генерируем токен подтверждения email
        verification_token = str(uuid.uuid4())

        new_user = User(
            email=email,
            username=username,
            phone=phone,
            hashed_password=get_password_hash(password),
            role='user',   # по умолчанию обычный пользователь
            is_email_verified=False,
            email_verification_token=verification_token
        )
        add_and_refresh(db, new_user)

        # Отправляем email с подтверждением 
        await send_verification_email(email, username, verification_token)

        # Показываем страницу успеха
        return render_template('register_success.mako', request=request, email=email)
    
    # Если телефон указан, но уже есть код в сессии (шаг 2 - подтверждеине)
    # Этот блок обрабатывается отдельным эндпоинтом /auth/verify-registration
    return RedirectResponse(url='/auth/register-page', status_code=303)
        

@router.get('/verify-registration-page')
def verify_registration_page(request: Request):
    # Страница ввода кода подтверждения
    pending = request.session.get('pending_registration')
    if not pending:
        return RedirectResponse(url='/auth/register-page', status_code=303)
    
    return render_template('verify_registration.mako',
                           request=request,
                           email=pending['email'],
                           username=pending['username'],
                           phone=pending['phone'],
                           password=pending['password']
    )

@router.post('/verify-registration')
@limiter.limit('5/minute')
def verify_registration(
    request: Request,
    code: str = Form(...),
    email: str = Form(...),
    username: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    if not verify_phone_code(phone, code):
        return render_template('verify_registration.mako',
                               request=request,
                               error='Неверный код подтверждения',
                               email=email, username=username, phone=phone, password=password
        )
    
    # Регистрируем пользователя
    existing = db.query(User).filter(
        (User.email == email) | (User.username == username)
    ).first()
    if existing:
        return render_template('register.mako', request=request, error='Email или никнейм уже занят')
    
    new_user = User(
        email=email,
        username=username,
        phone=phone,
        hashed_password=get_password_hash(password),
        role='user'
    )
    add_and_refresh(db, new_user)

    # Очищаем сессию
    request.session.pop('pending_registration', None)

    return RedirectResponse(url='/auth/login-page', status_code=303)

@router.get("/login-page")
def login_page(request: Request):
    """Страница входа HTML"""
    return render_template("login.mako", request=request, error=None)

@router.get('/forgot-password')
def forgot_password_page(request: Request):
    # Страница запроса восстановления пароля
    return render_template('forgot_password.mako', request=request, error=None)

@router.post('/forgot-password')
@limiter.limit('3/hour')
async def forgot_password(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    # Отправка ссылки для восстановления пароля
    user = db.query(User).filter(User.email == email).first()

    # Проверка подтверждения email
    if user and not user.is_email_verified:
        # Email не подтвержден - письмо не отправится
        return render_template('forgot_password.mako', request=request, error='Сначала подтвердите email. Проверьте почту.')

    # Для безопасности не сообщаем, существует ли email
    if user:
        # Генерируем токен
        token = str(uuid.uuid4())
        user.reset_password_token = token
        user.reset_password_expires = datetime.utcnow() + timedelta(hours=1)

        # Отправляем email
        await send_password_reset_email(email, user.username, token)

    return render_template('forgot_password_sent.mako', request=request, email=email)

@router.get('/reset-password')
def reset_password_page(request: Request, token: str, db: Session = Depends(get_db)):
    # Страница ввода нового пароля
    user = db.query(User).filter(
        User.reset_password_token == token,
        User.reset_password_expires > datetime.utcnow()
    ).first()

    if not user:
        return render_template('login.mako', request=request, error='Ссылка недействительная или истекла')
    
    return render_template('reset_password.mako', request=request, token=token)

@router.post('/reset-password')
@limiter.limit('3/hour')
def reset_password(
    request: Request,
    token: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Сохранение нового пароля
    user = db.query(User).filter(
        User.reset_password_token == token,
        User.reset_password_expires > datetime.utcnow()
    ).first()

    if not user:
        return render_template('login.mako', request=request, error='Ссылка недействительна или истекла')

    user.hashed_password = get_password_hash(password)
    user.reset_password_token = None
    user.reset_password_expires = None
    db.commit()

    return RedirectResponse(url='/auth/login-page?reset=success', status_code=303)

@router.post("/login-page")
@limiter.limit('5/minute')
async def login_page_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Обработка логина из HTML формы"""

    # Поиск пользователя по email или username 
    user = db.query(User).filter(
        (User.email == username) | (User.username == username)
    ).first()

    # user = authenticate_user(db, username, password)
    if not user or not verify_password(password, user.hashed_password):
        return render_template("login.mako", request=request, error="Неверный email, имя пользователя или пароль")
    
    # Проверка
    # if not user.is_email_verified:
    #     return render_template('login.mako', request=request, error='Подтвердите email перед входим. Проверьте почту.')

    # Отправляем приветственное письмо при первом входе 
    # if not hasattr(user, 'welcome_sent') or not user.welcome_sent:
    #     await send_welcome_email(user.email, user.username)
    #     user.welcome_sent = True
    #     db.commit()

    # Если включена 2FA
    if user.phone:
        # code = str(random.randint(100000, 999999))    пока не подключены SMS нужно убрать
        code = '123456'
        store_2fa_code(user.id, code, 300)
        send_sms(user.phone, code)
        return render_template('2fa.mako', request=request, user_id=user.id)
    
    # Если 2FA не включена - сразу логиним
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, 'role': user.role}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)

    # Если это первый вход (welcome не отправляли и не показывали страницу)
    if not hasattr(user, 'welcome_shown') or not user.welcome_shown:
        user.welcome_shown = True
        db.commit()
        # Перенаправляем на страницу-приветствие
        return RedirectResponse(url='/welcome', status_code=303)

    return response

@router.post('/verify-2fa')
@limiter.limit('5/minute')
def verify_2fa(
    request: Request,
    user_id: int = Form(...),
    code: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return render_template('login.mako', request=request, error='Пользователь не найден')
    
    if not verify_2fa_code(user.id, code):
        return render_template('2fa.mako', request=request, user_id=user.id, error='Неверный код подтверждения')
    

    acces_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.email, 'role': user.role}, expires_delta=acces_token_expires
    )

    response = RedirectResponse(url='/', status_code=303)
    response.set_cookie(key='access_token', value=access_token, httponly=True)
    return response

@router.get('/verify-email')
async def verify_email(request: Request, token: str, db: Session = Depends(get_db)):
    # Подтверждение email при регистрации
    user = db.query(User).filter(User.email_verification_token == token).first()

    if not user:
        return render_template('login.mako', request=request, error='Недействительная ссылка подтверждения')
    
    user.is_email_verified = True
    user.email_verification_token = None
    db.commit()

    # Обновляем кэш роли
    delete_user_role_cache(user.id)
    set_user_role_cache(user.id, user.role)

    # Отправляем приветственное письмо (только если еще не отправляли)
    if not user.welcome_sent:
        await send_welcome_email(user.email, user.username)
        user.welcome_sent = True
        db.commit()

    # Показываем страницу успеха с кнопкой "Продолжить"
    return render_template('email_verified_success.mako', request=request)

@router.get("/logout")
def logout():
    """Выход из системы"""
    response = RedirectResponse(url="/auth/login-page", status_code=303)
    response.delete_cookie("access_token")
    return response


# ========== API ЭНДПОИНТЫ (JSON) ==========

@router.post("/register")
@limiter.limit('3/minute')
def api_register(request: Request, email: str, password: str, db: Session = Depends(get_db)):
    """Регистрация через API (JSON)"""
    existing_user = get_user_by_email(db, email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(email=email, hashed_password=get_password_hash(password))
    return add_and_refresh(db, new_user)


@router.post("/login")
@limiter.limit('5/minute')
def api_login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Логин через API (JSON), возвращает JWT токен"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
@limiter.limit('100/minute')
def api_get_me(request: Request, current_user: User = Depends(get_current_user)):
    """Получить информацию о текущем пользователе (JSON)"""
    return current_user