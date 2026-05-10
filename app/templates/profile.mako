<%inherit file='base.mako' />
<%def name='title()'>Профиль - ProgressPal</%def>

<div class='row justify-content-center'>
    <div class='col-md-6'>
        <div class='card'>
            <div class='card-header bg-primary text-white'>
                <h4 class='mb-0'>👤 Профиль</h4>
            </div>
            <div class='card-body'>
                <p><strong>Email:</strong> ${current_user.email}</p>
                <p><strong>Никнейм:</strong> ${current_user.username}</p>
                <p><strong>Телефон:</strong> ${current_user.phone or 'Не указан'}</p>
                <p><strong>Роль:</strong> ${'VIP' if current_user.role == 'vip' else 'Free'}</p>

                <hr>
                <h5>🔐 Двухфакторная аутентификация</h5>
                % if current_user.is_2fa_enabled:
                    <div class='alert alert-success'>☑️ 2FA включена</div>
                    <form method='post' action='/profile/disable-2fa'>
                        <button class='btn btn-danger'>Отключить 2FA</button>
                    </form>
                % else:
                    <div class='alert alert-info'>🚫 2FA выключена</div>
                    % if current_user.phone:
                        <form method='post' action='/profile/enable-2fa'>
                            <button class='btn btn-success'>Включить 2FA</button>
                        </form>
                    % else:
                        <div class='alert alert-warning'>Сначала укажите номер телефона</div>
                    % endif
                % endif
            </div>
        </div>
    </div>
</div>