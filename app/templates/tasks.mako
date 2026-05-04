<%inherit file="base.mako" />
<%def name="title()">Мои задачи - ProgressPal</%def>

<!-- Глобальный прогресс -->
<div class="card mb-4">
    <div class="card-body">
        <h5 class="card-title">🎯 Общий прогресс по всем задачам</h5>
        <div class="progress" style="height: 35px;">
            <div class="progress-bar bg-success progress-bar-striped" style="width: ${stats['percent']}%">
                ${stats['percent']}%
            </div>
        </div>
        <div class="row mt-3 text-center">
            <div class="col">
                <h4>${stats['total_tasks']}</h4>
                <small class="text-muted">Всего задач</small>
            </div>
            <div class="col">
                <h4 class="text-success">${stats['done_tasks']}</h4>
                <small class="text-muted">Выполнено задач|пунктов</small>
            </div>
            <div class="col">
                <h4 class="text-warning">${stats['total_checkpoints']}</h4>
                <small class="text-muted">Всего пунктов</small>
            </div>
        </div>
    </div>
</div>

% if request.query_params.get('payment') == 'success':
    <div class="alert alert-success alert-dismissible fade show" role="alert">
        🎉 Поздравляем! Вы успешно приобрели VIP статус. Теперь вам доступны неограниченные закрепления задач.
        <button type='button' class="btn-close" data-bs-dismiss='alert'></button>
    </div>
% endif
% if request.query_params.get('payment') == 'canceled':
    <div class='alert alert-warning alert-dismissible fade show' role='alert'>
        Оплата отменена. Вы можете попробовать снова в любое время.
        <button type='button' class='btn-close' data-bs-dismiss="alert"></button>
    </div>
% endif

<!-- Сообщение об ошибке лимита закрепления -->
% if request.query_params.get('error') == 'star_limit':
    <div class="alert alert-warning alert-dismissible fade show" role="alert">
        ⚠️ Бесплатный тариф позволяет закрепить только 3 задачи. Повысьте статус до VIP, чтобы снять ограничения.
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
% endif

<!-- Блок тарифной карточки -->
<div class="card mb-4">
    <div class="card-body">
        <div class="d-flex justify-content-between align-items-center">
            <div>
                <strong>👑 Ваш тариф:</strong>
                % if current_user.role == 'vip':
                    <span class="badge bg-warning">VIP</span> — безлимитные задачи
                % else:
                    <span class="badge bg-secondary">Free</span> — до 3 закреплённых задач
                % endif
            </div>
            % if current_user.role != 'vip':
                <a href="/upgrade-page" class="btn btn-sm btn-warning">⬆️ Upgrade to VIP</a>
            % endif
        </div>
        
        % if current_user.role != 'vip':
            <div class="progress mt-2" style="height: 10px;">
                <div class="progress-bar bg-info" style="width: ${(stats['starred_count'] / 3 * 100)}%">
                </div>
            </div>
            <small class="text-muted">Закреплено ${stats['starred_count']} из 3 задач</small>
        % endif
        
    </div>
</div>

<!-- Форма создания задачи -->
<div class="card mb-4">
    <div class="card-header bg-primary text-white">
        <h5 class="mb-0">➕ Новая задача</h5>
    </div>
    <div class="card-body">
        <form method="post" action="/api/tasks-form">
            <div class="row g-2">
                <div class="col-md-5">
                    <input type="text" class="form-control" name="title" placeholder="Название задачи" required>
                </div>
                <div class="col-md-4">
                    <textarea class="form-control" name="content" placeholder="Описание (необязательно)" rows="1"></textarea>
                </div>
                <div class="col-md-2">
                    <input type="date" class="form-control" name="deadline">
                </div>
                <div class="col-md-1">
                    <button type="submit" class="btn btn-primary w-100">➕</button>
                </div>
            </div>
        </form>
    </div>
</div>

<!-- Список задач -->
<div class="card">
    <div class="card-header">
        <h5 class="mb-0">📝 Мои задачи</h5>
    </div>
    <div class="list-group list-group-flush">
        % for idx, task in enumerate(tasks):
        <div class="list-group-item">
            <!-- Заголовок задачи -->
            <div class="row align-items-center mb-2">
                <div class="col-md-8">
                    <h5 class="mb-0">
                        <span class="badge bg-secondary me-2">#${idx + 1}</span>
                        <span class="badge bg-${task.deadline_color} me-2">●</span>
                        ${task.title}
                    </h5>
                    % if task.content:
                        <small class="text-muted d-block mt-1">📝 ${task.content}</small>
                    % endif
                    
                    % if task.is_done:
                        <small class="text-success d-block">
                            ✅ Решена: ${task.created_at.strftime('%d.%m.%Y %H:%M')}
                        </small>
                    % elif task.deadline:
                        <small class="text-${task.deadline_color} d-block">
                            📅 ${task.deadline.strftime('%d.%m.%Y')} — ${task.deadline_text}
                        </small>
                    % endif
                    
                    <small class="text-muted d-block">
                        🕒 Создана: ${task.created_at.strftime('%d.%m.%Y %H:%M')}
                    </small>
                </div>
                <!-- КНОПКИ ДЕЙСТВИЙ -->
                <div class="col-md-4 text-end">
                    <!-- Кнопка закладки (избранное) -->
                    <form method="post" action="/api/tasks/${task.id}/star-form" style="display: inline;">
                        <button class="btn btn-sm ${'btn-warning' if task.is_starred else 'btn-outline-secondary'}" title="В избранное">
                            % if task.is_starred:
                                ⭐
                            % else:
                                ☆
                            % endif
                        </button>
                    </form>
                    <!-- Кнопка редактирования -->
                    <a href="/api/tasks/${task.id}/edit-form" class="btn btn-sm btn-warning" title="Редактировать">✏️</a>
                    <!-- Кнопка удаления -->
                    <form method="post" action="/api/tasks/${task.id}/delete-form" style="display: inline;">
                        <button class="btn btn-sm btn-danger" title="Удалить задачу">🗑</button>
                    </form>
                </div>
            </div>
            
            <!-- Прогресс-бар задачи -->
            <div class="progress mb-2" style="height: 20px;">
                <div class="progress-bar bg-info" style="width: ${task.progress_percent}%">
                    ${task.progress_percent}%
                </div>
            </div>
            
            <!-- Только для НЕвыполненных задач -->
            % if not task.is_done:
                <!-- Форма добавления пункта -->
                <form method="post" action="/api/tasks/${task.id}/checkpoints-form" class="mb-2">
                    <div class="input-group input-group-sm">
                        <input type="text" class="form-control" name="title" placeholder="Новый пункт..." required>
                        <button class="btn btn-outline-primary" type="submit">+ Добавить пункт</button>
                    </div>
                </form>
                
                <!-- Кнопка "Завершить задачу" (если нет пунктов) -->
                % if not task.checkpoints:
                    <form method="post" action="/api/tasks/${task.id}/done-form" class="mb-2">
                        <button class="btn btn-sm btn-success w-100">✅ Завершить задачу</button>
                    </form>
                % endif
                
                <!-- Сообщение "Нет пунктов" -->
                % if not task.checkpoints:
                    <small class="text-muted ms-3">📌 Нет пунктов. Добавьте первый, чтобы разбить задачу на этапы!</small>
                % endif
                
                <!-- Подсказка (если есть пункты) -->
                % if task.checkpoints:
                    <div class="alert alert-info mb-2 text-center py-1 small">
                        📋 Управляйте выполнением через пункты ниже
                    </div>
                % endif
            % endif
            
            <!-- Список пунктов -->
            % if task.checkpoints:
                <div class="list-group list-group-flush ms-3">
                % for cp in task.checkpoints:
                    <div class="d-flex justify-content-between align-items-center py-1">
                        <div>
                            % if cp.is_done:
                                <form method="post" action="/api/checkpoints/${cp.id}/undo-form" style="display: inline;">
                                    <button type="submit" class="btn btn-link p-0 text-decoration-none" style="font-size: 1.2rem;">☑️</button>
                                </form>
                                <span class="text-decoration-line-through">${cp.title}</span>
                            % else:
                                <form method="post" action="/api/checkpoints/${cp.id}/done-form" style="display: inline;">
                                    <button type="submit" class="btn btn-link p-0 text-decoration-none" style="font-size: 1.2rem;">◻️</button>
                                </form>
                                ${cp.title}
                            % endif
                        </div>
                        <form method="post" action="/api/checkpoints/${cp.id}/delete-form" style="display: inline;">
                            <button class="btn btn-sm btn-outline-danger" title="Удалить пункт">✗</button>
                        </form>
                    </div>
                % endfor
                </div>
            % endif
            
            <!-- Сообщение о выполнении задачи (с кнопкой отката) -->
            % if task.is_done:
                <div class="alert alert-success mb-0 mt-2 text-center py-1 d-flex justify-content-between align-items-center">
                    <span>✅ Задача выполнена!</span>
                    <form method="post" action="/api/tasks/${task.id}/undo-form" style="display: inline;">
                        <button class="btn btn-sm btn-warning" title="Откатить выполнение">↩️ Откатить</button>
                    </form>
                </div>
            % endif
        </div>
        % else:
        <div class="list-group-item text-center text-muted">
            🎉 У вас пока нет задач. Создайте первую!
        </div>
        % endfor
    </div>
</div>