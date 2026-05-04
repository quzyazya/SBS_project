from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
from yookassa import Configuration, Payment, PaymentMethod

from app.config import settings
from app.database import get_db
from app.models import User
from app.auth import get_current_user, get_user_from_token
from app.templating import render_template

router = APIRouter(prefix='/payments', tags=['Payments'])

# Настройка ЮKassa

@router.post('/create-payment')
async def create_payment(interval: str = Form(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Создает платеж в ЮKassa

    # Определяем сумму и описание
    if interval == 'month':
        amount = 25.00
        description = 'VIP подписка на 1 месяц'
    else:
        amount = 250.00
        description = 'VIP подписка на 1 год'

    # Уникальный ID заказа
    order_id = str(uuid.uuid4())

    try:
        # Создаем платеж
        payment = Payment.create({
            'amount': {
                'value': f'{amount:.2f}',
                'currency': 'RUB'
            },
            'payment_method_data': {
                'type': 'bank_card'
            },
            'confirmation': {
                'type': 'redirect',
                'return_url': f'http://localhost:8000/payments/success?order_id={order_id}&interval={interval}'
            },
            'description': description,
            'metadata': {
                'user_id': str(current_user.id),
                'user_email': current_user.email,
                'interval': interval,
                'order_id': order_id
            }
        })

        # Сохраняем информацию о платеже в БД
        # Здесь можно создать модель Payment в <L
        
        # Перенаправляем на страницу оплаты 
        return RedirectResponse(url=payment.confirmation.confirmation_url, status_code=303)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get('/success')
async def payment_success(
    order_id: str,
    interval: str,
    request: Request,
    db: Session = Depends(get_db)
):
    # Страница успешной оплаты

    # Получаем пользователя из cookie
    user = get_user_from_token(db, request)

    if user:
        # Обновляем статус пользователя
        if interval == 'month':
            user.subscription_expires_at = datetime.utcnow() + timedelta(days=30)
        else:
            user.subscription_expires_at = datetime.utcnow() + timedelta(days=365)
        
        user.role = 'vip'
        db.commit()

    return RedirectResponse(url='/?payment-success', status_code=303)

@router.get('/cancel')
async def payment_cancel():
    return RedirectResponse(url='/?payment-canceled')

@router.post('/webhook')
async def yookassa_webhook(request: Request, db: Session = Depends(get_db)):
    # Обработчик вебхуков ЮKassa
    body = await request.json()

    # Проверяем подпись вебхука 
    
    if body.get('event') == 'payment.succeeded':
        payment = body.get('object', {})
        metadata = payment.get('metadata', {})
        user_id = int(metadata.get('user_id', 0))
        interval = metadata.get('interval', 'month')

        user = db.query(User).filter(User.id == user_id).first()
        if user:
            if interval == 'month':
                user.subscription_expires_at = datetime.utcnow() + timedelta(days=30)
            else:
                user._subscription_expires_at = datetime.utcnow() + timedelta(days=365)
            user.role = 'vip'
            db.commit()

    return JSONResponse(content={'status': 'ok'})























