import json

from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
from yookassa import Configuration, Payment

from app.config import settings
from app.database import get_db
from app.models import User
from app.auth import get_current_user
# from app.templating import render_template

router = APIRouter(prefix='/payments', tags=['Payments'])

# Настраиваем ЮKassa с ключами из .env
Configuration.configure(settings.YOOKASSA_SHOP_ID, settings.YOOKASSA_SECRET_KEY)

@router.post('/create-payment')
async def create_payment(interval: str = Form(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Создает платеж в ЮKassa и перенаправляет пользователя на страницу оплаты

    # Определяем сумму и описание в зависимости от выбранной подписки
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
    interval: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Страница успешной оплаты (вызывается после возврата из ЮKassa)

    if current_user:
        # Обновляем статус пользователя
        if interval == 'month':
            current_user.subscription_expires_at = datetime.utcnow() + timedelta(days=30)
        else:
            current_user.subscription_expires_at = datetime.utcnow() + timedelta(days=365)
        
        current_user.role = 'vip'
        db.commit()

    return RedirectResponse(url='/?payment-success', status_code=303)

@router.get('/cancel')
async def payment_cancel():
    # Страница отмены оплаты
    return RedirectResponse(url='/?payment-canceled')

@router.post('/webhook')
async def yookassa_webhook(request: Request, db: Session = Depends(get_db)):
    # Обработчик вебхуков ЮKassa (страховка на случай еслит пользователь не вернулся на сайт)
    body = await request.json()

    # Проверяем подпись вебхука 
    
    try:
        data = json.loads(body)

        if data.get('event') == 'payment.succeeded':
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

    except json.JSONDecodeError:    
        return JSONResponse(content={
            'status': 'error',
            'message': 'Invalid JSON' 
        }, status_code=400)
    
    except Exception as e:
        print(f'Webhook error: {e}')
        return JSONResponse(content={
            'status': 'error',
            'message': str(e)
        }, status_code=400) 

    return JSONResponse(content={'status': 'ok'})























