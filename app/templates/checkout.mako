<%inherit file="base.mako">
<%def name="title()">Оплата - ProgressPal</%def>

<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-primary text-white text-center">
                <h4>💳 Оплата подписки</h4>
            </div>
            <div class="card-body text-center">
                <div class="alert alert-info">
                    <strong>${'VIP Месяц' if interval == 'month' else 'VIP Год'}</strong><br>
                    Сумма: ${'25₽' if interval == 'month' else '250₽'}
                </div>
                <div id="payment-container"></div>
                <div id="error-message" class="text-danger mt-2"></div>
            </div>
        </div>
    </div>
</div>

<script src="https://static.yookassa.ru/checkout-ui/0.1.0/checkout-ui.js"></script>
<script>
    const checkout = new YooKassaCheckoutUI({
        confirmation_token: '${confirmation_token}',
        return_url: 'http://localhost:8000/payments/success',
        error_callback: function(error) {
            document.getElementById('error-message').innerText = error.message;
        }
    });
    checkout.render('payment-container');
</script>