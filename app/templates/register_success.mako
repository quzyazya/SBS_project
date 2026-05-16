<%inherit file="base.mako" />
<%def name="title()">Регистрация успешна - ProgressPal</%def>

<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-success text-white">
                <h4 class="mb-0">☑️ Регистрация успешна!</h4>
            </div>
            <div class="card-body text-center">
                <p>На ваш email <strong>${email}</strong> отправлено письмо с подтверждением.</p>
                <p>Перейдите по ссылке в письме, чтобы активировать аккаунт.</p>
                <p><small class="text-muted">Если письмо не пришло, проверьте папку Спам</small></p>
                
                <a href="/auth/login-page" class="btn btn-primary mt-3">Перейти ко входу</a>
            </div>
        </div>
    </div>
</div>