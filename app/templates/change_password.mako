<%inherit file="base.mako" />
<%def name="title()">Смена пароля - ProgressPal</%def>

<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-warning text-dark">
                <h4 class="mb-0">🔒 Смена пароля</h4>
            </div>
            <div class="card-body">
                % if error:
                    <div class="alert alert-danger">${error}</div>
                % endif
                
                <form method="post" action="/profile/change-password">
                    <div class="mb-3">
                        <label class="form-label">Старый пароль</label>
                        <input type="password" name="old_password" class="form-control" required>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">Новый пароль</label>
                        <input type="password" name="new_password" class="form-control" required>
                        <small class="text-muted">Минимум 6 символов</small>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">Подтвердите новый пароль</label>
                        <input type="password" name="confirm_password" class="form-control" required>
                    </div>
                    
                    <button type="submit" class="btn btn-warning w-100">Сменить пароль</button>
                </form>
            </div>
        </div>
    </div>
</div>