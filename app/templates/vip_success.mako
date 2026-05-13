<%inherit file="base.mako" />
<%def name="title()">Поздравляем! - ProgressPal</%def>

<div class="row justify-content-center">
    <div class="col-md-5">
        <div class="card shadow-lg" style="border: none; background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); border-radius: 20px;">
            <div class="card-body text-center p-4">
                <div style="font-size: 2.5rem;">🎉</div>
                <h3 class="text-white mb-2" style="font-size: 1.5rem;">Поздравляем!</h3>
                <p class="text-white-50 mb-3" style="font-size: 0.9rem;">
                    Вы успешно приобрели VIP статус!<br>
                    Теперь вам доступны:
                </p>
                <ul class="text-white text-start mb-3" style="list-style: none; padding-left: 0; font-size: 0.85rem;">
                    <li>⭐ &nbsp; Закрепление любого количества задач</li>
                    <li>📅 &nbsp; Календарь задач с дедлайнами</li>
                    <li>✏️ &nbsp; Бесконечная смена никнейма</li>
                </ul>
                <a href="/" class="btn btn-light btn-sm px-4" style="background: #fff; color: #9b59b6; border-radius: 50px; font-weight: bold; font-size: 0.85rem;">
                    Завершить
                </a>
            </div>
        </div>
    </div>
</div>