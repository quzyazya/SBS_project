<%inherit file="base.mako" />
<%def name="title()">Email подтверждён - ProgressPal</%def>

<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-success text-white">
                <h4 class="mb-0">☑️ Email подтверждён!</h4>
            </div>
            <div class="card-body text-center">
                <p>Ваш email успешно подтверждён.</p>
                <p>Теперь вы можете надёжно пользоваться всеми функциями сервиса.</p>
                <a href="/profile" class="btn btn-primary btn-lg mt-3">Продолжить →</a>
            </div>
        </div>
    </div>
</div>