<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Сброс пароля</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #9b59b6; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .button { background: #9b59b6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
        .warning { background: #fff3cd; padding: 10px; margin-top: 20px; }
        .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>ProgressPal</h2>
        </div>
        <div class="content">
            <h3>Сброс пароля</h3>
            <p>Здравствуйте, ${username}!</p>
            <p>Мы получили запрос на сброс пароля.</p>
            <p><a href="${reset_url}" class="button">Сбросить пароль</a></p>
            <p>Или скопируйте ссылку: ${reset_url}</p>
            <div class="warning">
                ⚠️ Если вы не запрашивали сброс пароля, проигнорируйте это письмо.
            </div>
            <p>Ссылка действительна 1 час.</p>
        </div>
        <div class="footer">
            <p>© 2026 ProgressPal</p>
        </div>
    </div>
</body>
</html>