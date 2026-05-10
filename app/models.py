from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    hashed_password = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    role = Column(String(20), default='user')  # f.Ex: (user, vip)

    # 2FA поля
    is_2fa_enabled = Column(Boolean, default=False)
    otp_secret = Column(String(100), nullable=True)
    tasks = relationship('Task', back_populates='owner', cascade='all, delete-orphan')


class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    deadline = Column(DateTime, nullable=True)
    is_done = Column(Boolean, default=False)
    is_starred = Column(Boolean, default = False)
    
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    owner = relationship('User', back_populates='tasks')
    checkpoints = relationship('CheckPoint', back_populates='task', cascade='all, delete-orphan')
    
    # ========== СВОЙСТВА ==========
    
    @property
    def progress_percent(self) -> int:
        """Процент выполнения задачи (0% или 100%, только при полном завершении)"""
        return 100 if self.is_done else 0
    
    @property
    def deadline_color(self) -> str:
        """Цвет индикатора дедлайна"""
        if self.is_done:
            return "success"
        if not self.deadline:
            return "secondary"
        
        from datetime import datetime
        days_left = (self.deadline.date() - datetime.utcnow().date()).days
        
        if days_left < 0:
            return "danger"
        elif days_left <= 2:
            return "danger"
        elif days_left <= 5:
            return "warning"
        else:
            return "success"
    
    @property
    def deadline_text(self) -> str:
        """Текстовое описание дедлайна"""
        if self.is_done:
            return "Выполнено"
        if not self.deadline:
            return "Без дедлайна"
        
        from datetime import datetime
        days_left = (self.deadline.date() - datetime.utcnow().date()).days
        
        if days_left < 0:
            return f"Просрочено на {abs(days_left)} дн."
        elif days_left == 0:
            return "Уже сегодня!"
        elif days_left == 1:
            return "Уже завтра!"
        elif days_left <= 5:
            return f"Осталось {days_left} дн."
        else:
            return f"Дедлайн через {days_left} дн."
    
    # ========== МЕТОДЫ ==========
    
    def update_status_from_checkpoints(self, db):
        """Обновляет статус задачи на основе выполненных пунктов"""
        if self.checkpoints:
            all_done = all(cp.is_done for cp in self.checkpoints)
            if all_done and not self.is_done:
                self.is_done = True
                db.commit()
            elif not all_done and self.is_done:
                self.is_done = False
                db.commit()


class CheckPoint(Base):
    __tablename__ = 'checkpoints'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    is_done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    task = relationship('Task', back_populates='checkpoints')

class ArchivedTask(Base):
    __tablename__ = 'archived_tasks'

    id = Column(Integer, primary_key = True, index = True)
    original_id = Column(Integer, nullable = False)     # ID исходной задачи
    title = Column(String(200), nullable = False)
    deadline = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, default=datetime.utcnow)  
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    user = relationship('User')
