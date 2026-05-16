import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from mako.lookup import TemplateLookup
from app.config import settings

# Настройка Mako для шаблонов писем
templates_dir = os.path.join(os.path.dirname(__file__), 'templates', 'emails')
template_lookup = TemplateLookup(directories=[templates_dir], input_encoding='utf-8', output_encoding='utf-8')

def render_email_template(template_name: str, **context) -> str:
    # Рендерит Mako шаблон для email
    template = template_lookup.get_template(template_name)
    return template.render(**context)

def get_email_config(email: str) -> ConnectionConfig:
    # Возвращает SMTP-конфигурацию в зависимости от домена email
    # Настройка подключения к SMTP

    # Для Mailpit
    '''return ConnectionConfig(
        MAIL_USERNAME="",
        MAIL_PASSWORD="",
        MAIL_FROM="test@example.com",
        MAIL_FROM_NAME=settings.SMTP_FROM_NAME,
        MAIL_PORT=1025,
        MAIL_SERVER="mailpit",
        MAIL_STARTTLS=False,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=False,
        VALIDATE_CERTS=False
    )'''

    # Для Gmail
    if 'gmail.com' in email:
        return ConnectionConfig(
            MAIL_USERNAME=settings.SMTP_GMAIL_USER,
            MAIL_PASSWORD=settings.SMTP_GMAIL_PASSWORD,
            MAIL_FROM=settings.SMTP_GMAIL_USER,
            MAIL_FROM_NAME=settings.SMTP_FROM_NAME,
            MAIL_PORT=587,
            MAIL_SERVER='smtp.gmail.com',
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
    
    # Для Mail.ru
    elif 'mail.ru' in email or 'inbox.ru' in email or 'list.ru' in email or 'bk.ru' in email:
        return ConnectionConfig(
            MAIL_USERNAME=settings.SMTP_MAILRU_USER,
            MAIL_PASSWORD=settings.SMTP_MAILRU_PASSWORD,
            MAIL_FROM=settings.SMTP_MAILRU_USER,
            MAIL_FROM_NAME=settings.SMTP_FROM_NAME,
            MAIL_PORT=465,
            MAIL_SERVER='smtp.mail.ru',
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=True,  # Mail.ru использует SSL на порту 465
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
    
    # Для Яндекс.Почты
    elif 'yandex.ru' in email:
        return ConnectionConfig(
            MAIL_USERNAME=settings.SMTP_YANDEX_USER,
            MAIL_PASSWORD=settings.SMTP_YANDEX_PASSWORD,
            MAIL_FROM=settings.SMTP_YANDEX_USER,
            MAIL_FROM_NAME=settings.SMTP_FROM_NAME,
            MAIL_PORT=465,
            MAIL_SERVER='smtp.yandex.ru',
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=True,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
    
    # Конфигурация для других доменов 
    else:
        # Используем Gmail как fallback
        return ConnectionConfig(
            MAIL_USERNAME=settings.SMTP_GMAIL_USER,
            MAIL_PASSWORD=settings.SMTP_GMAIL_PASSWORD,
            MAIL_FROM=settings.SMTP_GMAIL_USER,
            MAIL_FROM_NAME=settings.SMTP_FROM_NAME,
            MAIL_PORT=587,
            MAIL_SERVER='smtp.gmail.com',
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )

def extract_email_domain(email: str) -> str:
    # Извлекает домен из email адреса
    try:
        return email.split('@')[1].lower()
    except IndexError:
        return ''

async def send_verification_email(email: str, username: str, token: str) -> bool:
    # Отправляет письмо для подтверждения email с правильным SMTP
    verification_url = f'http://localhost:8000/auth/verify-email?token={token}'

    try:
        # Получаем правильную конфигурацию для этого email
        conf = get_email_config(email)

        html_content = render_email_template(
            'verification.mako',
            username=username,
            verification_url=verification_url
        )

        message = MessageSchema(
            subject='Подтверждение email - ProgressPal',
            recipients=[email],
            body=html_content,
            subtype='html'
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        print(f'☑️ Email отправлен на {email}')
        return True
    except Exception as e:
        print(f'✖️ Ошибка отправки email на {email}: {str(e)}')
        return False

async def send_password_reset_email(email: str, username: str, token: str):
    # Отправляет письмо для сброса пароля
    reset_url = f'http://localhost:8000/auth/reset-password?token={token}'

    try:
        conf = get_email_config(email)

        html_content = render_email_template(
            'reset_password.mako',
            username=username,
            reset_url=reset_url
        )

        message = MessageSchema(
            subject='Сброс пароля - ProgressPal',
            recipients=[email],
            body=html_content,
            subtype='html'
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        print(f"☑️ Email для сброса пароля отправлен на {email}")
        return True
    except Exception as e:
        print(f'✖️ Ошибка отправки приветственного email на {email}: {str(e)}')
        return False
    
async def send_password_changed_email(email: str, username: str) -> bool:
    # Отправляет уведомление об успешной смене пароля
    try:
        conf = get_email_config(email)

        html_content = render_email_template(
            'password_changed.mako',    # Используем шаблон        
            username=username
        )

        message = MessageSchema(
            subject='Ваш пароль был изменён - ProgressPal',
            recipients=[email],
            body=html_content,
            subtype='html'
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        print(f'☑️ Уведомление о смене пароля отправлено на {email}')
        return True
    except Exception as e:
        print(f'✖️ Ошибка отправки уведомления на {email}: {str(e)}')
        return False

async def send_welcome_email(email: str, username: str):
    # Отправляет приветственное письмо
    html_content = render_email_template('welcome.mako', username=username)

    conf = get_email_config(email)

    message = MessageSchema(
        subject='Добро пожаловать в ProgressPal!',
        recipients=[email],
        body=html_content,
        subtype='html'
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    print(f"☑️ Приветственный email отправлен на {email}")