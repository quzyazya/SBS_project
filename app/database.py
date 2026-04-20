from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

# Синхронный движок
engine = create_engine(  # Создаётся "движок" — центральный объект, который управляет подключениями к базе данных.
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# Фабрика сессий
SessionLocal = sessionmaker(   # Создаётся "фабрика", которая будет выдавать новые сессии (соединения с БД) по запросу.
    engine,
    autocommit=False,
    autoflush=False
)

# async_session_maker = async_sessionmaker(   # Создаётся "фабрика", которая будет выдавать новые сессии (соединения с БД) по запросу.
#     engine,
#     class_=AsyncSession,    # Говорит фабрике создавать именно асинхронные сессии
#     expire_on_commit=False  # Говорит SQLAlchemy "не удаляй данные из объекта после сохранения в БД", исключает танцы с бубном через refresh()
# )

# Базовый класс для моделей
class Base(DeclarativeBase):
    pass

# Зависимость для FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()