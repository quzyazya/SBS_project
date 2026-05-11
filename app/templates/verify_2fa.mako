<%inherit file="base.mako" />
<%def name="title()">Подтверждение 2FA - ProgressPal</%def>

<div class="row justify-content-center">
    <div class="col-md-5">
        <div class="card">
            <div class="card-header bg-warning text-dark text-center">
                <h4 class="mb-0">🔐 Подтверждение 2FA</h4>
            </div>
            <div class="card-body">
                <p class="text-center">Код подтверждения отправлен на ваш телефон</p>
                <form method="post" action="/profile/verify-2fa">
                    <div class="mb-3">
                        <label class="form-label">Код из SMS</label>
                        <input type="text" name="code" class="form-control" placeholder="000000" required>
                    </div>
                    % if request.query_params.get('error') == 'invalid_code':
                        <div class="alert alert-danger">Неверный код подтверждения</div>
                    % endif
                    <button type="submit" class="btn btn-primary w-100">Подтвердить и включить</button>
                </form>
            </div>
        </div>
    </div>
</div>