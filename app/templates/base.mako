<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${self.title() if hasattr(self, 'title') else 'ProgressPal'}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .card { border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
        .progress-bar { transition: width 0.3s ease; }
        .task-done { text-decoration: line-through; opacity: 0.7; }
        .container { max-width: 800px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">📒 ProgressPal</a>
            <div class="navbar-nav ms-auto">
                % if current_user:
                    <span class="nav-item nav-link text-light">👤 ${current_user.username}</span>
                    <a class="nav-item nav-link" href="/auth/logout">🚪 Выйти</a>
                    <a class='nav-item nav-link' href='/profile'>⚙️ Профиль</a>
                % else:
                    <a class="nav-item nav-link" href="/auth/login-page">🔐 Вход</a>
                    <a class="nav-item nav-link" href="/auth/register-page">🪪 Регистрация</a>
                % endif
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        % if error:
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                ${error}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        % endif

        ${next.body()}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>