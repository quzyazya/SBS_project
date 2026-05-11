import requests
from app.config import settings
from app.redis_utils import redis_client

def send_sms(phone: str, message: str) -> bool:
    # Отправляет SMS через SMSC.ru
    # Аргументы:
    #     phone: номер телефонка в международном формате (н-р, 79001234567)
    #     message: текст сообщения
    # Возвращает:
    #   True если отправлено успешно, иначе False

    # Удаляем лишние символы из номера
    clean_phone = phone.replace('+', '').replace('-', '').replace(' ', '')

    # Параметры запроса к SMSC.ru
    params = {
        'login': settings.SMSC_LOGIN,
        'psw': settings.SMSC_PASSWORD,
        'phones': clean_phone,
        'mes': message,
        'fmt': 3,   # JSON формат ответа
        'charset': 'utf-8',
    }

    try:
        response = requests.get('https://smsc.ru/sys/send.php', params=params, timeout=10)
        data = response.json()

        # Проверка ответа
        if 'error_code' in data:
            print(f'SMS error: {data.get('error')}')
            return False
        
        print(f'SMS успешно отправлено на номер: {phone}. ID: {data.get('id')}')
        return True
    
    except Exception as e:
        print(f'Failed to send SMS: {e}')
        return False

def send_verification_code(phone: str, code: str):
    # Отправляет код подтверждения на телефон
    message = f'Ваш код подтверждения: {code}. Никому не сообщайте этот код.'
    return send_sms(phone, message)