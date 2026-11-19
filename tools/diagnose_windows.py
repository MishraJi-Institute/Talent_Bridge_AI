#!/usr/bin/env python3
"""Collect non-secret local diagnostics for TalentBridgeAI startup failures."""
from __future__ import annotations
import os, platform, shutil, socket, subprocess, sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
DJANGO = ROOT / 'legacy-django'
VENV_PY = DJANGO / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
DB = ROOT / 'database' / 'TalentBridgeAI.sqlite3'
LOGS = ROOT / 'logs'
LOGS.mkdir(exist_ok=True)
OUT = LOGS / 'diagnostic_report.txt'

def port_status(port: int) -> str:
    with socket.socket() as s:
        s.settimeout(.5)
        return 'LISTENING' if s.connect_ex(('127.0.0.1', port)) == 0 else 'NOT LISTENING'

def tail(path: Path, lines: int = 35) -> str:
    if not path.exists(): return '(not present)'
    try: return '\n'.join(path.read_text(encoding='utf-8', errors='replace').splitlines()[-lines:]) or '(empty)'
    except OSError as exc: return f'(could not read: {exc})'

rows = [
    'TalentBridgeAI local diagnostic report',
    f'Timestamp: {datetime.now().isoformat(timespec="seconds")}',
    f'OS: {platform.platform()}',
    f'Python launcher: {sys.executable}',
    f'Python version: {platform.python_version()}',
    f'Project root: {ROOT}',
    f'Django manage.py exists: {(DJANGO / "manage.py").is_file()}',
    f'Project virtualenv Python exists: {VENV_PY.is_file()}',
    f'Requirements file exists: {(DJANGO / "requirements.txt").is_file()}',
    f'Private .env exists: {(ROOT / ".env").is_file()} (contents intentionally not read or printed)',
    f'SQLite database exists: {DB.is_file()}',
    f'SQLite database size: {DB.stat().st_size if DB.is_file() else "n/a"} bytes',
    f'Port 8000: {port_status(8000)}',
    f'Port 5500: {port_status(5500)}',
    '', '--- Django server log (last 35 lines) ---', tail(LOGS / 'server.log'),
    '', '--- Setup log (last 35 lines) ---', tail(LOGS / 'setup.log'),
]
if VENV_PY.is_file():
    try:
        p = subprocess.run([str(VENV_PY), '-c', 'import django; print("Django", django.get_version())'], cwd=DJANGO, capture_output=True, text=True, timeout=10)
        rows += ['', '--- Virtual environment Django import ---', (p.stdout or p.stderr).strip() or f'exit code {p.returncode}']
    except Exception as exc:
        rows += ['', '--- Virtual environment Django import ---', repr(exc)]
else:
    rows += ['', 'Django import check skipped: project virtual environment is missing.']
OUT.write_text('\n'.join(rows) + '\n', encoding='utf-8')
print('\n'.join(rows))
print(f'\nSaved diagnostic report: {OUT}')
