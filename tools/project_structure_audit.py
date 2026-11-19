"""Generate a non-destructive project structure and reference audit."""
from __future__ import annotations

import argparse
import ast
import hashlib
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {
    '.git', '.venv', 'venv', '__pycache__', 'staticfiles', 'site',
    'private_media', 'backups', 'logs',
}
ASSET_SUFFIXES = {
    '.css', '.js', '.png', '.jpg', '.jpeg', '.svg', '.webp', '.gif',
    '.ico', '.woff', '.woff2', '.ttf', '.mp4', '.webm',
}
REQUIRED = (
    'legacy-django/manage.py',
    'legacy-django/config/settings.py',
    'legacy-django/config/urls.py',
    'legacy-django/jobs/models.py',
    'legacy-django/jobs/migrations/__init__.py',
    'legacy-django/requirements.txt',
    'index.html',
    'css/style.css',
    'js/script.js',
    'database',
    'README.md',
    '.env.example',
)


def included(path: Path) -> bool:
    return not any(part in SKIP_PARTS for part in path.parts)


def files_under(*roots: Path):
    for root in roots:
        if root.is_file():
            yield root
        elif root.is_dir():
            yield from (path for path in root.rglob('*') if path.is_file() and included(path))


def source_text(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8-sig')
    except (OSError, UnicodeError):
        return ''


def module_name(path: Path, base: Path) -> str:
    relative = path.relative_to(base).with_suffix('')
    parts = list(relative.parts)
    if parts[-1] == '__init__':
        parts.pop()
    return '.'.join(parts)


def python_findings(python_files: list[Path]):
    modules = {}
    syntax_errors = []
    for path in python_files:
        try:
            ast.parse(source_text(path), filename=str(path))
        except SyntaxError as error:
            syntax_errors.append(f'{path.relative_to(ROOT)}:{error.lineno}: {error.msg}')
            continue
        if path.is_relative_to(ROOT / 'legacy-django'):
            modules[module_name(path, ROOT / 'legacy-django')] = path

    graph = defaultdict(set)
    broken = []
    local_roots = {'config', 'jobs'}
    for module, path in modules.items():
        try:
            tree = ast.parse(source_text(path), filename=str(path))
        except SyntaxError:
            continue
        package = module if path.name == '__init__.py' else module.rpartition('.')[0]
        for node in ast.walk(tree):
            targets = []
            if isinstance(node, ast.Import):
                targets = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    prefix = package.split('.') if package else []
                    if node.level > 1:
                        prefix = prefix[:-(node.level - 1)]
                    base = '.'.join(prefix + ([node.module] if node.module else []))
                    targets = [base] if base else []
                elif node.module:
                    targets = [node.module]
            for target in targets:
                root_name = target.split('.', 1)[0]
                if root_name not in local_roots:
                    continue
                if target not in modules:
                    broken.append(f'{path.relative_to(ROOT)} imports missing module {target}')
                elif target != module:
                    graph[module].add(target)

    cycles = []
    visited = set()
    active = []

    def visit(module):
        if module in active:
            cycle = active[active.index(module):] + [module]
            normalized = tuple(sorted(cycle))
            if normalized not in cycles:
                cycles.append(normalized)
            return
        if module in visited:
            return
        active.append(module)
        for dependency in graph[module]:
            visit(dependency)
        active.pop()
        visited.add(module)

    for module in modules:
        visit(module)
    return syntax_errors, sorted(set(broken)), sorted(cycles)


def asset_findings(html_files: list[Path], css_files: list[Path]):
    missing = set()
    attribute = re.compile(r'''(?:src|href)\s*=\s*["']([^"']+)["']''', re.IGNORECASE)
    css_url = re.compile(r'''url\(\s*["']?([^)"']+)''', re.IGNORECASE)
    for path in html_files + css_files:
        text = source_text(path)
        candidates = attribute.findall(text) if path.suffix.lower() == '.html' else css_url.findall(text)
        for value in candidates:
            value = value.strip()
            parsed = urlsplit(value)
            if parsed.scheme or parsed.netloc or value.startswith(('#', 'data:', '{{', '{%')):
                continue
            relative = unquote(parsed.path).lstrip('/')
            if not Path(relative).suffix.lower() in ASSET_SUFFIXES:
                continue
            if '{{' in relative or '{%' in relative:
                continue
            candidates_to_check = []
            if value.startswith('/'):
                candidates_to_check.append(ROOT / relative)
                if relative.startswith('static/'):
                    candidates_to_check.append(ROOT / 'legacy-django' / relative)
            else:
                candidates_to_check.append((path.parent / relative).resolve())
            if not any(candidate.is_file() for candidate in candidates_to_check):
                missing.add(f'{path.relative_to(ROOT)} references {value}')
    return sorted(missing)


def duplicate_findings(source_files: list[Path]):
    by_hash = defaultdict(list)
    for path in source_files:
        if path.suffix.lower() not in {'.html', '.css', '.js'}:
            continue
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            continue
        by_hash[(path.suffix.lower(), digest)].append(path.relative_to(ROOT).as_posix())
    return [sorted(paths) for paths in by_hash.values() if len(paths) > 1]


def template_findings(python_files: list[Path], html_files: list[Path]):
    available = {path.name for path in html_files}
    for template_root in (
        ROOT / 'legacy-django' / 'templates',
        ROOT / 'legacy-django' / 'jobs' / 'templates',
        ROOT / 'pages',
    ):
        for path in files_under(template_root):
            available.add(path.relative_to(template_root).as_posix())
    missing = set()
    template_literal = re.compile(r'''["']([^"']+\.html)["']''')
    for path in python_files:
        for name in template_literal.findall(source_text(path)):
            if '*' in name or '?' in name or name.startswith('/'):
                continue
            if name not in available and Path(name).name not in available:
                missing.add(f'{path.relative_to(ROOT)} references missing template {name}')
    return sorted(missing)


def reference_candidates(source_files: list[Path], reference_sources: list[Path]):
    text = '\n'.join(source_text(path) for path in reference_sources)
    candidates = []
    for path in source_files:
        if path.suffix.lower() not in ASSET_SUFFIXES:
            continue
        if path.name not in text:
            candidates.append(path.relative_to(ROOT).as_posix())
    return candidates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='PROJECT_STRUCTURE_REPORT.md')
    parser.add_argument('--check', action='store_true', help='exit nonzero when structural errors are found')
    args = parser.parse_args()

    python_files = list(files_under(ROOT / 'legacy-django'))
    python_files = [path for path in python_files if path.suffix == '.py']
    html_files = list(files_under(
        ROOT / 'pages',
        ROOT / 'legacy-django' / 'templates',
        ROOT / 'legacy-django' / 'jobs' / 'templates',
    ))
    html_files += [path for path in (ROOT / 'index.html', ROOT / '404.html') if path.is_file()]
    css_files = list(files_under(ROOT / 'css'))
    js_files = list(files_under(ROOT / 'js'))
    asset_files = list(files_under(ROOT / 'images', ROOT / 'logo', ROOT / 'videos'))
    source_files = python_files + html_files + css_files + js_files + asset_files

    missing_required = [item for item in REQUIRED if not (ROOT / item).exists()]
    syntax_errors, broken_imports, cycles = python_findings(python_files)
    missing_assets = asset_findings(html_files, css_files)
    missing_templates = template_findings(python_files, html_files)
    duplicates = duplicate_findings(source_files)
    references = list(files_under(
        ROOT / 'legacy-django', ROOT / 'pages', ROOT / 'css', ROOT / 'js',
        ROOT / 'tools', ROOT / 'README.md', ROOT / 'README_RUN_DJANGO.md',
    ))
    unreferenced = reference_candidates(asset_files + css_files + js_files, references)
    app_migrations = []
    for model_file in files_under(ROOT / 'legacy-django'):
        if model_file.name == 'models.py':
            migrations = model_file.parent / 'migrations'
            if not migrations.is_dir() or not (migrations / '__init__.py').is_file():
                app_migrations.append(str(migrations.relative_to(ROOT)))

    lines = [
        '# Project structure report',
        '',
        'Generated by `python tools/project_structure_audit.py` using Python standard-library scans. '
        'The report is non-destructive: duplicate and unreferenced-file findings are review candidates, '
        'not deletion instructions.',
        '',
        '## Current architecture',
        '',
        '- `legacy-django/config/`: Django configuration and URL routing.',
        '- `legacy-django/jobs/`: current Django app, business logic, tests, and migrations.',
        '- `legacy-django/templates/`: Django-only templates.',
        '- Root `pages/`, `css/`, `js/`, `images/`, `logo/`, and `videos/`: source frontend and Django-served assets.',
        '- `site/`: generated static deployment output; excluded from duplicate checks and should not be hand-edited.',
        '- `database/`, `private_media/`, `logs/`, and `backups/`: runtime or local data; not source files.',
        '- No files were moved or deleted. Existing imports, routes, and path conventions remain intact.',
        '',
        '## Scan results',
        '',
        f'- Required project entries missing: **{len(missing_required)}**',
        f'- Python syntax errors: **{len(syntax_errors)}**',
        f'- Broken local imports: **{len(broken_imports)}**',
        f'- Potential circular import groups: **{len(cycles)}**',
        f'- Python-referenced templates missing: **{len(missing_templates)}**',
        f'- Referenced local assets missing: **{len(missing_assets)}**',
        f'- Apps missing a migrations package: **{len(app_migrations)}**',
        f'- Exact duplicate source groups: **{len(duplicates)}**',
        f'- Heuristic unreferenced asset candidates: **{len(unreferenced)}**',
        '',
        '### Required entries',
        '',
    ]
    lines.extend([f'- Missing: `{item}`' for item in missing_required] or ['- All required entries are present.'])
    sections = (
        ('Python syntax errors', syntax_errors),
        ('Broken local imports', broken_imports),
        ('Potential circular import groups', [' → '.join(group) for group in cycles]),
        ('Missing templates', missing_templates),
        ('Missing asset paths', missing_assets),
        ('Apps missing migrations', app_migrations),
    )
    for title, findings in sections:
        lines.extend(['', f'### {title}', ''])
        lines.extend([f'- {item}' for item in findings] or ['- None detected.'])
    lines.extend(['', '### Exact duplicate source files', ''])
    lines.extend(['- ' + ', '.join(f'`{path}`' for path in group) for group in duplicates] or ['- None detected outside generated `site/` output.'])
    lines.extend([
        '',
        '### Unreferenced asset candidates',
        '',
        'This filename search is intentionally conservative and can miss dynamic references or produce false positives. Verify each candidate manually; nothing is removed.',
    ])
    lines.extend([f'- `{path}`' for path in unreferenced] or ['- None detected.'])
    lines.extend([
        '',
        '## Scan limits',
        '',
        '- Import analysis covers local `config` and `jobs` module imports; dynamic imports and runtime plugin resolution are not inferred.',
        '- Template checks match template basenames and cannot prove every runtime-selected template branch.',
        '- Asset checks cover local HTML `src`/`href` and CSS `url(...)` references; JavaScript-generated paths and remote assets require browser/network testing.',
        '- Django routes, database behavior, authentication flows, upload behavior, admin access, and browser rendering require application tests and live preview checks.',
        '- Generated static output under `site/` is intentionally omitted because it mirrors source files by design.',
        '',
    ])

    output = (ROOT / args.output).resolve()
    output.write_text('\n'.join(lines), encoding='utf-8')
    print(f'Wrote {output.relative_to(ROOT)}')
    print(
        f'Found {len(missing_required)} missing required entries, {len(syntax_errors)} syntax errors, '
        f'{len(broken_imports)} broken imports, and {len(missing_assets)} missing local asset paths.'
    )
    if args.check and any((missing_required, syntax_errors, broken_imports, missing_templates, missing_assets, app_migrations)):
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
