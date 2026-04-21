from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index = True)
    email = Column(String(100), unique = True, index = True, nullable = False)
    hashed_password = Column(String(200), nullable = False)
    is_active = Column(Boolean, default = True)
    created_at = Column(DateTime, server_deafult = func.now())

    # Связь с задачами (один пользователь -> много задач)
    tasks = relationship('Task', back_populates = 'owner', cascade = 'all, delete-orphan')

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index = True)
    title = Column(String(50), nullable=False)
    content = Column(Text, nullable=True)
    deadline = Column(DateTime, nullable=True)
    is_done = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Внешний ключ к пользователю
    owner_id = Column(Integer, ForeignKey('users.id'), nullable = False)

    # Связь с пользователем
    owner = relationship('User', back_populates = 'tasks')

