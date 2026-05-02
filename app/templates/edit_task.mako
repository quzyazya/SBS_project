<%inherit file="base.mako" />
<%def name="title()">Редактирование задачи - ProgressPal</%def>

<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-warning text-white">
                <h4 class="mb-0">✏️ Редактирование задачи</h4>
            </div>
            <div class="card-body">
                <form method="post">
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
                    <a href="/" class="btn btn-secondary w-100 mt-2">Отмена</a>
                </form>
            </div>
        </div>
    </div>
</div>