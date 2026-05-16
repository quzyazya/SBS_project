<%inherit file="base.mako" />
<%def name="title()">Скоро - ProgressPal</%def>

<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card shadow-lg" style="border: none; background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); border-radius: 20px;">
            <div class="card-body text-center p-5">
                <div style="font-size: 4rem;">🚧</div>
                <h2 class="text-white mb-3">Coming Soon...</h2>
                <p class="text-white-50 mb-4">
                    Оплата через ЮKassa временно недоступна.<br>
                    Но вы можете получить VIP статус бесплатно!
                </p>
                
                <form method="post" action="/activate-paid-vip">
                    <button type="submit" class="btn btn-light btn-lg px-5" style="background: #fff; color: #9b59b6; border-radius: 50px; font-weight: bold;">
                        🎁 Временно подключить VIP статус
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>