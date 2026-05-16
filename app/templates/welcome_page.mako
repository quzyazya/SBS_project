<%inherit file="base.mako" />
<%def name="title()">Добро пожаловать! - ProgressPal</%def>

<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card shadow-lg" style="border: none; background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); border-radius: 20px;">
            <div class="card-body text-center p-5">
                <div style="font-size: 4rem;">🎉</div>
                <h2 class="text-white mb-4">Добро пожаловать в ProgressPal!</h2>
                <p class="text-white-50 mb-4">Вот что вы можете делать с нашим сервисом:</p>
                
                <div class="row text-start text-white mb-4">
                    <div class="col-md-6 mb-3">
                        <div class="border rounded p-3 h-100" style="border-color: rgba(255,255,255,0.3) !important;">
                            <span style="font-size: 2rem;">📋</span>
                            <h5 class="mt-2">Создавать задачи</h5>
                            <small>Добавлять задачи с дедлайнами и описанием</small>
                        </div>
                    </div>
                    <div class="col-md-6 mb-3">
                        <div class="border rounded p-3 h-100" style="border-color: rgba(255,255,255,0.3) !important;">
                            <span style="font-size: 2rem;">📌</span>
                            <h5 class="mt-2">Закреплять важное</h5>
                            <small>Закрепляйте до 3 важных задач (VIP - безлимит)</small>
                        </div>
                    </div>
                    <div class="col-md-6 mb-3">
                        <div class="border rounded p-3 h-100" style="border-color: rgba(255,255,255,0.3) !important;">
                            <span style="font-size: 2rem;">📅</span>
                            <h5 class="mt-2">Календарь дедлайнов</h5>
                            <small>Отслеживать сроки в удобном календаре (только VIP)</small>
                        </div>
                    </div>
                    <div class="col-md-6 mb-3">
                        <div class="border rounded p-3 h-100" style="border-color: rgba(255,255,255,0.3) !important;">
                            <span style="font-size: 2rem;">🔐</span>
                            <h5 class="mt-2">2FA безопасность</h5>
                            <small>Защитите аккаунт двухфакторной аутентификацией</small>
                        </div>
                    </div>
                </div>
                
                <a href="/" class="btn btn-light btn-lg px-5" style="background: #fff; color: #9b59b6; border-radius: 50px; font-weight: bold;">
                    Продолжить →
                </a>
            </div>
        </div>
    </div>
</div>