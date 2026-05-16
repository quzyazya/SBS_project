<%inherit file="base.mako" />
<%def name="title()">Подтверждение email - ProgressPal</%def>

<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h4 class="mb-0">📧 Подтверждение email</h4>
            </div>
            <div class="card-body text-center">
                <div class="alert alert-info">
                    <strong>Письмо отправлено!</strong><br>
                    На ваш email <strong>${email}</strong> отправлено письмо с ссылкой для подтверждения.
                </div>
                <p>Пожалуйста, перейдите по ссылке в письме, чтобы подтвердить свой email.</p>
                <p><small class="text-muted">Если письмо не пришло через несколько минут, проверьте папку Спам.</small></p>
                
                <div class="text-center mt-3 mb-3">
                    <div id="countdown" class="alert alert-secondary">
                        ⏳ Повторная отправка будет доступна через <span id="timer">02:00</span>
                    </div>
                    <form id="resendForm" method="post" action="/profile/resend-verification-email" style="margin-top: 15px;">
                        <button type="submit" id="resendBtn" class="btn btn-warning" disabled>📧 Отправить повторно</button>
                    </form>
                </div>
                
                <hr>
                <a href="/profile" class="btn btn-outline-secondary mt-2">Вернуться в профиль</a>
            </div>
        </div>
    </div>
</div>

<script>
    // Ждём 2 минуты с момента загрузки страницы
    let timeLeft = 120;
    
    const timerElement = document.getElementById('timer');
    const resendBtn = document.getElementById('resendBtn');
    
    function updateTimer() {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        // Используем простое сложение строк вместо padStart для совместимости
        const minutesStr = minutes < 10 ? '0' + minutes : '' + minutes;
        const secondsStr = seconds < 10 ? '0' + seconds : '' + seconds;
        timerElement.textContent = minutesStr + ':' + secondsStr;
        
        if (timeLeft <= 0) {
            resendBtn.disabled = false;
            timerElement.textContent = '00:00';
        } else {
            resendBtn.disabled = true;
            timeLeft--;
            setTimeout(updateTimer, 1000);
        }
    }
    
    // Запускаем таймер
    updateTimer();
</script>