"""
One-shot Step-1 organizer. Moves files (no deletes). Logs every action.
Does not touch .env, database/, private_media/, or overwrite secrets.
"""
from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG: list[dict] = []
stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def log(action: str, src: str = "", dst: str = "", note: str = "") -> None:
    LOG.append({"action": action, "src": src, "dst": dst, "note": note})
    print(f"{action}: {src} -> {dst} {note}".strip())


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    log("mkdir", "", str(path.relative_to(ROOT)))


def move_path(src: Path, dst: Path) -> None:
    if not src.exists():
        log("skip-missing", str(src.relative_to(ROOT)), str(dst.relative_to(ROOT)))
        return
    if dst.exists():
        log("skip-exists", str(src.relative_to(ROOT)), str(dst.relative_to(ROOT)), "destination exists")
        return
    ensure_dir(dst.parent)
    shutil.move(str(src), str(dst))
    log("move", str(src.relative_to(ROOT)), str(dst.relative_to(ROOT)))


def write_wrapper_bat(root_name: str, target_rel: str) -> None:
    """Keep root .bat names working by delegating to scripts/."""
    wrapper = ROOT / root_name
    body = (
        "@echo off\r\n"
        "setlocal\r\n"
        f'call "%~dp0{target_rel}" %*\r\n'
        "exit /b %ERRORLEVEL%\r\n"
    )
    # Only write wrapper if original was moved (target exists) and wrapper missing or we replace after move
    wrapper.write_text(body, encoding="utf-8")
    log("wrapper", root_name, target_rel)


def main() -> int:
    # --- Target skeleton ---
    for d in [
        "frontend/pages",
        "frontend/css",
        "frontend/js",
        "frontend/assets/images",
        "frontend/assets/logos",
        "frontend/assets/icons",
        "frontend/assets/videos",
        "backend",
        "docs/architecture",
        "docs/setup",
        "docs/troubleshooting",
        "docs/reports",
        "docs/development",
        "scripts/install",
        "scripts/startup",
        "scripts/maintenance",
        "scripts/backup",
        "scripts/diagnostics",
        "tests/frontend",
        "tests/backend",
        "tests/integration",
        "assets/images",
        "assets/logos",
        "assets/icons",
    ]:
        ensure_dir(ROOT / d)

    # --- Frontend moves (preserve URL space via settings later) ---
    move_path(ROOT / "pages", ROOT / "frontend" / "pages")
    move_path(ROOT / "css", ROOT / "frontend" / "css")
    move_path(ROOT / "js", ROOT / "frontend" / "js")
    move_path(ROOT / "images", ROOT / "frontend" / "assets" / "images")
    move_path(ROOT / "logo", ROOT / "frontend" / "assets" / "logos")
    move_path(ROOT / "videos", ROOT / "frontend" / "assets" / "videos")

    # Compatibility junctions/symlinks at old paths so any missed refs keep working.
    # On Windows use directory junctions (no admin required for junctions).
    def junction(link: Path, target: Path) -> None:
        if link.exists():
            log("skip-link", str(link.relative_to(ROOT)), str(target.relative_to(ROOT)), "link path exists")
            return
        if not target.exists():
            log("skip-link", str(link.relative_to(ROOT)), str(target.relative_to(ROOT)), "target missing")
            return
        import subprocess

        # mklink /J link target
        cmd = ["cmd", "/c", "mklink", "/J", str(link), str(target)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode == 0:
            log("junction", str(link.relative_to(ROOT)), str(target.relative_to(ROOT)), proc.stdout.strip())
        else:
            log("junction-fail", str(link.relative_to(ROOT)), str(target.relative_to(ROOT)), proc.stderr.strip())

    junction(ROOT / "pages", ROOT / "frontend" / "pages")
    junction(ROOT / "css", ROOT / "frontend" / "css")
    junction(ROOT / "js", ROOT / "frontend" / "js")
    junction(ROOT / "images", ROOT / "frontend" / "assets" / "images")
    junction(ROOT / "logo", ROOT / "frontend" / "assets" / "logos")
    junction(ROOT / "videos", ROOT / "frontend" / "assets" / "videos")

    # --- Docs classification (move from root; keep README.md / START_HERE.md at root) ---
    doc_map = {
        "docs/architecture": [
            "PROJECT_LAYOUT.md",
            "PROJECT_STRUCTURE_REPORT.md",
            "TALENTBRIDGEAI_PAGE_DIRECTORY.md",
            "TALENTBRIDGEAI_DEVELOPMENT_PLAN.md",
            "TALENTBRIDGEAI_IMPLEMENTATION_PLAN.md",
            "PYTHON_CONNECTIVITY_AUDIT.md",
        ],
        "docs/setup": [
            "README_RUN_DJANGO.md",
            "README_FRESH_INSTALL.md",
            "README_SIGNIN_SIGNUP.md",
            "GOOGLE_OAUTH_SETUP.md",
            "EMAIL_VERIFICATION_SETUP.md",
            "NOTIFICATION_SETUP.md",
            "LIVE_PREVIEW_SETUP.md",
            "LIVE_PREVIEW_README.md",
            "STARTUP_README.md",
            "PORTABLE_INSTALLATION_GUIDE.md",
            "VSCODE_AUTO_SETUP.md",
            "INSTALL.txt",
            "AUTOMATIC_SETUP_README.txt",
            "AUTO_FOLDER_SWITCH_SETUP.txt",
            "AUTO_UPDATE_ON_OPEN_README.txt",
            "PERMANENT_FIRST_OPEN_SETUP_HI.txt",
            "SERVER_DETAILS.txt",
        ],
        "docs/troubleshooting": [
            "DATABASE_SETUP_FIX.md",
            "DJANGO_DEFAULT_PREVIEW_FIX.md",
            "SERVER_PERSISTENCE_FIX.md",
            "PORTABLE_SERVER_OWNERSHIP_FIX.md",
            "LOGIN_VISUAL_FIX_NOTES.md",
            "INTERRUPTION_RECOVERY.md",
            "DATA_PROTECTION_GUIDE.md",
            "BACKUP_GUIDE.md",
            "AUTO_FOLDER_SWITCH_FIX_v3.txt",
            "LOGIN_AND_AUTOSTART_REPAIR.txt",
            "GOOGLE_NOTICE_PATCH_REPORT.txt",
            "GOOGLE_NOTICE_REPAIR_REPORT.txt",
            "OAUTH_FINAL_SOURCE.txt",
            "UPDATE_VALIDATION.txt",
        ],
        "docs/reports": [
            "TALENTBRIDGEAI_AUDIT_REPORT.md",
            "TALENTBRIDGEAI_PROJECT_AUDIT.md",
            "TALENTBRIDGEAI_PROGRESS.md",
            "TALENTBRIDGEAI_RESUME_PROGRESS.md",
            "DELIVERY_STATUS.md",
            "DEMO_DATA_AND_QA.md",
            "OAUTH_IMPLEMENTATION_QA.md",
            "STEP2_CHANGE_REPORT.md",
            "STEP2_TEST_REPORT.md",
            "LIVE_PREVIEW_PROGRESS.md",
            "DEVELOPMENT_PROGRESS.md",
            "ACTIVITY_NOW.md",
            "CLIENT_DEMO_README.md",
            "ZIP_RELEASE_GUIDE.md",
            "TALENTBRIDGEAI_COMPLETE_CHANGE_REPORT.txt",
            "TALENTBRIDGEAI_COMPLETE_CHANGE_REPORT.pdf",
        ],
        "docs/development": [
            "PYTHON_CONNECTIVITY_AUDIT.md",
        ],
    }
    # Fix duplicate - PYTHON only in architecture
    doc_map["docs/development"] = [
        "ACTIVITY_NOW.md",  # also in reports - prefer reports only
    ]
    # Rebuild development list cleanly
    doc_map["docs/development"] = [
        "DEVELOPMENT_PROGRESS.md",
        "LIVE_PREVIEW_PROGRESS.md",
        "TALENTBRIDGEAI_PROGRESS.md",
        "TALENTBRIDGEAI_RESUME_PROGRESS.md",
        "TALENTBRIDGEAI_DEVELOPMENT_PLAN.md",
        "TALENTBRIDGEAI_IMPLEMENTATION_PLAN.md",
    ]
    # Remove those from reports/architecture if duplicated
    for key in ("docs/reports", "docs/architecture"):
        doc_map[key] = [f for f in doc_map[key] if f not in doc_map["docs/development"]]

    moved_docs = set()
    for dest_rel, names in doc_map.items():
        dest = ROOT / dest_rel
        for name in names:
            if name in moved_docs:
                continue
            src = ROOT / name
            if src.exists() and src.is_file():
                move_path(src, dest / name)
                moved_docs.add(name)

    # Move remaining root *.md except keep list into docs/reports
    keep_root = {"README.md", "START_HERE.md"}
    for md in ROOT.glob("*.md"):
        if md.name in keep_root or md.name.startswith("TALENTBRIDGEAI_FILE_") or md.name.startswith("TALENTBRIDGEAI_NEW_") or md.name.startswith("TALENTBRIDGEAI_STEP"):
            continue
        if md.name in moved_docs:
            continue
        move_path(md, ROOT / "docs" / "reports" / md.name)
        moved_docs.add(md.name)

    # Remaining root *.txt into docs/troubleshooting except keep none critical
    keep_txt = set()
    for txt in ROOT.glob("*.txt"):
        if txt.name in keep_txt or txt.name in moved_docs:
            continue
        # Skip if already under docs
        move_path(txt, ROOT / "docs" / "troubleshooting" / txt.name)
        moved_docs.add(txt.name)

    # Existing docs/* files stay; optional nested already there

    # --- Scripts ---
    script_map = {
        "scripts/install": [
            "INSTALL_TALENTBRIDGEAI.bat",
            "FIRST_RUN_OR_UPDATE.bat",
            "SETUP_AND_RUN_WINDOWS.bat",
            "CREATE_SUPERUSER.bat",
            "CREATE_ADMIN_AND_START.bat",
            "REPLACE_SUPERUSER.bat",
            "CONNECT_GOOGLE_OAUTH.bat",
            "CONNECT_GOOGLE_OAUTH.ps1",
        ],
        "scripts/startup": [
            "START_TALENTBRIDGEAI.bat",
            "START_TALENTBRIDGEAI_HIDDEN.vbs",
            "STOP_TALENTBRIDGEAI.bat",
            "RESTART_TALENTBRIDGEAI.bat",
            "OPEN_DJANGO_WEBSITE.bat",
            "RUN_DJANGO_WINDOWS.bat",
            "ENABLE_AUTO_STARTUP.bat",
            "DISABLE_AUTO_STARTUP.bat",
            "DISABLE_AUTO_SERVER_STARTUP.bat",
            "APPLY_UPDATE_PRESERVE_DATA.bat",
            "APPLY_UPDATE_PRESERVE_DATA.ps1",
            "AUTO_UPDATE_PRESERVE_DATA.ps1",
        ],
        "scripts/maintenance": [
            "UPDATE_TALENTBRIDGEAI.bat",
            "REPAIR_TALENTBRIDGEAI.bat",
            "FIX_SERVER_PERMANENTLY.bat",
            "FIX_TALENTBRIDGEAI_SERVER_NOW.bat",
            "FIX_STATIC_PREVIEW_BANNER.bat",
            "FIX_STATIC_PREVIEW_BANNER.ps1",
            "APPLY_TALENTBRIDGE_GOOGLE_NOTICE_FIX.bat",
        ],
        "scripts/backup": [
            "CREATE_BACKUP.bat",
            "CREATE_PORTABLE_RELEASE.bat",
        ],
        "scripts/diagnostics": [
            "CHECK_DJANGO_SERVER.bat",
            "CHECK_STATUS.bat",
            "DIAGNOSE_TALENTBRIDGEAI.bat",
            "FINAL_CLIENT_DEMO.bat",
        ],
    }
    moved_scripts = set()
    for dest_rel, names in script_map.items():
        for name in names:
            src = ROOT / name
            dst = ROOT / dest_rel / name
            if src.exists():
                move_path(src, dst)
                moved_scripts.add(name)
                if name.endswith(".bat"):
                    write_wrapper_bat(name, f"{dest_rel}\\{name}".replace("/", "\\"))

    # --- Backend: move Django project (exclude .venv live move via rename of children) ---
    src_django = ROOT / "legacy-django"
    dst_django = ROOT / "backend" / "legacy-django"
    if src_django.exists() and not dst_django.exists():
        ensure_dir(dst_django)
        for child in list(src_django.iterdir()):
            # Move everything including .venv (logged); Windows may need path rewrite later
            move_path(child, dst_django / child.name)
        # Remove empty legacy-django dir if empty, then junction
        try:
            src_django.rmdir()
            log("rmdir-empty", "legacy-django", "", "empty after move")
        except OSError as exc:
            log("rmdir-fail", "legacy-django", "", str(exc))
        junction(ROOT / "legacy-django", dst_django)

    # tests README pointers (no duplicate of Django tests)
    readme = ROOT / "tests" / "README.md"
    if not readme.exists():
        readme.write_text(
            "# Tests layout\n\n"
            "- Backend Django tests remain inside `backend/legacy-django/jobs/` "
            "(Django discovery). Do not duplicate them here.\n"
            "- `tests/frontend/`: future UI/link checks.\n"
            "- `tests/integration/`: future cross-layer checks.\n"
            "- Root `_check_links.py` remains a repo-level link checker.\n",
            encoding="utf-8",
        )
        log("write", "", "tests/README.md")

    # Pointer READMEs for assets/
    for rel, text in [
        (
            "assets/README.md",
            "Canonical visual assets live under `frontend/assets/`. "
            "This folder is reserved for shared non-frontend packaging assets; "
            "do not duplicate images here.\n",
        ),
        (
            "frontend/README.md",
            "Frontend sources: `pages/`, `css/`, `js/`, `assets/`. "
            "Served by Django URL routes `/pages/`, `/css/`, `/js/`, `/images/`.\n",
        ),
        (
            "backend/README.md",
            "Django project: `legacy-django/`. Virtualenv: `legacy-django/.venv`.\n"
            "Repo root still has a `legacy-django` junction for compatibility.\n",
        ),
        (
            "scripts/README.md",
            "Operational scripts by category. Root `*.bat` wrappers call into these folders.\n",
        ),
    ]:
        path = ROOT / rel
        if not path.exists():
            path.write_text(text, encoding="utf-8")
            log("write", "", rel)

    out = ROOT / "backups" / f"structure_20261118_002618" / f"move_log_{stamp}.json"
    # fallback if backup folder naming differs
    backup_dirs = sorted((ROOT / "backups").glob("structure_*"))
    if backup_dirs:
        out = backup_dirs[-1] / f"move_log_{stamp}.json"
    else:
        out = ROOT / f"move_log_{stamp}.json"
    out.write_text(json.dumps(LOG, indent=2), encoding="utf-8")
    print(f"LOG_WRITTEN={out}")
    print(f"ACTIONS={len(LOG)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
