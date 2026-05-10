<%inherit file="base.mako" />
<%def name="title()">Регистрация - ProgressPal</%def>

<div class="row justify-content-center">
    <div class="col-md-6">
        <div class='card'>
            <div class='card-header bg-success text-white text-center'>
                <h4 class='mb-0'>📝 Регистрация</h4>
            </div>
            <div class='card-body'>
                <form method='post'>
                    <div class='mb-3'>
                        <label class='form-label'>Email</label>
                        <input type='email' name='email' class='form-control' required>
                    </div>
                    <div class='mb-3'>
                        <label class='form-label'>Никнейм</label>
                        <input type='text' name='username' class='form-control' required>
                    </div>
                    <div class='mb-3'>
                        <label class='form-label'>Телефон</label>
                        <input type='tel' name='phone' class='form-control' placeholder='+7XXXXXXXXXX'>
                    </div>
                    <div class='mb-3'>
                        <label class='form-label'>Пароль</label>
                        <input type='password' name='password' class='form-control' required>
                    </div>
                    <button type='submit' class='btn btn-success w-100'>Зарегистрироваться</button>
                </form>
                <hr>
                <p class='text-center mb-0'>
                    Уже есть аккаунт? <a href='/auth/login-page'>Войти</a>
                </p>
            </div>
        </div>
    </div>
</div>