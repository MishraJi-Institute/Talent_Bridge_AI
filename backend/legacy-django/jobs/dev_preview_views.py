import os
from datetime import datetime, timezone
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.checks import run_checks
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.template import TemplateSyntaxError, engines
from django.utils import timezone as django_timezone
from django.views.decorators.http import require_GET

from .dev_preview import source_fingerprints


SERVER_STARTED_AT = datetime.now(timezone.utc)
_CHECKED_AT = 0.0
_CHECK_MESSAGES = []


def _template_errors():
    project_root = Path(settings.PROJECT_ROOT)
    template_roots = [
        settings.BASE_DIR / 'templates',
        project_root / 'pages',
        project_root,
    ]
    for config in apps.get_app_configs():
        root = Path(config.path) / 'templates'
        try:
            root.relative_to(project_root)
        except ValueError:
            continue
        template_roots.append(root)
    engine = engines['django'].engine
    errors = []
    checked = set()
    for root in template_roots:
        if not root.is_dir():
            continue
        paths = root.glob('*.html') if root == project_root else root.rglob('*.html')
        for path in paths:
            if path in checked or any(part in {'.venv', 'site', '__pycache__'} for part in path.parts):
                continue
            checked.add(path)
            try:
                engine.from_string(path.read_text(encoding='utf-8'))
            except TemplateSyntaxError as error:
                errors.append({
                    'level': 'error',
                    'message': f'{path.relative_to(project_root)}: {error}',
                })
    return errors


def _require_development():
    if not settings.DEBUG:
        raise Http404


@require_GET
def dev_preview_dashboard(request):
    _require_development()
    return render(request, 'dev_preview.html')


@require_GET
def dev_preview_state(request):
    global _CHECKED_AT, _CHECK_MESSAGES
    _require_development()

    if django_timezone.now().timestamp() - _CHECKED_AT >= 5:
        _CHECK_MESSAGES = [
            {'level': check.level_tag, 'message': check.msg}
            for check in run_checks()
            if check.is_serious()
        ]
        _CHECK_MESSAGES.extend(_template_errors())
        _CHECKED_AT = django_timezone.now().timestamp()

    fingerprints, counts, missing_roots, source_files = source_fingerprints()
    frontend_errors = [f'Missing source folder: {folder}' for folder in missing_roots]
    frontend_ok = not frontend_errors and counts['styles'] > 0 and counts['scripts'] > 0
    if not frontend_ok and not frontend_errors:
        frontend_errors.append('Expected CSS or JavaScript source files were not found.')
    errors = _CHECK_MESSAGES + [
        {'level': 'error', 'message': message}
        for message in frontend_errors
    ]

    return JsonResponse({
        'server': {
            'status': 'ok' if not _CHECK_MESSAGES else 'error',
            'mode': 'development',
            'pid': os.getpid(),
            'started_at': SERVER_STARTED_AT.isoformat(),
            'url': request.build_absolute_uri('/'),
        },
        'frontend': {
            'status': 'ok' if frontend_ok else 'error',
            'counts': counts,
            'scripts': source_files['scripts'],
        },
        'fingerprints': fingerprints,
        'errors': errors,
    })
