<%inherit file="base.mako" />
<%def name="title()">VIP подписка - ProgressPal</%def>
<div class="row justify-content-center">
    % if not current_user.is_email_verified:
        <div class="col-md-8">
            <div class="alert alert-warning text-center">
                ⚠️ Для покупки подписки необходимо 
                <a href="/profile" class="alert-link">подтвердить email в профиле</a>
            </div>
        </div>
    % else:
        <div class="col-md-8">
            <h1 style='margin-left: 50px;' class="mb-4">🚀  Повысьте продуктивность с VIP</h1>

            <!-- Преимущества VIP -->
            <div class="card mb-4">
                <div class="card-body">
                    <h5 class="card-title text-center">✨ Преимущества VIP статуса</h5>
                    <div class="row text-center mt-3">
                        <div class="col-md-6 mb-3">
                            <div class="border rounded p-3 h-100">
                                <span style="font-size: 2rem;">📌</span>
                                <h6 class="mt-2">Неограниченные закрепления</h6>
                                <small class="text-muted">Free: до 3 закреплённых задач<br>VIP: безлимит на задачи</small>
                            </div>
                        </div>
                        <div class="col-md-6 mb-3">
                            <div class="border rounded p-3 h-100">
                                <span style="font-size: 2rem;">📅</span>
                                <h6 class="mt-2">Функциональный календарь</h6>
                                <small class="text-muted">Free: нет календаря задач<br>VIP: календарь задач с дедлайнами</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Выбор тарифа -->                  
            <div class="row">
                <!-- Месяц -->
                <div class="col-md-6 mb-4">
                    <div class="card h-100 text-center border-warning">
                        <div class="card-header bg-warning text-dark">
                            <h4 class="mb-0">🔥 VIP Месяц</h4>
                            <span class="badge bg-light text-dark mt-1">✨ ВЫГОДНОЕ ПРЕДЛОЖЕНИЕ</span>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <span style="font-size: 1.2rem; text-decoration: line-through; color: gray;">50₽</span>
                                <span style="font-size: 2rem; font-weight: bold; color: #ff6b6b;"> 25₽</span>
                                <span class="text-muted">/месяц</span>
                            </div>
                            <ul class="list-unstyled text-start">
                                <li>✓ 📌 Неограниченные закрепления</li>
                                <li>✓ 📅 Календарь задач с дедлайнами</li>
                                <li>✓ ♾️ Неограниченное количество никнеймов</li>
                                <li>✓ 🔥 Экономия 50%</li>
                            </ul>
                            <form action="/payments/create-payment" method="post">
                                <input type="hidden" name="interval" value="month">
                                <button type="submit" class="btn btn-warning w-100 mt-3">Оплатить 25₽💵</button>
                            </form>
                        </div>
                    </div>
                </div>
                
                <!-- Год -->
                <div class="col-md-6 mb-4">
                    <div class="card h-100 text-center border-success">
                        <div class="card-header bg-success text-white mt-0">
                            <h4 class="mb-0">💎 VIP Год</h4>
                            <span class="badge bg-light text-dark mt-1">🔥 ЛУЧШАЯ ЦЕНА</span>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <span style="font-size: 1.2rem; text-decoration: line-through; color: gray;">580₽</span>
                                <span style="font-size: 2rem; font-weight: bold; color: #ff6b6b;"> 250₽</span>
                                <span class="text-muted">/год</span>
                            </div>
                            <ul class="list-unstyled text-start">
                                <li>✓ 📌 Неограниченные закрепления</li>
                                <li>✓ 📅 Календарь задач с дедлайнами</li>
                                <li>✓ ♾️ Неограниченное количество никнеймов</li>
                                <li>✓ 🔥 Экономия 57%</li>
                            </ul>
                            <form action="/payments/create-payment" method="post">
                                <input type="hidden" name="interval" value="year">
                                <button type="submit" class="btn btn-success w-100 mt-3">Оплатить 250₽💵</button>
                            </form>
                        </div>
                    </div>
                </div>
                <!-- Бесплатный пробный период -->
                <div class='row mt-4'>
                    <div class='col-md-12'>
                        <div class='card text-center border-info'>
                            <div class='card-header bg-info text-white'>
                                <h4 class='mb-0'>🎁 Бесплатный пробный период</h4>
                            </div>
                            <div class='card-body'>
                                <h3 class='text-info'>7 дней VIP</h3>
                                <p>Полностью бесплатно! Без привязки карты.</p>
                                <form method='post' action='/activate-trial-vip-temporary'>
                                    <button type='submit' class='btn btn-info btn-lg'>Активировать пробный период 🎉</button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Сравнение тарифов -->
            <div class="card mt-2">
                <div class="card-header bg-secondary text-white">
                    <h5 class="mb-0">📊 Сравнение тарифов</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-bordered text-center">
                            <thead>
                                <tr><th>Функция</th><th>Free</th><th>VIP</th></tr>
                            </thead>
                            <tbody>
                                <tr><td class="text-start">Создание задач</td><td>✔️ Безлимит</td><td>✔️ Безлимит</td></tr>
                                <tr><td class="text-start">Закрепление задач (📌)</td><td>⚠️ До 3</td><td>✔️ Безлимит</td></tr>
                                <tr><td class="text-start">Календарь задач</td><td>❌</td><td>✔️ Доступен</td></tr>
                                <tr><td class="text-start">Приоритетная поддержка</td><td>❌</td><td>✔️</td></tr>
                                <tr><td class="text-start">Смена никнейма</td><td>😢 1 раз</td><td> ♾️</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    % endif
</div>