<%inherit file="base.mako" />
<%def name="title()">Редактирование задачи - ProgressPal</%def>

<div class="row">
    <div class="col-md-8 mx-auto">
        <div class="card">
            <div class="card">
                <div class='card-header bg-warning text-white d-flex justify-content-between align-items-center'>
                    <h4 class="mb-0">✏️ Редактирование задачи</h4>
                    <div class='d-flex align-items-center gap-2'>
                        <div class='progress' style='width: 100px; heigth: 8px;'>
                            <div class='progress-bar bg-success' style='width: ${task.progress_percent}%'></div>
                        </div>
                        <span class='small text-white'>${task.progress_percent}%</span>
                    </div>
            </div>
            <div class="card-body">
                <form method="post" action='/api/tasks/${task.id}/edit-form'>
                    <div class="mb-3">
                        <label class="form-label">Название</label>
                        <input type="text" name="title" class="form-control" value="${task.title}" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Описание</label>
                        <textarea name="content" class="form-control" rows="3">${task.content or ''}</textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Дедлайн</label>
                        <input type="date" name="deadline" class="form-control" 
                               value="${task.deadline.strftime('%Y-%m-%d') if task.deadline else ''}">
                    </div>
                    <button type="submit" class="btn btn-primary w-100">💾 Сохранить</button>
                </form>

                <hr>
                <!-- Подзадачи (чекпоинты) -->
                <h5 class='mb-3'>📋 Пункты задачи</h5>
                <!-- Форма добавления нового пункта -->
                <form method='post' action='/api/tasks/${task.id}/checkpoint-form' class='mb-3'>
                    <div class='input-group input-group-sm'>
                        <input type='text' name='title' class='form-control' placeholder='Новый пункт...' required>
                        <button class='btn btn-outline-primary' type='submit'>+ Добавить пункт</button>
                    </div>
                </form>

                <!-- Список пунктов -->
                % if task.checkpoints:
                    <div class='list-group'>
                    % for cp in task.checkpoints:
                        <div class='list-group-item py-2'>
                            <div class='d-flex justify-content-between align-items-center'>
                                <div class='d-flex align-items-center gap-2'>
                                    % if cp.is_done:
                                        <form method='post' action='/api/checkpoints/${cp.id}/undo-form' style='display: inline;'>
                                            <button type='submit' class='btn btn-link p-0 text-decoration-none' style='font-size: 1.2rem;'>☑️</button>
                                        </form>
                                        <span class='text-decoration-line-through'>${cp.title}</span>
                                    % else:
                                        <form method='post' action='/api/checkpoints/${cp.id}/done-form' style='display: inline;'>
                                            <button type='submit' class='btn btn-link p-0 text-decoration-none' style='font-size: 1.2rem;'>◻️</button>
                                        </form>
                                        ${cp.title}
                                    % endif
                                </div>
                                <form method='post' action='/api/checkpoints/${cp.id}/delete-form' style='display: inline;'>
                                    <button class='btn btn-sm btn-outline-danger' title='Удалить пункт'>✗</button>
                                </form>
                            </div>
                        </div>
                    % endfor
                    </div>
                % else:
                    <div class='alert alert-info text-center py-2'>
                        📌 Нет пунктов. Добавьте первый, чтобы разбить задачу на этапы!
                    </div>
                % endif

                <hr>
                <a href='/' class='btn btn-secondary w-100'>← Вернуться к задачам</a>
            </div> 
        </div>
    </div>
</div>