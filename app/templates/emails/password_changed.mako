<!DOCTYPE html>
<html>
<head>
    <meta charset='UTF-8'>
    <title>Пароль изменён</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #9b59b6; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .warning { background: #fff3cd; padding: 10px; margin-top: 20x; }
        .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class='container'>
        <div class='header'>
            <h2>ProgressPal</h2>
        </div>
        <div class='content'>
            <h3>🔐 Пароль изменён</h3>
            <p>Здравствуйте, ${username}!</p>
            <p>Ваш пароль был успешно изменён.</p>
            <p>Если вы не меняли пароль, немедленно свяжитесь с поддержкой и смените пароль снова.</p>
            <div class='warning'>
                ⚠️ Если вы не запрашивали смену пароля, кто-то мог получить доступ к вашему аккаунту.
            </div>
        </div>
        <div class='footer'>
            <p>© 2026 ProgressPal</p>
        </div>
    </div>
</body>
</html>