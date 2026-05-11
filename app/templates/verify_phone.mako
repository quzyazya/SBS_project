<%inherit file="base.mako" />
<%def name="title()">Подтверждение телефона - ProgressPal</%def>

<div class="row justify-content-center">
    <div class="col-md-5">
        <div class="card">
            <div class="card-header bg-info text-white text-center">
                <h4 class="mb-0">📱 Подтверждение телефона</h4>
            </div>
            <div class="card-body">
                <p class="text-center">Код подтверждения отправлен на номер</p>
                <p class="text-center fw-bold">${phone}</p>
                
                <form method="post" action="/profile/verify-phone">
                    <div class="mb-3">
                        <label class="form-label">Код из SMS</label>
                        <input type="text" name="code" class="form-control" placeholder="000000" required>
                    </div>
                    % if request.query_params.get('error') == 'invalid_code':
                        <div class="alert alert-danger">Неверный код подтверждения</div>
                    % endif
                    <button type="submit" class="btn btn-success w-100">Подтвердить телефон</button>
                </form>
                <hr>
                <form method="post" action="/profile/send-phone-code" class="mt-2">
                    <input type="hidden" name="phone" value="${phone}">
                    <button type="submit" class="btn btn-secondary w-100">Отправить код повторно</button>
                </form>
            </div>
        </div>
    </div>
</div>