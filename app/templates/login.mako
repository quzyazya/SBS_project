<%inherit file="base.mako" />
<%def name="title()">Вход - ProgressPal</%def>

<div class="row justify-content-center">
    <div class="col-md-5">
        <div class="card">
            <div class="card-header bg-primary text-white text-center">
                <h4 class="mb-0">🔐 Вход в систему</h4>
            </div>
            <div class="card-body">
                
                <!-- СООБЩЕНИЕ ОБ УСПЕШНОЙ СМЕНЕ ПАРОЛЯ -->
                % if request.query_params.get('success') == 'password_changed':
                    <div class="alert alert-success alert-dismissible fade show" role="alert">
                        ☑️ Вы успешно сменили пароль! Никому его не говорите.
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                % endif
                
                <!-- СООБЩЕНИЕ ОБ УСПЕШНОМ СБРОСЕ ПАРОЛЯ (если есть) -->
                % if request.query_params.get('reset') == 'success':
                    <div class="alert alert-success alert-dismissible fade show" role="alert">
                        ☑️ Пароль успешно изменён! Войдите с новым паролем.
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                % endif
                
                <form method="post" action="/auth/login-page">
                    <div class="mb-3">
                        <label for="username" class="form-label">Email</label>
                        <input type="email" class="form-control" id="username" name="username" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Пароль</label>
                        <input type="password" class="form-control" id="password" name="password" required>
                    </div>
                    <div class="mb-3 text-end">
                        <a href="/auth/forgot-password">Забыли пароль?</a>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Войти</button>
                </form>
                <hr>
                <p class="text-center mb-0">
                    Нет аккаунта? <a href="/auth/register-page">Зарегистрироваться</a>
                </p>
            </div>
        </div>
    </div>
</div>