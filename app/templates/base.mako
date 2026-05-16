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

        .bg-purple {
            background-color: #9b59b6 !important;
        }
        .bg-purple-striped {
            background-image: linear-gradient(45deg, rgba(255,255,255,.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,.15) 50%, rgba(255,255,255,.15) 75%, transparent 75%, transparent) !important;
            background-size: 1rem 1rem !important;
        }
    </style>
    <style>
        /* ======================================== */
        /* СВЕТЛАЯ ТЕМА (по умолчанию) */
        /* ======================================== */
        :root {
            --bg-color: #f4f6f9;
            --text-color: #212529;
            --card-bg: #ffffff;
            --card-header-bg: #f8f9fa;
            --border-color: #dee2e6;
            --input-bg: #ffffff;
            --input-border: #ced4da;
            --table-stripe: #f8f9fa;
            --table-header-bg: #f8f9fa;
            --table-hover: #f5f5f5;
            --btn-outline-color: #6c757d;
        }
        
        /* ======================================== */
        /* ТЁМНАЯ ТЕМА */
        /* ======================================== */
        body.dark-mode {
            --bg-color: #1a1a2e;
            --text-color: #ffffff;
            --card-bg: #16213e;
            --card-header-bg: #0f3460;
            --border-color: #2c3e50;
            --input-bg: #0f3460;
            --input-border: #2c3e50;
            --table-stripe: #1a1a2e;
            --table-header-bg: #0f3460;
            --table-hover: #2c3e50;
            --btn-outline-color: #adb5bd;
        }
        
        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            transition: background-color 0.3s ease;
        }
        
        /* ======================================== */
        /* ОСНОВНЫЕ ТЕКСТЫ - МЕНЯЮТ ЦВЕТ */
        /* ======================================== */
        body, .card-body, .list-group-item, .form-label, .table, p,
        h1, h2, h3, h4, h5, h6, .card-header, .list-group-item,
        .table td, .table th, .text-center, .fw-bold, .mb-0, .mt-2,
        .small, .card-title, .alert, .btn-link,
        .dropdown-item, .navbar-nav .nav-link {
            color: var(--text-color) !important;
        }
        
        /* Muted текст */
        .text-muted, small:not(.text-white), .small:not(.text-white) {
            color: #6c757d !important;
        }
        
        body.dark-mode .text-muted,
        body.dark-mode small:not(.text-white),
        body.dark-mode .small:not(.text-white) {
            color: #c0c0c0 !important;
        }
        
        /* ======================================== */
        /* ВЕРХНЕЕ МЕНЮ (никнейм, Выйти, Профиль) - ВСЕГДА БЕЛЫЕ */
        /* ======================================== */
        .navbar-nav .nav-link,
        .navbar-text,
        .dropdown-toggle,
        .navbar-nav {
            color: #ffffff !important;
        }
        
        /* Hover эффект (немного прозрачнее) */
        .navbar-nav .nav-link:hover {
            color: #ffffff !important;
            opacity: 0.8;
        }
        
        body.dark-mode .navbar-nav .nav-link,
        body.dark-mode .navbar-text,
        body.dark-mode .dropdown-toggle,
        body.dark-mode .navbar-nav {
            color: #ffffff !important;
        }
        
        body.dark-mode .navbar-nav .nav-link:hover {
            color: #ffffff !important;
            opacity: 0.8;
        }
        
        /* ======================================== */
        /* ЛОГОТИП ProgressPal - ВСЕГДА БЕЛЫЙ */
        /* ======================================== */
        .navbar-brand {
            color: #ffffff !important;
        }
        
        body.dark-mode .navbar-brand {
            color: #ffffff !important;
        }
        
        /* ======================================== */
        /* ССЫЛКИ НА СТРАНИЦАХ ВХОДА И РЕГИСТРАЦИИ */
        /* ======================================== */
        
        /* "Забыли пароль?" - всегда видимая */
        a[href="/auth/forgot-password"] {
            color: #000000 !important;
        }
        
        body.dark-mode a[href="/auth/forgot-password"] {
            color: #000000 !important;
        }
        
        /* "Нет аккаунта? Зарегистрироваться" */
        a[href="/auth/register-page"] {
            color: #000000 !important;
        }
        
        body.dark-mode a[href="/auth/register-page"] {
            color: #000000 !important;
        }
        
        /* "Уже есть аккаунт? Войти" - слово "Войти" должно быть чёрным/белым */
        a[href="/auth/login-page"] {
            color: var(--text-color) !important;
        }
        
        body.dark-mode a[href="/auth/login-page"] {
            color: #ffffff !important;
        }
        
        /* ======================================== */
        /* ТАБЛИЦЫ */
        /* ======================================== */
        .table {
            color: var(--text-color);
            background-color: var(--card-bg);
        }
        
        .table-striped > tbody > tr:nth-of-type(odd) {
            background-color: var(--table-stripe);
        }
        
        .table thead th {
            background-color: var(--table-header-bg);
            border-bottom-color: var(--border-color);
        }
        
        .table tbody tr:hover {
            background-color: var(--table-hover);
        }
        
        .table td, .table th {
            border-color: var(--border-color);
        }
        
        /* ======================================== */
        /* ФОРМЫ */
        /* ======================================== */
        .form-control, .input-group-text {
            background-color: var(--input-bg);
            border-color: var(--input-border);
            color: var(--text-color);
        }
        
        .form-control:focus {
            background-color: var(--input-bg);
            color: var(--text-color);
        }
        
        body.dark-mode .form-control::placeholder {
            color: #999999;
        }
        
        /* ======================================== */
        /* КНОПКИ */
        /* ======================================== */
        .btn-outline-secondary {
            color: var(--btn-outline-color);
            border-color: var(--btn-outline-color);
        }
        
        .btn-outline-secondary:hover {
            background-color: var(--btn-outline-color);
            color: var(--card-bg);
        }
        
        /* ======================================== */
        /* ПРОГРЕСС-БАР */
        /* ======================================== */
        .progress {
            background-color: var(--border-color);
        }
        
        /* ======================================== */
        /* ALERT */
        /* ======================================== */
        body.dark-mode .alert-info {
            background-color: #0f3460;
            border-color: #2c3e50;
            color: #ffffff;
        }
        
        body.dark-mode .alert-warning {
            background-color: #5a4a00;
            border-color: #8a6d00;
            color: #ffffff;
        }
        
        body.dark-mode .alert-danger {
            background-color: #5a1a1a;
            border-color: #8a2a2a;
            color: #ffffff;
        }
        
        body.dark-mode .alert-success {
            background-color: #1a5a2a;
            border-color: #2a8a3a;
            color: #ffffff;
        }
        
        /* ======================================== */
        /* БОКОВАЯ ПАНЕЛЬ С ЦИТАТОЙ */
        /* ======================================== */
        .quote-sidebar .card {
            background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%) !important;
        }
        
        .quote-sidebar .card * {
            color: white !important;
        }
        
        /* ======================================== */
        /* КАЛЕНДАРЬ */
        /* ======================================== */
        .card-header.bg-danger {
            background-color: #9b59b6 !important;
        }
        
        .card-header.bg-danger h6,
        .card-header.bg-danger .mb-0 {
            color: white !important;
        }
        
        body.dark-mode .card-header.bg-danger {
            background-color: #9b59b6 !important;
        }
        
        body.dark-mode .calendar-day {
            border-color: var(--border-color);
            background-color: var(--card-bg);
        }
        
        .calendar-day .day-number {
            color: var(--text-color);
        }
        
        body.dark-mode .calendar-day .text-danger {
            color: #ff6b6b !important;
        }
        
        body.dark-mode .calendar-day .text-warning {
            color: #ffd93d !important;
        }
        
        body.dark-mode .calendar-day .text-success {
            color: #6bcb77 !important;
        }
        
        /* ======================================== */
        /* BADGE */
        /* ======================================== */
        body.dark-mode .badge.bg-secondary {
            background-color: #2c3e50 !important;
            color: white;
        }
        
        body.dark-mode .badge.bg-warning {
            background-color: #f39c12 !important;
            color: #1a1a2e;
        }
        
        body.dark-mode .badge.bg-success {
            background-color: #27ae60 !important;
            color: white;
        }
        
        /* ======================================== */
        /* КАРТОЧКИ */
        /* ======================================== */
        .card, .list-group-item, .modal-content, .dropdown-menu {
            background-color: var(--card-bg);
            border-color: var(--border-color);
        }
        
        .card-header {
            background-color: var(--card-header-bg);
            border-bottom-color: var(--border-color);
        }
        
        .card-header * {
            color: var(--text-color) !important;
        }
        
        /* ======================================== */
        /* UPGRADE PAGE - ТЁМНАЯ ТЕМА */
        /* ======================================== */
        
        /* Карточки тарифов в тёмной теме */
        body.dark-mode .card.border-warning,
        body.dark-mode .card.border-success,
        body.dark-mode .card.border-info {
            background-color: var(--card-bg) !important;
            border-color: var(--border-color) !important;
        }
        
        /* Заголовки карточек - ВСЕГДА цветные (жёлтый/зелёный/голубой) */
        .card.border-warning .card-header.bg-warning {
            background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%) !important;
        }
        
        .card.border-success .card-header.bg-success {
            background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%) !important;
        }
        
        .card.border-info .card-header.bg-info {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%) !important;
        }
        
        /* Текст в заголовках карточек - всегда белый */
        .card.border-warning .card-header.bg-warning h4,
        .card.border-warning .card-header.bg-warning .badge,
        .card.border-success .card-header.bg-success h4,
        .card.border-success .card-header.bg-success .badge,
        .card.border-info .card-header.bg-info h4,
        .card.border-info .card-header.bg-info .badge {
            color: #ffffff !important;
        }
        
        /* В тёмной теме тоже цветные */
        body.dark-mode .card.border-warning .card-header.bg-warning {
            background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%) !important;
        }
        
        body.dark-mode .card.border-success .card-header.bg-success {
            background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%) !important;
        }
        
        body.dark-mode .card.border-info .card-header.bg-info {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%) !important;
        }
        
        body.dark-mode .card.border-warning .card-header.bg-warning h4,
        body.dark-mode .card.border-warning .card-header.bg-warning .badge,
        body.dark-mode .card.border-success .card-header.bg-success h4,
        body.dark-mode .card.border-success .card-header.bg-success .badge,
        body.dark-mode .card.border-info .card-header.bg-info h4,
        body.dark-mode .card.border-info .card-header.bg-info .badge {
            color: #ffffff !important;
        }
        
        /* Badge "ВЫГОДНОЕ ПРЕДЛОЖЕНИЕ" и "ЛУЧШАЯ ЦЕНА" */
        /* Светлая тема - прозрачный фон, цветной текст */
        .badge.bg-light.text-dark {
            background-color: transparent !important;
            color: #ffd700 !important;
            font-weight: bold;
        }
        
        /* Тёмная тема - тёмный фон, золотой текст */
        body.dark-mode .badge.bg-light.text-dark {
            background-color: #2c3e50 !important;
            color: #ffd700 !important;
        }
        
        /* Тело карточек */
        body.dark-mode .card-body {
            background-color: var(--card-bg) !important;
            color: #ffffff !important;
        }
        
        /* Текст цен */
        body.dark-mode .card-body .text-muted,
        body.dark-mode .card-body .text-gray {
            color: #c0c0c0 !important;
        }
        
        body.dark-mode .card-body .text-danger {
            color: #ff6b6b !important;
        }
        
        /* Зачёркнутая цена */
        body.dark-mode .card-body .text-decoration-line-through {
            color: #888888 !important;
        }
        
        /* Список преимуществ */
        body.dark-mode .card-body .list-unstyled li {
            color: #ffffff !important;
        }
        
        /* ======================================== */
        /* ТАБЛИЦА СРАВНЕНИЯ ТАРИФОВ */
        /* ======================================== */
        
        body.dark-mode .table-bordered {
            background-color: var(--card-bg) !important;
            border-color: var(--border-color) !important;
        }
        
        body.dark-mode .table-bordered thead th {
            background-color: var(--table-header-bg) !important;
            color: #ffffff !important;
            border-color: var(--border-color) !important;
        }
        
        body.dark-mode .table-bordered tbody td,
        body.dark-mode .table-bordered tbody th {
            background-color: var(--card-bg) !important;
            color: #ffffff !important;
            border-color: var(--border-color) !important;
        }
        
        body.dark-mode .table-bordered tbody tr:hover td {
            background-color: var(--table-hover) !important;
        }
        
        /* Карточка сравнения тарифов */
        body.dark-mode .card.bg-secondary {
            background-color: var(--card-bg) !important;
        }
        
        body.dark-mode .card-header.bg-secondary {
            background-color: var(--card-header-bg) !important;
        }
        
        body.dark-mode .card-header.bg-secondary h5 {
            color: #ffffff !important;
        }
        
        /* ======================================== */
        /* ГЛАВНАЯ СТРАНИЦА - РАМКИ КАРТОЧЕК */
        /* ======================================== */
        
        /* Карточки статистики - всегда видимые рамки */
        .card.border-primary,
        .card.border-warning,
        .card.border-info,
        .card.border-danger,
        .card.border-success {
            border-width: 2px !important;
        }
        
        /* Светлая тема */
        .card.border-primary { border-color: #9b59b6 !important; }
        .card.border-warning { border-color: #f39c12 !important; }
        .card.border-info { border-color: #3498db !important; }
        .card.border-danger { border-color: #e74c3c !important; }
        .card.border-success { border-color: #2ecc71 !important; }
        
        /* В тёмной теме рамки ярче */
        body.dark-mode .card.border-primary { border-color: #bb8af0 !important; }
        body.dark-mode .card.border-warning { border-color: #f5b041 !important; }
        body.dark-mode .card.border-info { border-color: #5dade2 !important; }
        body.dark-mode .card.border-danger { border-color: #f1948a !important; }
        body.dark-mode .card.border-success { border-color: #82e0aa !important; }
        
        /* Тени для карточек в тёмной теме */
        body.dark-mode .card {
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }
        
        /* Текст внутри цветных карточек */
        body.dark-mode .card.border-primary .card-body,
        body.dark-mode .card.border-warning .card-body,
        body.dark-mode .card.border-info .card-body,
        body.dark-mode .card.border-danger .card-body,
        body.dark-mode .card.border-success .card-body {
            color: #ffffff !important;
        }
        
        /* Иконки и цифры внутри карточек */
        body.dark-mode .card .text-success {
            color: #82e0aa !important;
        }
        
        body.dark-mode .card .text-warning {
            color: #f5b041 !important;
        }
        
        body.dark-mode .card .text-danger {
            color: #f1948a !important;
        }
        
        body.dark-mode .card .text-primary {
            color: #bb8af0 !important;
        }
        
        body.dark-mode .card .text-info {
            color: #5dade2 !important;
        }

        /* ======================================== */
        /* КАРТОЧКИ СТАТИСТИКИ - ЯВНЫЕ УГЛЫ */
        /* ======================================== */
        
        /* Явный фон для всех карточек статистики */
        .card {
            border-radius: 12px !important;
            overflow: hidden !important;
        }
        
        /* В светлой теме */
        .card.border-primary,
        .card.border-warning,
        .card.border-info,
        .card.border-danger,
        .card.border-success {
            background-color: var(--card-bg) !important;
            border-radius: 12px !important;
            overflow: hidden !important;
        }
        
        /* В тёмной теме */
        body.dark-mode .card.border-primary,
        body.dark-mode .card.border-warning,
        body.dark-mode .card.border-info,
        body.dark-mode .card.border-danger,
        body.dark-mode .card.border-success {
            background-color: var(--card-bg) !important;
            border-radius: 12px !important;
            overflow: hidden !important;
        }
        
        /* Тело карточек статистики */
        .card .card-body {
            border-radius: 12px !important;
        }
        
        /* Убираем возможные overflow проблемы */
        .card, .card-body {
            overflow: hidden;
        }
        
        /* Гарантируем видимость уголков в тёмной теме */
        body.dark-mode .card {
            background-color: var(--card-bg) !important;
        }
        
        body.dark-mode .card.border-primary .card-body,
        body.dark-mode .card.border-warning .card-body,
        body.dark-mode .card.border-info .card-body,
        body.dark-mode .card.border-danger .card-body,
        body.dark-mode .card.border-success .card-body {
            background-color: var(--card-bg) !important;
        }

        /* ======================================== */
        /* ОСНОВНОЙ ПРОГРЕСС-БАР - ФИОЛЕТОВАЯ ОКАНТОВКА */
        /* ======================================== */
        
        /* Прогресс-бар на главной странице */
        .progress {
            background-color: var(--card-bg) !important;
            border-radius: 20px;
            border: 2px solid #9b59b6 !important;
            overflow: hidden;
        }
        
        /* В тёмной теме фон прогресс-бара = цвет карточки */
        body.dark-mode .progress {
            background-color: var(--card-bg) !important;
            border: 2px solid #bb8af0 !important;
        }
        
        /* Полоса прогресса */
        .progress-bar {
            background: linear-gradient(90deg, #9b59b6 0%, #8e44ad 100%);
            border-radius: 20px;
        }
        
        /* Остальные прогресс-бары (например, в задачах) без окантовки */
        .list-group-item .progress {
            border: none !important;
            background-color: var(--border-color) !important;
        }
        
        .list-group-item .progress-bar {
            background: linear-gradient(90deg, #9b59b6 0%, #8e44ad 100%);
        }
        
        /* В тёмной теме для прогресс-баров в задачах */
        body.dark-mode .list-group-item .progress {
            background-color: var(--border-color) !important;
        }
    </style>
</head>
<body class="${'dark-mode' if current_user and current_user.dark_mode else ''}">
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
