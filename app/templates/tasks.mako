<%inherit file="base.mako" />
<%def name="title()">Мои задачи - ProgressPal</%def>

<div class="card mb-4">
    <div class="card-body">
        <h5 class="card-title">🎯 Прогресс</h5>
        <div class="progress" style="height: 35px;">
            <div class="progress-bar bg-success progress-bar-striped progress-bar-animated" 
                 style="width: ${stats['percent']}%">
                ${stats['percent']}%
            </div>
        </div>
        <div class="row mt-3 text-center">
            <div class="col">
                <h4>${stats['tasks_quantity']}</h4>
                <small class="text-muted">Всего задач</small>
            </div>
            <div class="col">
                <h4 class="text-success">${stats['done_tasks']}</h4>
                <small class="text-muted">Выполнено</small>
            </div>
            <div class="col">
                <h4 class="text-warning">${stats['pending_tasks']}</h4>
                <small class="text-muted">Активных</small>
            </div>
        </div>
    </div>
</div>

<div class="card mb-4">
    <div class="card-header bg-primary text-white">
        <h5 class="mb-0">➕ Новая задача</h5>
    </div>
    <div class="card-body">
        <form method="post" action="/api/tasks-form">
            <div class="row g-2">
                <div class="col-md-7">
                    <input type="text" class="form-control" name="title" placeholder="Название задачи" required>
                </div>
                <div class="col-md-3">
                    <input type="datetime-local" class="form-control" name="deadline">
                </div>
                <div class="col-md-2">
                    <button type="submit" class="btn btn-primary w-100">➕ Добавить</button>
                </div>
            </div>
        </form>
    </div>
</div>

<div class="card">
    <div class="card-header">
        <h5 class="mb-0">📝 Мои задачи</h5>
    </div>
    <div class="list-group list-group-flush">
        % for task in tasks:
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-7">
                    % if task['is_done']:
                        <span class="task-done">${task['title']}</span>
                    % else:
                        <strong>${task['title']}</strong>
                    % endif
                    % if task['deadline']:
                        <br><small class="text-muted">📅 ${task['deadline'].replace('T', ' ').split('.')[0][:16]}</small>
                    % endif
                </div>
                <div class="col-md-5 text-end">
                    % if not task['is_done']:
                    <form method="post" action="/api/tasks/${task['id']}/done-form" style="display: inline;">
                        <button class="btn btn-sm btn-success" title="Выполнить">✓ Выполнить</button>
                    </form>
                    % endif
                    <form method="post" action="/api/tasks/${task['id']}/delete-form" style="display: inline;">
                        <button class="btn btn-sm btn-danger" title="Удалить">✗ Удалить</button>
                    </form>
                </div>
            </div>
        </div>
        % else:
        <div class="list-group-item text-center text-muted">
            🎉 У вас пока нет задач. Создайте первую!
        </div>
        % endfor
    </div>
</div>