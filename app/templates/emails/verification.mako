<!DOCTYPE html>
<html>
<head>
    <meta charset='UTF-8'>
    <title>Подтверждение email</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #9b59b6; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .button { background: #9b59b6; color: white; padding: 10px 20px; text-decoration: none; border-radiues: 5px; }
        .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class='container'>
        <div class='header'>
            <h2>ProgressPal</h2>
        </div>
        <div class='content'>
            <h3>Подтверждение email адреса</h3>
            <p>Здравствуйте, ${username}!</p>
            <p>Для завершения регистрации, пожалуйста, подтвердите ваш email:</p>
            <p><a href='${verification_url}' class='button'>Подтвердить email</a></p>
            <p>Или скопируйте ссылку: ${verification_url}</p>
            <p>Ссылка действительна 24 часа.</p>
        </div>
        <div class='footer'>
            <p>© 2026 ProgressPal</p>
        </div>
    </div>
</body>
</html>