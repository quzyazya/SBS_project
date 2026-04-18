from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import uvicorn

app = FastAPI(title = 'SBS', description = 'Task tracker with progress bar')

# Хранилище задач / Storage of the tasks
tasks_db = []
task_counter = 1

# Модель для создания задачи (Pydantic) / Model for create task
class TaskCreate(BaseModel):
    title: str
    content: Optional[str] = None
    deadline: Optional[datetime] = None

# Модель для ответа (что возвращаем клиенту) / Model for answer (what returns to client)
class TaskResponse(BaseModel):
    id: int
    title: str
    content: Optional[str]
    deadline: Optional[datetime]
    is_done: bool
    created_at: datetime


# ЭНДПОИНТЫ (РУЧКИ) / ENDPOINTS (ROOTS)

@app.post('/tasks', response_model = TaskResponse)
async def create_task(task: TaskCreate):
    global task_counter

    new_task = {
        'id': task_counter,
        'title': task.title,
        'content': task.content,
        'deadline': task.deadline,
        'is_done': False,
        'created_at': datetime.now()
    }

    tasks_db.append(new_task)
    task_counter += 1
    return new_task

# Получить все задачи / Get all tasks 
@app.get('/tasks', response_model = List[TaskResponse])
async def get_all_tasks():
    return tasks_db

# Получить одну задачу по ID / Get one task by ID
@app.get('/tasks/{task_id}', response_model = TaskResponse)
async def get_task(task_id: int):
    for task in tasks_db:
        if task['id'] == task_id:
            return task
    raise HTTPException(status_code = 404, detail = 'Task not found. Please check the correctness of the ID.')

# Обновить задачу / Update task
@app.put('/tasks/{task_id}', response_model = TaskResponse)
async def update_task(task_id: int, task_update: TaskCreate):
    for task in tasks_db:
        if task['id'] == task_id:
            task['title'] = task_update.title
            task['content'] = task_update.content
            task['deadline'] = task_update.deadline
            return task
    raise HTTPException(status_code = 404, detail = 'Task not found. Please check the correctness of the ID.')
    
# Отметить задачу выполненной / Mark the task as completed
@app.patch('/tasks/{task_id}/done')
async def mark_done(task_id: int):
    for task in tasks_db:
        if task['id'] == task_id:
            task['is_done'] = True
            return {'message': f'Task {task_id} marked as done.'}
    raise HTTPException(status_code = 404, detail = 'Task not found. Please check the correctness of the ID.')
    
# Удалить задачу / Delete task
@app.delete('/tasks/{task_id}', response_model = TaskResponse)
async def delete_task(task_id: int):
    global tasks_db
    for task_number, task in enumerate(tasks_db):
        if task['id'] == task_id:
            tasks_db.pop(task_number)
            return {'message': f'Task {task_id} successfully deleted.'}
    raise HTTPException(status_code = 404, detail = 'Task not found. Please check the correctness of the ID.')

# Статистика (прогресс) / Statistic (progress)
@app.get('/stats')
async def get_stats():
    tasks_quantity = len(tasks_db)
    done_tasks = sum(1 for task in tasks_db if task['is_done'])
    percent = (done_tasks / tasks_quantity * 100) if tasks_quantity > 0 else 0 
    tasks_with_deadline = [task for task in tasks_db if task.get('deadline') is not None]
    most_priority = min(tasks_with_deadline, key = lambda tsk: tsk['deadline'] if tasks_with_deadline else None)
    return {
        'tasks_quantity': tasks_quantity,
        'done_tasks': done_tasks,
        'pending_tasks': tasks_quantity - done_tasks,
        'percent': f'{round(percent, 1)}%',
        'most_priority': most_priority
    }

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)





























