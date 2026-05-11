from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import random
import requests

from app.redis_utils import store_2fa_code, verify_2fa_code, redis_client, store_phone_verification_code, verify_phone_code

from app.database import get_db, add_and_refresh
from app.models import User
from app.auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, get_user_by_email, authenticate_user,  
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.sms_utils import send_verification_code
from app.templating import render_template

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
def register_page_submit(
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
        existing = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        if existing:
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

        new_user = User(
            email=email,
            username=username,
            phone=phone,
            hashed_password=get_password_hash(password),
            role='user'   # по умолчанию обычный пользователь
        )
        add_and_refresh(db, new_user)
        return RedirectResponse(url="/auth/login-page", status_code=303)

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

@router.post('/upgrade-to-vip')
def upgrade_to_vip(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Повышает роль пользователя до VIP
    current_user.role = 'vip'
    db.commit()
    return {'message': 'Поздравляем, вы теперь VIP пользователь! Вам доступно неограниченное количество задач!'}

@router.post("/login-page")
def login_page_submit(
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
    
    # Если включена 2FA
    if user.phone:
        code = str(random.randint(100000, 999999))
        store_2fa_code(user.id, code, 300)
        send_sms(user.phone, code)
        return render_template('2fa.mako', request=request, user_id=user.id)
    
    # Если 2FA не включена - сразу логиним
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

@router.post('/verify-2fa')
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
        data={'sub': user.email}, expires_delta=acces_token_expires
    )

    response = RedirectResponse(url='/', status_code=303)
    response.set_cookie(key='access_token', value=access_token, httponly=True)
    return response

@router.get("/logout")
def logout():
    """Выход из системы"""
    response = RedirectResponse(url="/auth/login-page", status_code=303)
    response.delete_cookie("access_token")
    return response


# ========== API ЭНДПОИНТЫ (JSON) ==========

@router.post("/register")
def api_register(email: str, password: str, db: Session = Depends(get_db)):
    """Регистрация через API (JSON)"""
    existing_user = get_user_by_email(db, email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(email=email, hashed_password=get_password_hash(password))
    return add_and_refresh(db, new_user)


@router.post("/login")
def api_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
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
def api_get_me(current_user: User = Depends(get_current_user)):
    """Получить информацию о текущем пользователе (JSON)"""
    return current_user