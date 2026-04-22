from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db, add_and_refresh
from app.models import User
from app.auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.templating import render_template

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()


# ========== HTML ЭНДПОИНТЫ (Mako) ==========

@router.get("/register-page")
def register_page(request: Request):
    return render_template("register.mako", request=request, error=None)


@router.post("/register-page")
def register_page_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing_user = get_user_by_email(db, email)
    if existing_user:
        return render_template("register.mako", request=request, error="Email уже зарегистрирован")
    
    new_user = User(email=email, hashed_password=get_password_hash(password))
    add_and_refresh(db, new_user)
    return RedirectResponse(url="/auth/login-page", status_code=303)


@router.get("/login-page")
def login_page(request: Request):
    return render_template("login.mako", request=request, error=None)


@router.post("/login-page")
def login_page_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return render_template("login.mako", request=request, error="Неверный email или пароль")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/auth/login-page", status_code=303)
    response.delete_cookie("access_token")
    return response


# ========== API ЭНДПОИНТЫ ==========

@router.post("/register")
def api_register(email: str, password: str, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(email=email, hashed_password=get_password_hash(password))
    return add_and_refresh(db, new_user)


@router.post("/login")
def api_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
def api_get_me(current_user: User = Depends(get_current_user)):
    return current_user