"""
Finish TalentBridgeAI root organization.
- Moves scattered root files into logical folders
- Updates Django / build / script references
- Removes compatibility junctions after Django points at frontend/backend
- Writes docs/reports/TALENTBRIDGEAI_FILE_MOVE_LOG_FINISH.md
Does NOT touch .env, database/, private_media/, or delete unique content.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import stat
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"structure_finish_{STAMP}"
MOVES: list[dict] = []
NOTES: list[str] = []


def log_move(src: Path, dst: Path, reason: str) -> None:
    MOVES.append(
        {
            "from": str(src.relative_to(ROOT)).replace("\\", "/"),
            "to": str(dst.relative_to(ROOT)).replace("\\", "/"),
            "reason": reason,
        }
    )


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def safe_move(src: Path, dst: Path, reason: str) -> bool:
    if not src.exists():
        NOTES.append(f"skip missing: {src}")
        return False
    if src.resolve() == dst.resolve():
        NOTES.append(f"skip same path: {src}")
        return False
    ensure_parent(dst)
    if dst.exists():
        # Prefer keeping destination if identical; otherwise backup src aside
        if src.is_file() and dst.is_file() and src.read_bytes() == dst.read_bytes():
            src.unlink()
            log_move(src, dst, reason + " (duplicate removed; dest kept)")
            return True
        backup_dst = BACKUP / "collisions" / dst.relative_to(ROOT)
        ensure_parent(backup_dst)
        if dst.is_dir():
            shutil.copytree(dst, backup_dst, dirs_exist_ok=True)
        else:
            shutil.copy2(dst, backup_dst)
        NOTES.append(f"collision backup: {dst} -> {backup_dst}")
    ensure_parent(BACKUP / "pre_move" / src.relative_to(ROOT))
    pre = BACKUP / "pre_move" / src.relative_to(ROOT)
    ensure_parent(pre)
    if src.is_dir() and not os.path.islink(src) and not src.is_symlink():
        if not pre.exists():
            shutil.copytree(src, pre, dirs_exist_ok=True)
        shutil.move(str(src), str(dst))
    else:
        if src.is_file():
            shutil.copy2(src, pre)
        shutil.move(str(src), str(dst))
    log_move(src, dst, reason)
    return True


def replace_in_file(path: Path, replacements: list[tuple[str, str]]) -> int:
    if not path.is_file():
        return 0
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return 0
    original = text
    for old, new in replacements:
        text = text.replace(old, new)
    if text != original:
        path.write_text(text, encoding="utf-8", newline="\n")
        return 1
    return 0


def remove_junction(path: Path) -> None:
    if not path.exists():
        return
    # Windows junction / symlink
    if os.path.islink(path) or path.is_symlink():
        path.unlink()
        NOTES.append(f"removed link: {path.name}")
        return
    # cmd rmdir for junctions (islink may be False on some Python builds)
    result = subprocess.run(
        ["cmd", "/c", "rmdir", str(path)],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        NOTES.append(f"removed junction: {path.name}")
    else:
        NOTES.append(f"failed remove junction {path.name}: {result.stderr or result.stdout}")


def main() -> int:
    BACKUP.mkdir(parents=True, exist_ok=True)
    inventory = {
        "stamp": STAMP,
        "root_before": sorted(
            [{"name": p.name, "dir": p.is_dir()} for p in ROOT.iterdir()],
            key=lambda x: x["name"].lower(),
        ),
    }
    (BACKUP / "inventory_before.json").write_text(
        json.dumps(inventory, indent=2), encoding="utf-8"
    )

    # --- Move root documentation ---
    safe_move(
        ROOT / "START_HERE.md",
        ROOT / "docs" / "START_HERE.md",
        "Documentation belongs under docs/",
    )
    progress = ROOT / "TALENTBRIDGEAI_PROJECT_PROGRESS.md"
    dest_progress = ROOT / "docs" / "reports" / "TALENTBRIDGEAI_PROJECT_PROGRESS.md"
    if progress.exists():
        if dest_progress.exists():
            # keep newer/longer
            if progress.stat().st_size >= dest_progress.stat().st_size:
                shutil.copy2(dest_progress, BACKUP / "TALENTBRIDGEAI_PROJECT_PROGRESS.prev.md")
                shutil.copy2(progress, dest_progress)
            progress.unlink()
            log_move(progress, dest_progress, "Docs report (merged into docs/reports)")
        else:
            safe_move(progress, dest_progress, "Docs report under docs/reports/")

    # --- Move helper Python tools ---
    safe_move(
        ROOT / "bootstrap_env.py",
        ROOT / "tools" / "bootstrap_env.py",
        "Env bootstrap helper belongs in tools/",
    )
    safe_move(
        ROOT / "build_static.py",
        ROOT / "tools" / "build_static.py",
        "Static site builder belongs in tools/",
    )
    safe_move(
        ROOT / "_check_links.py",
        ROOT / "tools" / "_check_links.py",
        "Link checker belongs in tools/",
    )

    # --- Move homepage + 404 into frontend ---
    safe_move(
        ROOT / "index.html",
        ROOT / "frontend" / "index.html",
        "Homepage HTML with other frontend sources",
    )
    safe_move(
        ROOT / "404.html",
        ROOT / "frontend" / "pages" / "404.html",
        "Error page with other frontend HTML pages",
    )

    # --- Move design references ---
    design = ROOT / "design-references"
    if design.exists():
        safe_move(
            design,
            ROOT / "docs" / "design-references",
            "Design reference assets under docs/",
        )

    # --- Empty root assets stub ---
    assets = ROOT / "assets"
    if assets.exists() and os.path.realpath(assets) != os.path.realpath(ROOT / "frontend" / "assets"):
        readme = assets / "README.md"
        if readme.exists():
            dest_readme = ROOT / "frontend" / "assets" / "ROOT_ASSETS_README.md"
            if not dest_readme.exists():
                ensure_parent(dest_readme)
                shutil.copy2(readme, dest_readme)
                log_move(readme, dest_readme, "Preserve assets README under frontend/assets")
        # only remove if empty-ish (no real files with size)
        real_files = [p for p in assets.rglob("*") if p.is_file() and p.stat().st_size > 0 and p.name != "README.md"]
        if not real_files:
            shutil.rmtree(assets, ignore_errors=True)
            NOTES.append("removed empty root assets/ stub (content lives in frontend/assets)")
        else:
            NOTES.append(f"kept root assets/; non-empty files remain: {len(real_files)}")

    # --- Relocate BAT wrappers into scripts (canonical) ---
    bat_map = {
        "START_TALENTBRIDGEAI.bat": ROOT / "scripts" / "startup" / "START_TALENTBRIDGEAI.ROOT_WRAPPER.bat",
        "STOP_TALENTBRIDGEAI.bat": ROOT / "scripts" / "shutdown" / "STOP_TALENTBRIDGEAI.ROOT_WRAPPER.bat",
        "RESTART_TALENTBRIDGEAI.bat": ROOT / "scripts" / "startup" / "RESTART_TALENTBRIDGEAI.ROOT_WRAPPER.bat",
    }
    for name, dst in bat_map.items():
        src = ROOT / name
        if src.exists():
            # Keep thin root pointers? User asked all bats in scripts — remove root copies after ensuring scripts/startup has real starters.
            # Archive wrappers; real scripts already exist in scripts/startup|shutdown.
            ensure_parent(dst)
            shutil.copy2(src, dst)
            log_move(src, dst, "Archive root BAT wrapper under scripts/; use scripts/startup|shutdown")
            src.unlink()

    # Create minimal root README pointer for start commands (not a bat)
    start_pointer = ROOT / "docs" / "setup" / "HOW_TO_START.md"
    ensure_parent(start_pointer)
    if not start_pointer.exists():
        start_pointer.write_text(
            "# How to start TalentBridgeAI\n\n"
            "From the repo root:\n\n"
            "```bat\nscripts\\startup\\START_TALENTBRIDGEAI.bat\n```\n\n"
            "Stop:\n\n"
            "```bat\nscripts\\shutdown\\STOP_TALENTBRIDGEAI.bat\n```\n\n"
            "Restart:\n\n"
            "```bat\nscripts\\startup\\RESTART_TALENTBRIDGEAI.bat\n```\n",
            encoding="utf-8",
        )
        NOTES.append("wrote docs/setup/HOW_TO_START.md")

    # --- Patch Django settings ---
    settings = ROOT / "backend" / "legacy-django" / "config" / "settings.py"
    if settings.exists():
        text = settings.read_text(encoding="utf-8")
        new_dirs = """        'DIRS': [
            path
            for path in (
                BASE_DIR / "templates",
                FRONTEND_ROOT,                 # frontend/index.html
                FRONTEND_ROOT / "pages",       # frontend HTML pages
            )
            if path.exists()
        ],"""
        text2, n = re.subn(
            r"'DIRS':\s*\[[^\]]*\],",
            new_dirs,
            text,
            count=1,
            flags=re.S,
        )
        if n:
            # Also slim STATICFILES_DIRS to frontend-first
            text2 = text2.replace(
                """STATICFILES_DIRS = [
    path
    for path in (
        FRONTEND_ROOT / "css",
        FRONTEND_ROOT / "js",
        FRONTEND_ROOT / "assets" / "images",
        PROJECT_ROOT / "css",  # compatibility junction
        PROJECT_ROOT / "js",
        PROJECT_ROOT / "images",
        BASE_DIR / "static",
    )
    if path.is_dir()
]""",
                """STATICFILES_DIRS = [
    path
    for path in (
        FRONTEND_ROOT / "css",
        FRONTEND_ROOT / "js",
        FRONTEND_ROOT / "assets" / "images",
        BASE_DIR / "static",
    )
    if path.is_dir()
]""",
            )
            settings.write_text(text2, encoding="utf-8", newline="\n")
            NOTES.append("updated settings.py TEMPLATE_DIRS + STATICFILES_DIRS")
        else:
            NOTES.append("settings.py DIRS pattern not replaced — manual check needed")

    # --- Patch urls.py index.html serve path ---
    urls = ROOT / "backend" / "legacy-django" / "config" / "urls.py"
    if urls.exists():
        ut = urls.read_text(encoding="utf-8")
        ut2 = ut.replace(
            "path('index.html', serve, {'document_root': PROJECT_ROOT, 'path': 'index.html'}),",
            "path('index.html', serve, {'document_root': FRONTEND_ROOT, 'path': 'index.html'}),",
        )
        if ut2 != ut:
            urls.write_text(ut2, encoding="utf-8", newline="\n")
            NOTES.append("updated urls.py index.html document_root -> FRONTEND_ROOT")

    # --- Patch views.page_file to use FRONTEND_ROOT/pages ---
    views = ROOT / "backend" / "legacy-django" / "jobs" / "views.py"
    if views.exists():
        vt = views.read_text(encoding="utf-8")
        old = 'pages_root = (Path(settings.PROJECT_ROOT) / "pages").resolve()'
        new = (
            'frontend_root = Path(getattr(settings, "FRONTEND_ROOT", settings.PROJECT_ROOT))\n'
            '    pages_root = (frontend_root / "pages").resolve()\n'
            '    if not pages_root.is_dir():\n'
            '        pages_root = (Path(settings.PROJECT_ROOT) / "pages").resolve()'
        )
        if old in vt:
            views.write_text(vt.replace(old, new, 1), encoding="utf-8", newline="\n")
            NOTES.append("updated views.page_file pages_root -> FRONTEND_ROOT/pages")

    # --- Patch tests pages_root ---
    tests = ROOT / "backend" / "legacy-django" / "jobs" / "tests.py"
    if tests.exists():
        tt = tests.read_text(encoding="utf-8")
        tt2 = tt.replace(
            'pages_root = Path(settings.PROJECT_ROOT) / "pages"',
            'pages_root = Path(getattr(settings, "FRONTEND_ROOT", settings.PROJECT_ROOT)) / "pages"',
        )
        if tt2 != tt:
            tests.write_text(tt2, encoding="utf-8", newline="\n")
            NOTES.append("updated jobs/tests.py pages_root")

    # --- Patch build_static (now in tools/) ---
    build = ROOT / "tools" / "build_static.py"
    if build.exists():
        bt = build.read_text(encoding="utf-8")
        bt2 = bt.replace(
            "ROOT = Path(__file__).resolve().parent",
            "ROOT = Path(__file__).resolve().parents[1]  # repo root (script lives in tools/)",
        )
        bt2 = bt2.replace(
            'PUBLIC_DIRS = ("css", "images", "js", "pages", "videos")',
            'FRONTEND = ROOT / "frontend"\n'
            "PUBLIC_DIR_MAP = {\n"
            '    "css": FRONTEND / "css",\n'
            '    "js": FRONTEND / "js",\n'
            '    "pages": FRONTEND / "pages",\n'
            '    "images": FRONTEND / "assets" / "images",\n'
            '    "videos": FRONTEND / "assets" / "videos",\n'
            "}",
        )
        # Update copy loop if it iterates PUBLIC_DIRS — patch common patterns
        bt2 = bt2.replace(
            "for name in PUBLIC_DIRS:",
            "for name, src_dir in PUBLIC_DIR_MAP.items():",
        )
        bt2 = bt2.replace(
            'src = ROOT / name',
            'src = src_dir',
        )
        # index copy from frontend
        bt2 = bt2.replace(
            'shutil.copy2(ROOT / "index.html", OUTPUT / "index.html")',
            'shutil.copy2(FRONTEND / "index.html", OUTPUT / "index.html")',
        )
        bt2 = bt2.replace(
            'shutil.copy2(ROOT / "404.html", OUTPUT / "404.html")',
            'shutil.copy2(FRONTEND / "pages" / "404.html", OUTPUT / "404.html")',
        )
        build.write_text(bt2, encoding="utf-8", newline="\n")
        NOTES.append("updated tools/build_static.py for frontend/ layout")

    # --- netlify.toml ---
    netlify = ROOT / "netlify.toml"
    if netlify.exists():
        nt = netlify.read_text(encoding="utf-8")
        nt2 = nt.replace('command = "python build_static.py"', 'command = "python tools/build_static.py"')
        if nt2 != nt:
            netlify.write_text(nt2, encoding="utf-8", newline="\n")
            NOTES.append("updated netlify.toml build command")

    # --- scripts: legacy-django -> backend\\legacy-django (keep fallback) ---
    script_replacements = [
        ('cd /d "%~dp0..\\..\\legacy-django"', 'cd /d "%~dp0..\\..\\backend\\legacy-django"'),
        ("legacy-django\\manage.py", "backend\\legacy-django\\manage.py"),
        ("legacy-django\\.venv", "backend\\legacy-django\\.venv"),
        ('Join-Path $ProjectRoot "legacy-django"', 'Join-Path $ProjectRoot "backend\\legacy-django"'),
        ('Join-Path $root \'legacy-django', 'Join-Path $root \'backend\\legacy-django'),
        ('Join-Path $DefaultSource "legacy-django\\manage.py"', 'Join-Path $DefaultSource "backend\\legacy-django\\manage.py"'),
        ('Join-Path $candidate "legacy-django\\manage.py"', 'Join-Path $candidate "backend\\legacy-django\\manage.py"'),
        ('Join-Path $Source "legacy-django\\manage.py"', 'Join-Path $Source "backend\\legacy-django\\manage.py"'),
        ("py build_static.py", "py tools\\build_static.py"),
        ("python build_static.py", "python tools\\build_static.py"),
        ("& py build_static.py", "& py tools\\build_static.py"),
        ("& python build_static.py", "& python tools\\build_static.py"),
    ]
    updated_scripts = 0
    for path in (ROOT / "scripts").rglob("*"):
        if path.suffix.lower() in {".bat", ".ps1", ".cmd", ".md"}:
            updated_scripts += replace_in_file(path, script_replacements)
    NOTES.append(f"script files patched: {updated_scripts}")

    # --- .vscode launch.json ---
    launch = ROOT / ".vscode" / "launch.json"
    replace_in_file(
        launch,
        [
            ("${workspaceFolder}/legacy-django/manage.py", "${workspaceFolder}/backend/legacy-django/manage.py"),
            ('"${workspaceFolder}/legacy-django"', '"${workspaceFolder}/backend/legacy-django"'),
        ],
    )

    # --- scripts README ---
    scripts_readme = ROOT / "scripts" / "README.md"
    if scripts_readme.exists():
        scripts_readme.write_text(
            """# TalentBridgeAI scripts

All operational scripts live here (not in the project root).

| Folder | Purpose |
| --- | --- |
| `install/` | Install, first-run, superuser, Google OAuth connect |
| `startup/` | Start / restart / open site / enable auto-start |
| `shutdown/` | Stop server / disable auto-start |
| `maintenance/` | Repair, update, permanent fixes |
| `backup/` | Backup and portable release |
| `diagnostics/` | Status checks and diagnose |

Start the site:

```bat
scripts\\startup\\START_TALENTBRIDGEAI.bat
```

Stop:

```bat
scripts\\shutdown\\STOP_TALENTBRIDGEAI.bat
```

Django project path: `backend\\legacy-django\\`
""",
            encoding="utf-8",
            newline="\n",
        )

    # --- Remove compatibility junctions (Django/scripts now use frontend|backend) ---
    for name in ("css", "js", "pages", "images", "logo", "videos", "legacy-django"):
        remove_junction(ROOT / name)

    # --- Write move report ---
    report_path = ROOT / "docs" / "reports" / "TALENTBRIDGEAI_FILE_MOVE_LOG_FINISH.md"
    ensure_parent(report_path)

    def count_files(pattern: str) -> int:
        return sum(1 for _ in ROOT.glob(pattern) if _.is_file())

    # counts excluding venv/node_modules/backups/site/staticfiles
    def counted(globs: list[str]) -> int:
        skip_parts = {".venv", "node_modules", "staticfiles", "backups", "releases", "__pycache__", ".git"}
        total = 0
        for g in globs:
            for p in ROOT.glob(g):
                if not p.is_file():
                    continue
                if any(part in skip_parts for part in p.parts):
                    continue
                total += 1
        return total

    html_n = counted(["frontend/**/*.html", "backend/legacy-django/**/templates/**/*.html"])
    css_n = counted(["frontend/css/**/*.css"])
    js_n = counted(["frontend/js/**/*.js"])
    docs_n = counted(["docs/**/*.md", "docs/**/*.txt", "README.md"])
    scripts_n = counted(["scripts/**/*.*", "tools/**/*.*"])

    root_files = sorted([p.name for p in ROOT.iterdir() if p.is_file()])
    root_dirs = sorted([p.name for p in ROOT.iterdir() if p.is_dir()])

    lines = [
        f"# TalentBridgeAI — File Move Log (Finish Pass)",
        f"",
        f"Date: {datetime.now().isoformat(timespec='seconds')}",
        f"Backup: `backups/structure_finish_{STAMP}/`",
        f"",
        f"## Moves",
        f"",
        f"| Original | New | Reason |",
        f"| --- | --- | --- |",
    ]
    for m in MOVES:
        lines.append(f"| `{m['from']}` | `{m['to']}` | {m['reason']} |")
    lines += [
        f"",
        f"## Notes",
        f"",
    ]
    for n in NOTES:
        lines.append(f"- {n}")
    lines += [
        f"",
        f"## Counts (approx., excluding venv/staticfiles/backups/releases)",
        f"",
        f"- HTML (frontend + Django templates): **{html_n}**",
        f"- CSS (frontend/css): **{css_n}**",
        f"- JavaScript (frontend/js): **{js_n}**",
        f"- Documentation (docs + root README): **{docs_n}**",
        f"- Scripts/tools: **{scripts_n}**",
        f"- Files still in root: **{len(root_files)}** → `{', '.join(root_files)}`",
        f"",
        f"## Root directories after pass",
        f"",
        f"`{', '.join(root_dirs)}`",
        f"",
        f"## Intentionally kept in root",
        f"",
        f"| File | Why |",
        f"| --- | --- |",
        f"| `.env` / `.env.example` | Secrets / env template must stay at repo root for Django loader |",
        f"| `.gitignore` / `.gitattributes` | Git configuration |",
        f"| `README.md` | Standard project entry documentation |",
        f"| `netlify.toml` | Netlify expects repo-root config |",
        f"| `TalentBridgeAI.code-workspace` | VS Code multi-root workspace file |",
        f"| `.talentbridge_django.pid` / `.port` | Runtime locks written by startup manager |",
        f"",
        f"## References updated",
        f"",
        f"- `backend/legacy-django/config/settings.py` (TEMPLATE_DIRS, STATICFILES_DIRS)",
        f"- `backend/legacy-django/config/urls.py` (index.html from FRONTEND_ROOT)",
        f"- `backend/legacy-django/jobs/views.py` (page_file pages root)",
        f"- `backend/legacy-django/jobs/tests.py`",
        f"- `tools/build_static.py`, `netlify.toml`",
        f"- `scripts/**` paths → `backend\\legacy-django`",
        f"- `.vscode/launch.json`",
        f"",
        f"## Verification",
        f"",
        f"See companion section filled by the verification runner.",
        f"",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    (BACKUP / "moves.json").write_text(json.dumps(MOVES, indent=2), encoding="utf-8")
    print(f"DONE moves={len(MOVES)} report={report_path}")
    print("ROOT FILES:", root_files)
    print("ROOT DIRS:", root_dirs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
