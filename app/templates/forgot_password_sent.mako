<%inherit file='base.mako' />
<%def name='title()'>Письмо отправлено - ProgressPal</%def>

<div class='row justify-content-center'>
    <div class='col-md-6'>
        <div class='card'>
            <div class='card-header bg-success text-white'>
                <h4 class='mb-0'>📧 Письмо отправлено!</h4>
            </div>
            <div class='card-body text-center'>
                <p>Мы отправили ссылку для восстановления пароля на <strong>${email}</strong>.</p>
                <p>Если письмо не пришло через несколько минут, проверьте папку <strong>Спам</strong>.</p>
                <a href='/auth/login-page' class='btn btn-primary mt-3'>Вернуться ко входу</a>
            </div>
        </div>
    </div>
</div>
    