<%inherit file="base.mako" />
<%def name="title()">Профиль - ProgressPal</%def>

<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h4 class="mb-0">👤 Профиль</h4>
            </div>
            <div class="card-body">
                <p><strong>Email:</strong> ${current_user.email}</p>
                <p><strong>Никнейм:</strong> ${current_user.username}</p>
                <p><strong>Роль:</strong> ${'VIP' if current_user.role == 'vip' else 'Free'}</p>
                
                <hr>
                
                <!-- ===== ПОДТВЕРЖДЕНИЕ EMAIL ===== -->
                <h5>📧 Подтверждение email</h5>
                % if current_user.is_email_verified:
                    <div class="alert alert-success">
                        ☑️ Email подтверждён
                    </div>
                % else:
                    <div class="alert alert-warning">
                        ⚠️ Email не подтверждён<br>
                        <small>Некоторые функции могут быть ограничены</small>
                    </div>
                    <form method="post" action="/profile/send-verification-email" class="mt-2">
                        <button class="btn btn-primary">📧 Отправить письмо для подтверждения</button>
                    </form>
                    <div class='alert alert-info mt-2'>
                        💡 <strong>Подтвердите email</strong>, чтобы обезопасить себя от таких явлений, как:<br>
                        • Смена пароля<br>
                        • Вход с нового устройства<br>
                        • Другие важные события
                    </div>
                % endif
                
                <hr>
                
                <!-- ===== ПОДТВЕРЖДЕНИЕ ТЕЛЕФОНА ===== -->
                <h5>📱 Двухфакторная аутентификация</h5>
                % if current_user.phone:
                    <div class="alert alert-success">
                        ☑️ Телефон подтверждён: ${current_user.phone}<br>
                        <small>Используется для двухфакторной аутентификации при входе</small>
                    </div>
                    <form method="post" action="/profile/remove-phone" class="mt-2">
                        <button class="btn btn-outline-danger btn-sm">Удалить телефон</button>
                    </form>
                % else:
                    <div class="alert alert-info">
                        🔐 Для включения двухфакторной аутентификации добавьте номер телефона.<br>
                        <small>На него будет приходить код подтверждения при входе в систему</small>
                    </div>
                    <form method="post" action="/profile/send-phone-code" class="mt-2">
                        <div class="input-group">
                            <input type="tel" name="phone" class="form-control" placeholder="+7XXXXXXXXXX" required>
                            <button class="btn btn-success">Добавить телефон</button>
                        </div>
                    </form>
                % endif
                
                <hr>
                
                <!-- ===== СМЕНА НИКНЕЙМА ===== -->
                <h5>✏️ Смена никнейма</h5>
                % if current_user.role == 'vip':
                    <div class="alert alert-info">⭐ VIP меняйте никнейм без ограничений</div>
                    <form method="post" action="/profile/change-username" class="mb-4">
                        <div class="input-group">
                            <input type="text" name="new_username" class="form-control" placeholder="Новый никнейм" required>
                            <button class="btn btn-warning">Изменить</button>
                        </div>
                    </form>
                % elif current_user.nickname_changed:
                    <div class="alert alert-warning">⚠️ Вы уже меняли никнейм. Эта возможность доступна только один раз.</div>
                % else:
                    <form method="post" action="/profile/change-username" class="mb-4">
                        <div class="input-group">
                            <input type="text" name="new_username" class="form-control" placeholder="Новый никнейм" required>
                            <button class="btn btn-warning">Изменить</button>
                        </div>
                    </form>
                % endif
                <!-- СМЕНА ПАРОЛЯ -->
                <h5>🔒 Смена пароля</h5>
                <a href='/profile/change-password' class='btn btn-outline-warning btn sm'>Сменить пароль</a>

                <!-- ТЕМНАЯ ТЕМА -->
                <h5>🌙 Оформление</h5>
                <form method='post' action='/profile/toggle-theme' class='mt-2'>
                    <button type='submit' class="btn ${'btn-dark' if current_user.dark_mode else 'btn-outline-secondary'}">
                        % if current_user.dark_mode:
                            ☀️ Светлая тема
                        % else:
                            🌙 Тёмная тема
                        % endif
                    </button>
                </form>        
                <hr>

            </div>
        </div>
    </div>
</div>

<!-- Сообщения об успехах и ошибках -->
% if request.query_params.get('success') == 'nickname_changed':
    <div class="alert alert-success alert-dismissible fade show fixed-bottom mx-auto" style="max-width: 500px; left: 0; right: 0;">☑️ Никнейм успешно изменён!<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>
% endif
% if request.query_params.get('success') == 'phone_added':
    <div class="alert alert-success alert-dismissible fade show fixed-bottom mx-auto" style="max-width: 500px; left: 0; right: 0;">☑️ Телефон подтверждён! Двухфакторная аутентификация включена.<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>
% endif
% if request.query_params.get('success') == 'phone_removed':
    <div class="alert alert-success alert-dismissible fade show fixed-bottom mx-auto" style="max-width: 500px; left: 0; right: 0;">☑️ Телефон удалён. Двухфакторная аутентификация отключена.<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>
% endif
% if request.query_params.get('success') == 'email_verified':
    <div class="alert alert-success alert-dismissible fade show fixed-bottom mx-auto" style="max-width: 500px; left: 0; right: 0;">☑️ Email успешно подтверждён!<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>
% endif
% if request.query_params.get('success') == 'verification_sent':
    <div class="alert alert-success alert-dismissible fade show fixed-bottom mx-auto" style="max-width: 500px; left: 0; right: 0;">📧 Письмо для подтверждения отправлено! Проверьте почту.<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>
% endif
% if request.query_params.get('error') == 'nickname_already_changed':
    <div class="alert alert-danger alert-dismissible fade show fixed-bottom mx-auto" style="max-width: 500px; left: 0; right: 0;">⚠️ Вы уже меняли никнейм!<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>
% endif
% if request.query_params.get('error') == 'nickname_taken':
    <div class="alert alert-danger alert-dismissible fade show fixed-bottom mx-auto" style="max-width: 500px; left: 0; right: 0;">⚠️ Такой никнейм уже занят!<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>
% endif
% if request.query_params.get('error') == 'already_verified':
    <div class="alert alert-warning alert-dismissible fade show fixed-bottom mx-auto" style="max-width: 500px; left: 0; right: 0;">
        ⚠️ Ваш email уже подтверждён
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
% endif

% if request.query_params.get('error') == 'email_send_failed':
    <div class="alert alert-danger alert-dismissible fade show fixed-bottom mx-auto" style="max-width: 500px; left: 0; right: 0;">
        ✖️ Не удалось отправить письмо. Проверьте правильность email или попробуйте позже.
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
% endif

% if request.query_params.get('error') == 'disable_2fa_first':
    <div class="alert alert-danger alert-dismissible fade show fixed-bottom mx-auto" style="max-width: 500px; left: 0; right: 0;">
        ⚠️ Сначала отключите 2FA в настройках!
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
% endif

% if request.query_params.get('error') == 'invalid_code':
    <div class="alert alert-danger alert-dismissible fade show fixed-bottom mx-auto" style="max-width: 500px; left: 0; right: 0;">
        ⚠️ Неверный код подтверждения!
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
% endif

% if request.query_params.get('error') == 'sms_failed':
    <div class="alert alert-danger alert-dismissible fade show fixed-bottom mx-auto" style="max-width: 500px; left: 0; right: 0;">
        ⚠️ Не удалось отправить SMS. Попробуйте позже.
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
% endif