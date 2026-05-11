<%inherit file="base.mako" />
<%def name="title()">Мои задачи - ProgressPal</%def>

<!-- КАЛЕНДАРЬ (плавающий справа) -->
<div style="position: fixed; right: 20px; top: 100px; width: 320px; z-index: 1000;">
    <div class="card shadow-sm">
        <div class="card-header bg-danger text-white d-flex justify-content-between align-items-center" style='background-color: #e83e8c !important;'>
            <h6 class="mb-0">🗓️ Календарь дедлайнов</h6>
            <button id="searchToggleBtn" style="background: none; border: none; color: white; cursor: pointer;">🔍</button>
        </div>
        
        <!-- ВСПЛЫВАЮЩАЯ ПАНЕЛЬ ПОИСКА -->
        <div id="searchPanel" style="display: none; padding: 10px; border-bottom: 1px solid #e9ecef;">
            <form method="get" action="/" style="margin-bottom: 0;">
                <div class="input-group input-group-sm">
                    <input type="text" name="search" class="form-control" placeholder="Название задачи..." value="${request.query_params.get('search', '')}">
                    <button class="btn btn-primary" type="submit">Найти</button>
                </div>
            </form>
            
            % if search_query:
                <div class="mt-2">
                    <small class="text-muted">Результаты:</small>
                    <ul class="list-unstyled mt-1 mb-0 small">
                        % for t in tasks:
                            % if search_query.lower() in t['title'].lower():
                                <%
                                    # Берём порядковый номер из словаря, если нет — используем ID
                                    task_number = task_number_map.get(t['id'], t['id'])
                                %>
                                <li>
                                    <a href="/api/tasks/${t['id']}/edit-form">#${task_number} ${t['title'][:30]}</a>
                                    % if t['deadline']:
                                        <span class="text-muted"> — ${t['deadline'].strftime('%d.%m.%Y')}</span>
                                    % endif
                                </li>
                            % endif
                        % endfor
                    </ul>
                    % if not any(search_query.lower() in t['title'].lower() for t in tasks):
                        <div class="alert alert-warning py-1 mt-1 small">Задачи не найдены</div>
                    % endif
                </div>
            % endif
        </div>
        
        <div class="card-body p-2">
            % if calendar_data:
                <%namespace name="calendar" file="calendar.mako" />
                ${calendar.render_calendar(calendar_data, current_user, calendar_year, calendar_month)}
            % else:
                <div class='text-center text-muted p-3'>
                    🔒 Календарь доступен только VIP пользователям
                    <a href='/upgrade-page' class='btn btn-sm btn-warning mt-2 d-block'>🔝 Upgrade to VIP</a>
                </div>
            % endif
        </div>
    </div>
</div>

<!-- ОСНОВНОЙ БЛОК -->
<div class="container" style="max-width: 1000px; margin: 0 auto;">
    
    <!-- Глобальный прогресс -->
    <div class="card mb-4">
        <div class="card-body">
            <h5 class="card-title text-center mb-3">🎯 Общий прогресс</h5>
            <div class="progress" style="height: 35px; border-radius: 20px;">
                <div class="progress-bar bg-success progress-bar-striped progress-bar-animated" style="width: ${stats['percent']}%">
                    ${stats['percent']}%
                </div>
            </div>
            
            <div class="row mt-4 g-3">
                <div class="col-md-4 col-12">
                    <div class="card text-center border-primary h-100">
                        <div class="card-body py-3 d-flex flex-column justify-content-center" style="min-height: 120px;">
                            <span style="font-size: 2rem;">📋</span>
                            <h3 class="mb-0 mt-2">${stats['total_tasks']}</h3>
                            <small class="text-muted">Всего задач</small>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4 col-12">
                    <div class="card text-center h-100">
                        <div class="row g-0 h-100">
                            <div class="col-6 border-end d-flex flex-column justify-content-center">
                                <div class="py-2">
                                    <span style="font-size: 1.8rem;">☑️</span>
                                    <h4 class="mb-0 text-success">${stats['done_tasks']}</h4>
                                    <small class="text-muted">Выполнено</small>
                                </div>
                            </div>
                            <div class="col-6 d-flex flex-column justify-content-center">
                                <div class="py-2">
                                    <span style="font-size: 1.8rem;">✏️</span>
                                    <h4 class="mb-0 text-warning">${stats['active_tasks']}</h4>
                                    <small class="text-muted">Активных</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4 col-12">
                    <div class="card text-center border-warning h-100">
                        <div class="card-body py-3 d-flex flex-column justify-content-center" style="min-height: 120px;">
                            <span style="font-size: 2rem;">📌</span>
                            <h3 class="mb-0 mt-2">${stats['starred_count']}</h3>
                            <small class="text-muted">Закреплено</small>
                            % if current_user.role != 'vip':
                                <div class="progress mt-2" style="height: 6px; border-radius: 3px;">
                                    <div class="progress-bar bg-warning" style="width: ${(stats['starred_count'] / 3 * 100)}%"></div>
                                </div>
                                <small class="text-muted">🔒Лимит: 3</small>
                            % endif
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-3 g-3">
                <div class="col-md-4 col-12">
                    <div class="card text-center border-info h-100">
                        <div class="card-body py-3 d-flex flex-column justify-content-center" style="min-height: 120px;">
                            <span style="font-size: 2rem;">📃</span>
                            <h3 class="mb-0 mt-2">${stats['total_checkpoints']}</h3>
                            <small class="text-muted">Всего пунктов</small>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4 col-12">
                    <div class="card text-center h-100">
                        <div class="row g-0 h-100">
                            <div class="col-6 border-end d-flex flex-column justify-content-center">
                                <div class="py-2">
                                    <span style="font-size: 1.8rem;">☑️</span>
                                    <h4 class="mb-0 text-success">${stats['done_checkpoints']}</h4>
                                    <small class="text-muted">Выполнено</small>
                                </div>
                            </div>
                            <div class="col-6 d-flex flex-column justify-content-center">
                                <div class="py-2">
                                    <span style="font-size: 1.8rem;">⏳</span>
                                    <h4 class="mb-0 text-warning">${stats['active_checkpoints']}</h4>
                                    <small class="text-muted">Активных</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4 col-12">
                    <div class="card text-center border-danger h-100">
                        <div class="card-body py-3 d-flex flex-column justify-content-center" style="min-height: 120px;">
                            <span style="font-size: 2rem;">📉</span>
                            <h3 class="mb-0 mt-2 text-danger">${stats['overdue_tasks_count']}</h3>
                            <small class="text-muted">Просроченных задач</small>
                            % if stats['overdue_tasks_count'] > 0:
                                <small class="text-danger mt-1">‼️ Требуют внимания  ‼️</small>
                            % endif
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    % if request.query_params.get('error') == 'past_deadline':
        <div class='alert alert-danger alert-dismissible fade show' role='alert'>
            ✖️ Нельзя создать задачу с дедлайном в прошлом!
            <button type='button' class='btn-close' data-bs'dismiss='alert'></button>
        </div>
    % endif
    
    <!-- Сообщения и тарифная карточка (без изменений) -->
    % if request.query_params.get('payment') == 'success':
        <div class="alert alert-success alert-dismissible fade show" role="alert">🎉 Поздравляем! Вы успешно приобрели VIP статус.<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>
    % endif
    % if request.query_params.get('payment') == 'canceled':
        <div class="alert alert-warning alert-dismissible fade show" role="alert">Оплата отменена. Вы можете попробовать снова.<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>
    % endif
    % if request.query_params.get('error') == 'star_limit':
        <div class="alert alert-warning alert-dismissible fade show" role="alert">⚠️ Бесплатный тариф позволяет закрепить только 3 задачи.<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>
    % endif
    
    <div class="card mb-4">
        <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
                <div><strong>🪙 Ваш тариф:</strong>
                % if current_user.role == 'vip':
                    <span class="badge bg-warning">VIP</span> — безлимитные задачи
                % else:
                    <span class="badge bg-secondary">Free</span> — до 3 закреплённых задач
                % endif
                </div>
                % if current_user.role != 'vip':
                    <a href="/upgrade-page" class="btn btn-sm btn-warning">🔝 Upgrade to VIP</a>
                % endif
            </div>
            % if current_user.role != 'vip':
                <div class="progress mt-2" style="height: 10px;">
                    <div class="progress-bar bg-info" style="width: ${(stats['starred_count'] / 3 * 100)}%"></div>
                </div>
                <small class="text-muted">Закреплено ${stats['starred_count']} из 3 задач</small>
            % endif
        </div>
    </div>
    
    <!-- Форма создания задачи -->
    <div class="card mb-4">
        <div class="card-header bg-primary text-white"><h5 class="mb-0">➕ Новая задача</h5></div>
        <div class="card-body">
            <form method="post" action="/api/tasks-form">
                <div class="row g-2">
                    <div class="col-md-5"><input type="text" class="form-control" name="title" placeholder="Название задачи" required></div>
                    <div class="col-md-4"><textarea class="form-control" name="content" placeholder="Описание (необязательно)" rows="1"></textarea></div>
                    <div class="col-md-2"><input type="date" class="form-control" name="deadline"></div>
                    <div class="col-md-1"><button type="submit" class="btn btn-primary w-100">➕</button></div>
                </div>
            </form>
        </div>
    </div>
    
    <!-- Список задач -->
    <div class="card">
        <div class="card-header"><h5 class="mb-0">📝 Мои задачи</h5></div>
        <div class="list-group list-group-flush">
            % for idx, task in enumerate(tasks):
            <div class="list-group-item">
                <div class="row align-items-center mb-2">
                    <div class="col-md-8">
                        <div class="d-flex align-items-center gap-2 mb-1">
                            <span class="badge bg-secondary">#${task['number']}</span>
                            <span class="badge bg-${task['deadline_color']}">●</span>
                            <strong class="flex-grow-1">${task['title']}</strong>
                            <div class="progress" style="width: 80px; height: 8px;">
                                <div class="progress-bar bg-success" style="width: ${task['progress_percent']}%"></div>
                            </div>
                            <span class="small text-muted">${task['progress_percent']}%</span>
                        </div>
                        
                        % if task['content']:
                            <small class="text-muted d-block mt-1 ms-2">📝 ${task['content']}</small>
                        % endif
                        
                        % if task['is_done']:
                            <small class="text-success d-block ms-2">☑️ Решена: ${task['created_at'].strftime('%d.%m.%Y %H:%M')}</small>
                        % elif task['deadline']:
                            <small class="text-${task['deadline_color']} d-block ms-2">
                                📅 ${task['deadline'].strftime('%d.%m.%Y')} — ${task['deadline_text']}
                            </small>
                        % endif
                        
                        <small class="text-muted d-block ms-2">🕒 Создана: ${task['created_at'].strftime('%d.%m.%Y %H:%M')}</small>
                     </div>
                    <div class="col-md-4 text-end">
                        <form method="post" action="/api/tasks/${task['id']}/star-form" style="display: inline;">
                            <button class="btn btn-sm ${'btn-warning' if task['is_starred'] else 'btn-outline-secondary'}">
                                % if task['is_starred']:
                                ⭐ 
                                % else: 
                                ☆ 
                                % endif
                            </button>
                        </form>
                        <a href="/api/tasks/${task['id']}/edit-form" class="btn btn-sm btn-warning">✏️</a>
                        <form method="post" action="/api/tasks/${task['id']}/delete-form" style="display: inline;">
                            <button class="btn btn-sm btn-danger">🗑</button>
                        </form>
                    </div>
                </div>
                
                <!-- Только для НЕвыполненных задач (форма добавления пунктов) -->
                % if not task['is_done']:
                    <form method="post" action="/api/tasks/${task['id']}/checkpoints-form" class="mb-2">
                        <div class="input-group input-group-sm">
                            <input type="text" class="form-control" name="title" placeholder="Новый пункт..." required>
                            <button class="btn btn-outline-primary" type="submit">+ Добавить пункт</button>
                        </div>
                    </form>
                    
                    % if not task['checkpoints']:
                        <form method="post" action="/api/tasks/${task['id']}/done-form" class="mb-2">
                            <button class="btn btn-sm btn-success w-100">☑️ Завершить задачу</button>
                        </form>
                        <small class="text-muted ms-3">📌 Нет пунктов. Добавьте первый!</small>
                    % endif
                    
                    % if task['checkpoints']:
                        <div class="alert alert-info mb-2 text-center py-1 small">📋 Управляйте выполнением через пункты ниже</div>
                    % endif
                % endif
                
                <!-- Список пунктов -->
                % if task['checkpoints']:
                    <div class="list-group list-group-flush ms-3">
                    % for cp in task['checkpoints']:
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
                                <button class="btn btn-sm btn-outline-danger">✗</button>
                            </form>
                        </div>
                    % endfor
                    </div>
                % endif
                
                % if task['is_done']:
                    <div class="alert alert-success mb-0 mt-2 text-center py-1 d-flex justify-content-between align-items-center">
                        <span>☑️ Задача выполнена!</span>
                        <form method="post" action="/api/tasks/${task['id']}/undo-form" style="display: inline;">
                            <button class="btn btn-sm btn-warning">🔙 Откатить</button>
                        </form>
                    </div>
                % endif
            </div>
            % else:
            <div class="list-group-item text-center text-muted">🎉 У вас пока нет задач. Создайте первую!</div>
            % endfor
        </div>
    </div>
</div>

<script>
    const searchToggleBtn = document.getElementById('searchToggleBtn');
    const searchPanel = document.getElementById('searchPanel');
    let searchVisible = false;
    if (searchToggleBtn) {
        searchToggleBtn.addEventListener('click', function() {
            searchPanel.style.display = searchVisible ? 'none' : 'block';
            searchVisible = !searchVisible;
        });
    }
</script>