import hashlib
import os
import re
import time
from pathlib import Path

from django.conf import settings


_HTML_BODY = re.compile(br'</body\s*>', re.IGNORECASE)
_IGNORED_SOURCE_DIRECTORIES = {'.venv', 'venv', '__pycache__', 'staticfiles'}


def _raise_walk_error(error):
    raise error


def _source_paths(root, recursive):
    if not recursive:
        return sorted(root.glob('*'))

    paths = []
    for current, directories, filenames in os.walk(root, onerror=_raise_walk_error):
        directories[:] = sorted(
            name for name in directories
            if name not in _IGNORED_SOURCE_DIRECTORIES
        )
        paths.extend(Path(current) / name for name in filenames)
    return sorted(paths)


class LivePreviewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            response.status_code != 200
            or getattr(response, 'streaming', False)
            or not response.get('Content-Type', '').startswith('text/html')
            or request.path.startswith('/__dev__/')
        ):
            return response

        script = f'<script src="/js/core/dev-preview.js?v={time.time_ns()}" defer></script>'.encode('ascii')
        content = response.content
        closing_body = _HTML_BODY.search(content)
        if closing_body:
            response.content = content[:closing_body.start()] + script + content[closing_body.start():]
        else:
            response.content = content + script
        response.headers.pop('Content-Length', None)
        return response


def source_fingerprints():
    project_root = Path(settings.PROJECT_ROOT)
    app_root = Path(settings.BASE_DIR)
    configured_frontend = Path(getattr(settings, 'FRONTEND_ROOT', project_root / 'frontend'))
    # Keep fingerprinting inside the active PROJECT_ROOT (tests override PROJECT_ROOT).
    try:
        configured_frontend.resolve().relative_to(project_root.resolve())
        frontend_root = configured_frontend
    except ValueError:
        frontend_root = project_root / 'frontend'
    # Prefer the organized frontend/ tree; keep root junctions as fallbacks.
    styles_root = frontend_root / 'css' if (frontend_root / 'css').is_dir() else project_root / 'css'
    scripts_root = frontend_root / 'js' if (frontend_root / 'js').is_dir() else project_root / 'js'
    images_root = (
        frontend_root / 'assets' / 'images'
        if (frontend_root / 'assets' / 'images').is_dir()
        else project_root / 'images'
    )
    pages_root = frontend_root / 'pages' if (frontend_root / 'pages').is_dir() else project_root / 'pages'
    html_root = frontend_root if (frontend_root / 'index.html').is_file() else project_root
    optional_asset_roots = (
        frontend_root / 'logo',
        frontend_root / 'videos',
        project_root / 'logo',
        project_root / 'videos',
    )
    groups = {
        'styles': [(styles_root, {'.css'}, True, True)],
        'scripts': [(scripts_root, {'.js'}, True, True)],
        'assets': [
            (images_root, {'.png', '.jpg', '.jpeg', '.svg', '.webp', '.gif', '.ico'}, True, True),
            (frontend_root / 'logo', {'.png', '.jpg', '.jpeg', '.svg', '.webp', '.gif', '.ico'}, True, False),
            (frontend_root / 'videos', {'.mp4', '.webm'}, True, False),
            (project_root / 'logo', {'.png', '.jpg', '.jpeg', '.svg', '.webp', '.gif', '.ico'}, True, False),
            (project_root / 'videos', {'.mp4', '.webm'}, True, False),
        ],
        'templates': [
            (pages_root, {'.html'}, True, True),
            (app_root / 'templates', {'.html'}, True, False),
            (app_root / 'jobs' / 'templates', {'.html'}, True, False),
            (html_root, {'.html'}, False, True),
        ],
        'backend': [(app_root, {'.py'}, True, True)],
    }

    fingerprints = {}
    counts = {}
    source_files = {}
    missing_roots = []
    for group, roots in groups.items():
        digest = hashlib.sha256()
        count = 0
        group_files = []
        for root, extensions, recursive, required in roots:
            if not root.is_dir():
                if required and root not in optional_asset_roots:
                    try:
                        missing_roots.append(str(root.relative_to(project_root)))
                    except ValueError:
                        missing_roots.append(str(root))
                continue
            for path in _source_paths(root, recursive):
                if not path.is_file() or path.suffix.lower() not in extensions:
                    continue
                stat = path.stat()
                try:
                    relative = path.relative_to(project_root)
                except ValueError:
                    relative = path
                digest.update(
                    f'{relative}:{stat.st_mtime_ns}:{stat.st_size}\n'.encode('utf-8')
                )
                group_files.append(Path(relative).as_posix())
                count += 1
        fingerprints[group] = digest.hexdigest()
        counts[group] = count
        source_files[group] = group_files
    return fingerprints, counts, missing_roots, source_files
