<%inherit file='base.mako' />
<%def name='title()'>Восстановление пароля - ProgressPal</%def>

<div class='row justify-content-center'>
    <div class='col-md-6'>
        <div class='card'>
            <div class='card-header bg-warning text-dark'>
                <h4 class='mb-0'>🔐 Восстановление пароля</h4>
            </div>
            <div class='card-body'>
                % if error:
                    <div class='alert alert-danger'>${error}</div>
                % endif

                <p>Введите email, который вы использовали при регистрации. Мы отправим ссылку для сброса пароля.</p>
                
                <form method="post" action="/auth/forgot-password">
                    <div class="mb-3">
                        <label class="form-label">Email</label>
                        <input type="email" name="email" class="form-control" required>
                    </div>
                    <button type="submit" class="btn btn-warning w-100">Отправить ссылку</button>
                </form>
                
                <hr>
                <div class="text-center">
                    <a href="/auth/login-page">Вернуться ко входу</a>
                </div>
            </div>
        </div>
    </div>
</div>