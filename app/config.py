from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Настройки приложения / Network settings
    APP_NAME: str = "SBS"
    DEBUG: bool = True
    
    # Настройки базы данных / Database settings
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    # Общие SMTP настройки
    SMTP_FROM_NAME: str = 'ProgressPal'

    # SMTP для Mail.ru
    SMTP_MAILRU_HOST: str = 'smtp.mail.ru'
    SMTP_MAILRU_PORT: int = 465
    SMTP_MAILRU_USER: str
    SMTP_MAILRU_PASSWORD: str
    
    # SMTP для Gmail
    SMTP_GMAIL_HOST: str = "smtp.gmail.com"
    SMTP_GMAIL_PORT: int = 587
    SMTP_GMAIL_USER: str = ""
    SMTP_GMAIL_PASSWORD: str = ""
    
    # SMTP для Яндекс
    SMTP_YANDEX_HOST: str = "smtp.yandex.ru"
    SMTP_YANDEX_PORT: int = 465
    SMTP_YANDEX_USER: str = ""
    SMTP_YANDEX_PASSWORD: str = ""

    # SMTP для Mailpit (тестовый)
    SMTP_MAILPIT_HOST: str = 'mailpit'
    SMTP_MAILPIT_PORT: int = 1025
    SMTP_MAILPIT_USER: str = ''
    SMTP_MAILPIT_PASSWORD: str = ''

    # ЮКаssa
    YOOKASSA_SHOP_ID: str
    YOOKASSA_SECRET_KEY: str

    # JWT
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # REDIS
    REDIS_URL: str = 'redis://localhost:6379/0'
    
    SMSC_LOGIN: str = ""
    SMSC_PASSWORD: str = ""

    # для синхронных операций (Alembic, psycopg2)
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()