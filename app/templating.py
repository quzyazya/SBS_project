from mako.lookup import TemplateLookup
from mako.template import Template
from fastapi import Request
from fastapi.responses import HTMLResponse
from pathlib import Path
from typing import Dict, Any

# Настройка поиска шаблонов
TEMPLATES_DIR = Path("app/templates")
template_lookup = TemplateLookup(
    directories=[str(TEMPLATES_DIR)],
    input_encoding='utf-8',
    output_encoding='utf-8',
    filesystem_checks=True  # Автоматическая перезагрузка при изменении файлов
)


def render_template(template_name: str, request: Request, **context: Dict[str, Any]) -> HTMLResponse:
    """
    Универсальная функция для рендеринга Mako шаблонов.
    Аналог Jinja2Templates.TemplateResponse.
    """
    # Автоматически добавляем request в контекст
    context["request"] = request
    
    # Загружаем и рендерим шаблон
    template = template_lookup.get_template(template_name)
    rendered = template.render(**context)
    
    return HTMLResponse(content=rendered)