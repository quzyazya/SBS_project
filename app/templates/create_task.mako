<%inherit file="base.mako" />
<%def name="title()">Создать задачу - ProgressPal</%def>

<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h4 class="mb-0">➕ Создать задачу</h4>
            </div>
            <div class="card-body">
                <form method="post" action="/api/tasks-form">
                    <div class="mb-3">
                        <label class="form-label">Название</label>
                        <input type="text" name="title" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Описание</label>
                        <textarea name="content" class="form-control" rows="3"></textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Дедлайн</label>
                        <input type="date" name="deadline" class="form-control" value="${deadline or ''}" min="${today}">
                        % if deadline and deadline < today:
                            <small class="text-danger">✖️ Нельзя выбрать дату в прошлом</small>
                        % endif
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Создать</button>
                    <a href="/" class="btn btn-secondary w-100 mt-2">Отмена</a>
                </form>
            </div>
        </div>
    </div>
</div>