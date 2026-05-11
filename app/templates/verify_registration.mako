<%inherit file="base.mako" />
<%def name="title()">Подтверждение телефона - ProgressPal</%def>

<div class="row justify-content-center">
    <div class="col-md-5">
        <div class="card">
            <div class="card-header bg-warning text-dark text-center">
                <h4 class="mb-0">📱 Подтверждение телефона</h4>
            </div>
            <div class="card-body">
                <p class="text-center">Код подтверждения отправлен на ваш телефон</p>
                
                <form method="post" action="/auth/verify-registration">
                    <input type="hidden" name="email" value="${email or ''}">
                    <input type="hidden" name="username" value="${username or ''}">
                    <input type="hidden" name="phone" value="${phone or ''}">
                    <input type="hidden" name="password" value="${password or ''}">
                    
                    <div class="mb-3">
                        <label class="form-label">Код из SMS</label>
                        <input type="text" name="code" class="form-control" placeholder="000000" required>
                    </div>
                    % if error:
                        <div class="alert alert-danger">${error}</div>
                    % endif
                    <button type="submit" class="btn btn-primary w-100">Подтвердить и завершить регистрацию</button>
                </form>
            </div>
        </div>
    </div>
</div>