#!/usr/bin/env python3
"""Safe Windows/local development lifecycle manager for TalentBridgeAI."""
from __future__ import annotations
import argparse, os, re, shutil, socket, subprocess, sys, time, urllib.request, zipfile, webbrowser
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
DJANGO = ROOT / 'backend' / 'legacy-django'
if not (DJANGO / 'manage.py').is_file():
    DJANGO = ROOT / 'legacy-django'
REQ = DJANGO / 'requirements.txt'
VENV = DJANGO / '.venv'
PY = VENV / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
LOGDIR = ROOT / 'logs'
BACKUP = ROOT / 'backups'
PIDFILE = ROOT / '.talentbridge_django.pid'
BRIDGE_PIDFILE = ROOT / '.talentbridge_port_bridge.pid'
BRIDGE_SCRIPT = ROOT / 'tools' / 'talentbridge_port_bridge.py'
STOP_MARKER = ROOT / '.talentbridge_django.stopping'
LAUNCH_LOCK = ROOT / '.talentbridge_django.lock'
# Bookmarks and docs often use 8000; the managed server may land on 8001.
# Keep both working via a tiny redirect bridge on the unused alias port.
CANONICAL_ALIAS_PORTS = (8000, 8001)

# Cross-extraction state lives outside the ZIP so every newly extracted copy
# can find the last working checkout on this Windows account.
GLOBAL_STATE = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'TalentBridgeAI'
ACTIVE_ROOT_FILE = GLOBAL_STATE / 'active_project.txt'
GLOBAL_PID_FILE = GLOBAL_STATE / 'server.pid'
PORT_FILE = ROOT / '.talentbridge_django.port'


def sync_previous_checkout_data():
    """Import private config and user data from the last checkout, preserving backups."""
    GLOBAL_STATE.mkdir(parents=True, exist_ok=True)
    candidates = []
    try:
        saved = ACTIVE_ROOT_FILE.read_text(encoding='utf-8').strip()
        if saved:
            candidates.append(Path(saved))
    except OSError:
        pass
    configured_source = os.environ.get('TALENTBRIDGEAI_OLD_ROOT', '').strip()
    if configured_source:
        candidates.insert(0, Path(configured_source))
    # A prior checkout beside the newly extracted folder is another safe candidate.
    candidates.append(ROOT.parent / 'TalentBridgeAI')
    source = None
    for candidate in candidates:
        try:
            candidate = candidate.resolve()
            if candidate != ROOT.resolve() and (
                (candidate / 'backend' / 'legacy-django' / 'manage.py').is_file()
                or (candidate / 'legacy-django' / 'manage.py').is_file()
            ):
                source = candidate
                break
        except OSError:
            continue
    if source is None:
        log('No previous TalentBridgeAI checkout found; keeping this extraction data.')
        return
    copied = []
    # Copy .env from the prior checkout (never package credentials in a ZIP).
    old_env = source / '.env'
    new_env = ROOT / '.env'
    if old_env.is_file() and not new_env.exists():
        shutil.copy2(old_env, new_env)
        copied.append('.env')
    # Prefer the prior database over an empty/sample DB shipped in a ZIP.
    old_db_dir = source / 'database'
    new_db_dir = ROOT / 'database'
    if old_db_dir.is_dir():
        for old_db in old_db_dir.glob('*.sqlite3'):
            new_db_dir.mkdir(parents=True, exist_ok=True)
            target = new_db_dir / old_db.name
            if not target.exists():
                shutil.copy2(old_db, target)
                copied.append('database/' + old_db.name)
    # User uploads are merged without deleting files already in the new copy.
    for dirname in ('private_media', 'media', 'uploads'):
        old_dir = source / dirname
        new_dir = ROOT / dirname
        if old_dir.is_dir():
            for item in old_dir.rglob('*'):
                if not item.is_file():
                    continue
                target = new_dir / item.relative_to(old_dir)
                if not target.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, target)
            copied.append(dirname + ' (missing files merged)')
    log(
        f'Imported prior checkout data from {source}; items={copied}. '
        'Existing destination settings and database files were preserved.'
    )


def remember_active_checkout():
    GLOBAL_STATE.mkdir(parents=True, exist_ok=True)
    ACTIVE_ROOT_FILE.write_text(str(ROOT.resolve()), encoding='utf-8')
HOST, DEFAULT_PORT, PORT = '127.0.0.1', 8000, 8000
URL = f'http://{HOST}:{PORT}/'
ADMIN = URL + 'admin/login/'
HEALTH_PATHS = ('', 'login/', 'admin/login/', 'signup/job-seeker/', 'signup/employer/', 'static/admin/css/base.css')


def run(cmd, *, cwd=ROOT, check=True, capture=False, env=None):
    return subprocess.run(cmd, cwd=cwd, check=check, text=True, env=env,
                          stdout=subprocess.PIPE if capture else None,
                          stderr=subprocess.STDOUT if capture else None)


def log(msg):
    LOGDIR.mkdir(exist_ok=True)
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line, flush=True)
    with (LOGDIR / 'setup.log').open('a', encoding='utf-8') as f: f.write(line+'\n')


def find_boot_python():
    candidates = []
    if os.name == 'nt':
        for v in ('3.13', '3.12', '3.11'):
            candidates.append(['py', '-'+v])
    candidates.append([sys.executable])
    candidates.append(['python'])
    for c in candidates:
        try:
            p = subprocess.run(
                c + ['-c', 'import sys; print("{}.{}".format(sys.version_info.major, sys.version_info.minor))'],
                capture_output=True, text=True, timeout=15,
            )
            if p.returncode == 0:
                major_minor = tuple(map(int, p.stdout.strip().split('.')[:2]))
                if (3, 11) <= major_minor < (3, 14): return c
        except (OSError, ValueError, IndexError, subprocess.SubprocessError): pass
    raise RuntimeError('Python 3.11, 3.12, or 3.13 is required. Install Python and enable PATH/py launcher.')


def installed_python_version(executable):
    try:
        result = subprocess.run(
            [str(executable), '-c', 'import sys; print("{}.{}".format(sys.version_info.major, sys.version_info.minor))'],
            cwd=DJANGO, capture_output=True, text=True, timeout=15,
        )
        if result.returncode:
            return None
        return tuple(map(int, result.stdout.strip().split('.')[:2]))
    except (OSError, ValueError, IndexError, subprocess.SubprocessError):
        return None


def supported_python_version(version):
    return version is not None and (3, 11) <= version < (3, 14)


def ensure_env():
    if not DJANGO.joinpath('manage.py').is_file() or not REQ.is_file():
        raise RuntimeError(f'Expected Django project not found at {DJANGO}')
    version = installed_python_version(PY) if PY.is_file() else None
    valid = supported_python_version(version)
    if not valid:
        if VENV.exists():
            if version is None:
                log('Existing virtual environment is not runnable on this PC/path. Rebuilding only legacy-django\\.venv...')
            else:
                log(f'Existing virtual environment uses unsupported Python {version[0]}.{version[1]}. Rebuilding only legacy-django\\.venv...')
            shutil.rmtree(VENV, ignore_errors=False)
        log('Creating a portable project-specific virtual environment...')
        bootstrap_python = find_boot_python()
        run(bootstrap_python+['-m','venv',str(VENV)])
    if not PY.is_file(): raise RuntimeError(f'Virtual environment Python missing: {PY}')
    version = installed_python_version(PY)
    if not supported_python_version(version):
        detail = f'{version[0]}.{version[1]}' if version else 'unavailable'
        raise RuntimeError(f'Project virtual environment must use Python 3.11, 3.12, or 3.13; found {detail}.')
    log(f'Using project virtual environment with Python {version[0]}.{version[1]}.')
    return PY




def register_portable_launcher():
    """Copy START_TALENTBRIDGEAI.bat to Desktop/Start Menu so it runs from anywhere."""
    if os.name != 'nt':
        return
    GLOBAL_STATE.mkdir(parents=True, exist_ok=True)
    src = ROOT / 'START_TALENTBRIDGEAI.bat'
    if not src.is_file():
        log('START_TALENTBRIDGEAI.bat missing at project root; portable shortcuts skipped.')
        return
    cached = GLOBAL_STATE / 'START_TALENTBRIDGEAI.bat'
    shutil.copy2(src, cached)
    targets = []
    profile = os.environ.get('USERPROFILE', '').strip()
    if profile:
        desktop = Path(profile) / 'Desktop'
        if desktop.is_dir():
            targets.append(desktop / 'TalentBridgeAI START (Auto Install).bat')
        onedrive = os.environ.get('OneDrive', '').strip()
        if onedrive:
            od_desktop = Path(onedrive) / 'Desktop'
            if od_desktop.is_dir():
                targets.append(od_desktop / 'TalentBridgeAI START (Auto Install).bat')
    appdata = os.environ.get('APPDATA', '').strip()
    if appdata:
        menu = Path(appdata) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'TalentBridgeAI'
        menu.mkdir(parents=True, exist_ok=True)
        targets.append(menu / 'Start TalentBridgeAI (Auto Install).bat')
    for target in targets:
        try:
            shutil.copy2(src, target)
        except OSError as exc:
            log(f'Could not copy launcher to {target}: {exc}')
    log(f'Portable launcher updated ({len(targets)} shortcut(s); also {cached}).')


def register_user_startup():
    """Register a simple per-user CMD launcher (avoids fragile VBScript startup files)."""
    if os.name != 'nt':
        log('Windows sign-in auto-start registration skipped on non-Windows OS.')
        return
    appdata = os.environ.get('APPDATA')
    if not appdata:
        raise RuntimeError('APPDATA is unavailable; cannot register Windows sign-in startup.')
    startup = Path(appdata) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
    startup.mkdir(parents=True, exist_ok=True)
    launcher = str((ROOT / 'START_TALENTBRIDGEAI.bat').resolve())
    startup_cmd = startup / 'TalentBridgeAI_Server_Startup.cmd'
    lines = [
        '@echo off',
        f'cd /d "{ROOT}"',
        f'start "" /min cmd.exe /c ""{launcher}""',
        ''
    ]
    startup_cmd.write_text('\r\n'.join(lines), encoding='utf-8')
    # Remove the legacy broken VBS generated by earlier package versions.
    old_vbs = startup / 'TalentBridgeAI_Server_Startup.vbs'
    try:
        old_vbs.unlink(missing_ok=True)
    except OSError:
        pass
    log(f'Windows sign-in auto-start registered using CMD: {startup_cmd}')


def ensure_private_env():
    env = ROOT / '.env'
    example = ROOT / '.env.example'
    if not env.exists():
        if not example.exists(): raise RuntimeError('.env.example is missing; cannot initialize local configuration.')
        shutil.copyfile(example, env)
        with env.open('a', encoding='utf-8') as f:
            f.write(
                '\n# One-click launcher defaults (see tools/windows_manager.py auto)\n'
                'TALENTBRIDGEAI_AUTO_PUBLISH=1\n'
            )
        log('Created .env from .env.example (AUTO_PUBLISH enabled). Add Google OAuth + optional RENDER_API_KEY.')
    text = env.read_text(encoding='utf-8-sig')
    import secrets
    lines = text.splitlines()
    has_key = any(x.partition('=')[0].strip() == 'DJANGO_SECRET_KEY' and x.partition('=')[2].strip() for x in lines)
    if not has_key:
        with env.open('a', encoding='utf-8') as f:
            f.write('\n# Generated once locally; do not share this file.\nDJANGO_SECRET_KEY='+secrets.token_urlsafe(48)+'\n')
        log('Generated persistent DJANGO_SECRET_KEY in private .env.')
    for d in (ROOT/'database', ROOT/'private_media', ROOT/'logs', ROOT/'backups', DJANGO/'staticfiles'):
        d.mkdir(parents=True, exist_ok=True)


def parsed_private_env():
    """Read .env without printing it. The last non-empty value wins for duplicate keys."""
    path = ROOT / '.env'
    values = {}
    if not path.is_file():
        return values
    for raw in path.read_text(encoding='utf-8-sig').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key:
            continue
        if value or key not in values:
            values[key] = value
    return values


def validate_private_env():
    values = parsed_private_env()
    if not values.get('DJANGO_SECRET_KEY', '').strip():
        raise RuntimeError('Private environment is missing DJANGO_SECRET_KEY; it was not printed or changed.')
    engine = values.get('DB_ENGINE', 'sqlite').strip().lower()
    if engine not in {'sqlite', 'mysql'}:
        raise RuntimeError('DB_ENGINE must be either sqlite or mysql.')
    if not values.get('DB_NAME', 'TalentBridgeAI').strip():
        raise RuntimeError('DB_NAME must not be empty.')
    if bool(values.get('GOOGLE_OAUTH_CLIENT_ID')) != bool(values.get('GOOGLE_OAUTH_CLIENT_SECRET')):
        log('Google OAuth has only one credential configured; Google sign-in will remain unavailable until both are set.')


def launcher_env():
    """Environment for a new Django process. Overrides stale values inherited by this process."""
    env = os.environ.copy()
    env.update(parsed_private_env())
    env['DJANGO_ENV'] = 'development'
    env['DJANGO_DEBUG'] = 'true'
    return env


REQ_STAMP = VENV / '.requirements.sha256'


def _requirements_digest():
    import hashlib
    return hashlib.sha256(REQ.read_bytes()).hexdigest()


def pip_ready(py):
    log('Verifying required Python packages (full requirements.txt)...')
    digest = _requirements_digest()
    stamp = REQ_STAMP.read_text(encoding='ascii').strip() if REQ_STAMP.is_file() else ''
    imports = 'import django, allauth, dotenv, PIL, pymysql, whitenoise, gunicorn'
    probe = subprocess.run([str(py), '-c', imports], cwd=DJANGO, capture_output=True, text=True)
    if probe.returncode or stamp != digest:
        log('Installing or refreshing dependencies from requirements.txt...')
        run([str(py), '-m', 'pip', 'install', '--upgrade', 'pip'], check=False)
        run([str(py), '-m', 'pip', 'install', '-r', str(REQ)])
        REQ_STAMP.write_text(digest, encoding='ascii')
    run([str(py), '-m', 'pip', 'check'])


def db_backup(py):
    """Create a unique, integrity-checked SQLite snapshot before migration."""
    import sqlite3
    env = ROOT/'.env'
    cfg = {'DB_ENGINE':'sqlite','DB_NAME':'TalentBridgeAI'}
    if env.exists():
        for line in env.read_text(encoding='utf-8-sig').splitlines():
            if '=' in line and not line.lstrip().startswith('#'):
                k,v=line.split('=',1); cfg[k.strip()]=v.strip().strip('"').strip("'")
    if cfg.get('DB_ENGINE','sqlite').lower() != 'sqlite':
        log('Non-SQLite database configured; database backup is delegated to configured DB provider.'); return
    name = cfg.get('DB_NAME') or 'TalentBridgeAI'
    if not name.lower().endswith('.sqlite3'): name += '.sqlite3'
    db = ROOT/'database'/name
    if db.is_file():
        BACKUP.mkdir(exist_ok=True)
        stem = db.stem+'_'+datetime.now().strftime('%Y%m%d_%H%M%S')
        target = BACKUP/(stem+'.sqlite3')
        suffix = 1
        while target.exists():
            target = BACKUP/(stem+f'_{suffix:02d}.sqlite3')
            suffix += 1
        try:
            fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            source_uri = db.resolve().as_uri() + '?mode=ro'
            source = sqlite3.connect(source_uri, uri=True)
            try:
                destination = sqlite3.connect(target)
                try:
                    source.backup(destination)
                    result = destination.execute('PRAGMA integrity_check').fetchone()
                    if not result or result[0] != 'ok':
                        raise RuntimeError('SQLite backup integrity check failed; migration was not started.')
                finally:
                    destination.close()
            finally:
                source.close()
        except Exception:
            target.unlink(missing_ok=True)
            raise
        log(f'Created and verified SQLite migration backup: {target.relative_to(ROOT)}')


def _planned_migrations(plan_output):
    migrations = []
    for line in plan_output.splitlines():
        match = re.match(
            r'^\s*(?:\[[ X]\]\s*)?([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)\s*$',
            line,
        )
        if match:
            migrations.append((match.group(1), match.group(2)))
    return migrations


def django_checks(py, migrate=False, collect=False, env=None):
    common=[str(py),'manage.py']
    run(common+['check'],cwd=DJANGO,env=env)
    # Test configured DB connection before migration.
    run(common+['shell','-c',"from django.db import connection; c=connection.cursor(); c.execute('SELECT 1'); print('DATABASE CONNECTIVITY: OK')"],cwd=DJANGO,env=env)
    if migrate:
        plan = run(common+['migrate','--plan'],cwd=DJANGO,capture=True,env=env)
        plan_output = plan.stdout or ''
        pending_migrations = _planned_migrations(plan_output)
        pending = bool(pending_migrations)
        if pending:
            print('Migration impact review:')
            print(plan_output.strip())
            risk_markers = (
                'delete model', 'remove field', 'remove index', 'remove constraint',
                'runpython', 'drop table', 'drop column', 'delete from', 'truncate',
            )
            risky = any(marker in plan_output.lower() for marker in risk_markers)
            for app_label, migration_name in pending_migrations:
                sql = run(
                    common+['sqlmigrate',app_label,migration_name],
                    cwd=DJANGO,capture=True,env=env,
                )
                sql_output = sql.stdout or ''
                if re.search(r'\b(DROP\s+(?:TABLE|COLUMN|INDEX)|DELETE\s+FROM|TRUNCATE)\b', sql_output, re.IGNORECASE):
                    risky = True
            db_engine = (env or launcher_env()).get('DB_ENGINE', 'sqlite').lower()
            if risky and db_engine != 'sqlite':
                if (env or launcher_env()).get('TALENTBRIDGEAI_MIGRATION_BACKUP_CONFIRMED') != '1':
                    raise RuntimeError(
                        'A potentially destructive migration was found for a non-SQLite database. '
                        'Create and verify a provider-side backup first, then set '
                        'TALENTBRIDGEAI_MIGRATION_BACKUP_CONFIRMED=1 for the migration run.'
                    )
                log('External database backup was explicitly confirmed for the risky migration.')
            db_backup(py)
            run(common+['migrate','--noinput'],cwd=DJANGO,env=env)
        else:
            log('No pending migrations; database left untouched.')
    if collect: run(common+['collectstatic','--noinput'],cwd=DJANGO,env=env)


def prepare_local_auth(py, env):
    run([str(py),'manage.py','prepare_local_auth'],cwd=DJANGO,env=env)
    # Read-only account audit: reports whether admin accounts have usable passwords.
    run([str(py),'manage.py','audit_admin_auth'],cwd=DJANGO,env=env)


def port_open():
    with socket.socket() as s:
        s.settimeout(.4); return s.connect_ex((HOST,PORT)) == 0


def port_available(port):
    with socket.socket() as sock:
        try:
            sock.bind((HOST, port))
            return True
        except OSError:
            return False


def set_server_port(port):
    global PORT, URL, ADMIN
    PORT = port
    URL = f'http://{HOST}:{PORT}/'
    ADMIN = URL + 'admin/login/'


def configure_server_port(action):
    """Reuse this checkout's server or select an unoccupied local development port.

    Prefer the default port (8000) when it is free so bookmarks to :8000 keep working.
    If a managed server is already healthy on the saved port, keep it.
    """
    try:
        requested = int(os.environ.get('TALENTBRIDGEAI_PORT', DEFAULT_PORT))
    except ValueError as error:
        raise RuntimeError('TALENTBRIDGEAI_PORT must be a valid TCP port number.') from error
    if not 1 <= requested <= 65535:
        raise RuntimeError('TALENTBRIDGEAI_PORT must be between 1 and 65535.')

    saved = None
    try:
        saved = int(PORT_FILE.read_text(encoding='ascii').strip())
        if not 1 <= saved <= 65535:
            saved = None
    except (OSError, ValueError):
        saved = None

    # Stick with an already-healthy managed server, even if it is on 8001.
    if saved is not None:
        set_server_port(saved)
        if port_open() and managed_roots():
            return

    # Fresh start: prefer 8000 / requested before any stale saved alternate port.
    candidates = [requested, DEFAULT_PORT]
    if saved is not None:
        candidates.append(saved)
    candidates.extend(CANONICAL_ALIAS_PORTS)
    candidates.extend(range(DEFAULT_PORT, min(DEFAULT_PORT + 21, 65536)))
    candidates = list(dict.fromkeys(candidates))

    for candidate in candidates:
        set_server_port(candidate)
        if port_open() and managed_roots():
            return

    if action in {'start', 'restart', 'install'}:
        for candidate in candidates:
            set_server_port(candidate)
            if port_available(candidate):
                return
        raise RuntimeError(
            f'No available local development port was found in the candidate set {candidates}. '
            'No unrelated process was stopped.'
        )

    set_server_port(candidates[0])


def _bridge_pid() -> int | None:
    try:
        pid = int(BRIDGE_PIDFILE.read_text(encoding='ascii').strip())
    except (OSError, ValueError):
        return None
    return pid if pid_alive(pid) else None


def stop_port_bridge():
    pid = _bridge_pid()
    if not pid:
        BRIDGE_PIDFILE.unlink(missing_ok=True)
        return
    if os.name == 'nt':
        subprocess.run(['taskkill', '/PID', str(pid), '/T', '/F'], capture_output=True, text=True)
    else:
        import signal
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass
    BRIDGE_PIDFILE.unlink(missing_ok=True)
    log(f'Stopped TalentBridge port bridge (PID {pid}).')


def ensure_port_bridge():
    """Keep the unused canonical port (8000/8001) redirecting to the live Django port."""
    if not BRIDGE_SCRIPT.is_file():
        return
    aliases = [port for port in CANONICAL_ALIAS_PORTS if port != PORT]
    if not aliases:
        return

    # Refresh any previous bridge so it always points at the current Django port.
    stop_port_bridge()

    for listen_port in aliases:
        if not port_available(listen_port):
            log(
                f'Alias port {listen_port} is occupied by another process; '
                f'bookmarks to http://{HOST}:{listen_port}/ will not auto-redirect. '
                f'Use http://{HOST}:{PORT}/ instead.'
            )
            continue
        creationflags = 0
        if os.name == 'nt':
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        out = (LOGDIR / 'port_bridge.log').open('a', encoding='utf-8')
        proc = subprocess.Popen(
            [
                sys.executable,
                str(BRIDGE_SCRIPT),
                '--listen-host', HOST,
                '--listen', str(listen_port),
                '--target-host', HOST,
                '--target', str(PORT),
            ],
            cwd=ROOT,
            stdout=out,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            creationflags=creationflags,
            close_fds=True,
        )
        BRIDGE_PIDFILE.write_text(str(proc.pid), encoding='ascii')
        time.sleep(0.35)
        with socket.socket() as sock:
            sock.settimeout(0.4)
            listening = sock.connect_ex((HOST, listen_port)) == 0
        if listening:
            log(
                f'Port bridge ready: http://{HOST}:{listen_port}/ ↦ http://{HOST}:{PORT}/ '
                f'(reverse proxy PID {proc.pid}). Both ports open the same site.'
            )
            print(
                f'Also reachable via http://{HOST}:{listen_port}/ '
                f'(proxied to http://{HOST}:{PORT}/)',
                flush=True,
            )
            return
        log(f'Port bridge failed to listen on {listen_port}; continuing with Django on {PORT} only.')
        stop_port_bridge()


def pid_alive(pid):
    if os.name == 'nt':
        result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}', '/NH'], capture_output=True, text=True)
        return str(pid) in result.stdout and 'No tasks' not in result.stdout
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def acquire_launch_lock():
    """Serialize startup so two launchers cannot both bind port 8000."""
    for _ in range(2):
        try:
            fd = os.open(LAUNCH_LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            try:
                holder = int(LAUNCH_LOCK.read_text(encoding='ascii').strip())
            except (OSError, ValueError):
                holder = None
            if holder and pid_alive(holder):
                raise RuntimeError('Another TalentBridgeAI startup is already in progress. It was not interrupted.')
            LAUNCH_LOCK.unlink(missing_ok=True)
            continue
        os.write(fd, str(os.getpid()).encode('ascii'))
        return fd
    raise RuntimeError('Could not acquire the TalentBridgeAI startup lock.')


def release_launch_lock(fd):
    if fd is None:
        return
    os.close(fd)
    LAUNCH_LOCK.unlink(missing_ok=True)


def server_log_has_traceback(start_pos):
    path = LOGDIR / 'server.log'
    try:
        with path.open('r', encoding='utf-8', errors='replace') as handle:
            handle.seek(start_pos)
            return 'Traceback (most recent call last)' in handle.read()
    except OSError:
        return False


def project_runservers():
    """Return (pid, parent_pid) for this project's runserver processes, including the autoreload worker."""
    host_port = f'{HOST}:{PORT}'.lower()
    # Identify only this exact checkout. A generic "talentbridgeai" substring
    # can accidentally claim a different copy of the project.
    manage_marker = str((DJANGO / 'manage.py').resolve()).replace('\\', '/').lower()
    venv_marker = str(VENV.resolve()).replace('\\', '/').lower()
    if os.name == 'nt':
        script = (
            "Get-CimInstance Win32_Process | "
            "Where-Object { $_.CommandLine } | "
            "ForEach-Object { '{0}|{1}|{2}' -f $_.ProcessId, $_.ParentProcessId, $_.CommandLine }"
        )
        result = subprocess.run(
            ['powershell.exe', '-NoProfile', '-Command', script],
            capture_output=True, text=True,
        )
        rows = []
        for line in result.stdout.splitlines():
            parts = line.split('|', 2)
            if len(parts) != 3 or not parts[0].isdigit() or not parts[1].isdigit():
                continue
            command = parts[2].replace('\\', '/').lower()
            if 'runserver' not in command or host_port not in command:
                continue
            # Require the full path to this checkout's manage.py or its venv.
            if manage_marker not in command and venv_marker not in command:
                continue
            rows.append((int(parts[0]), int(parts[1])))
        return rows
    rows = []
    proc_root = Path('/proc')
    if not proc_root.is_dir():
        return rows
    for entry in proc_root.iterdir():
        if not entry.name.isdigit():
            continue
        try:
            command = (entry / 'cmdline').read_bytes().replace(b'\x00', b' ').decode(errors='ignore').lower()
            parent = (entry / 'status').read_text(encoding='utf-8', errors='ignore')
        except OSError:
            continue
        if 'runserver' not in command or host_port not in command:
            continue
        if manage_marker not in command and venv_marker not in command:
            continue
        ppid = 0
        for status_line in parent.splitlines():
            if status_line.startswith('PPid:'):
                ppid = int(status_line.split()[1])
                break
        rows.append((int(entry.name), ppid))
    return rows


def managed_roots():
    rows = project_runservers()
    pids = {pid for pid, _parent in rows}
    roots = [pid for pid, parent in rows if parent not in pids]
    if not roots and rows:
        roots = [min(pids)]
    try:
        recorded = int(PIDFILE.read_text(encoding='ascii').strip())
    except (OSError, ValueError):
        recorded = None
    if recorded in pids:
        roots = [recorded] + [pid for pid in roots if pid != recorded]
    return roots


def owned_pid():
    roots = managed_roots()
    return roots[0] if roots else None


def http_status(path, timeout=2):
    request = urllib.request.Request(URL + path, headers={'User-Agent': 'TalentBridgeAI-LocalHealth/1.0'})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except Exception:
        return None


def health_report():
    return {path or '/': http_status(path) for path in HEALTH_PATHS}


def wait_http(seconds=35, proc=None):
    end=time.time()+seconds
    while time.time()<end:
        if proc is not None and proc.poll() is not None:
            return False
        checks = health_report()
        if (
            checks.get('/') == 200
            and checks.get('static/admin/css/base.css') == 200
            and all(checks.get(path) in (200, 301, 302, 303, 307, 308)
                    for path in ('login/', 'admin/login/', 'signup/job-seeker/', 'signup/employer/'))
        ):
            return True
        time.sleep(.5)
    return False


def open_website():
    """Open only the verified Django URL, never the generated static preview."""
    checks = health_report()
    failed = {path: status for path, status in checks.items() if status is None or status >= 400}
    if failed:
        details = ', '.join(f'{path}={status or "NO RESPONSE"}' for path, status in failed.items())
        raise RuntimeError(f'Django health check failed; browser was not opened: {details}')
    try:
        opened = webbrowser.open(URL, new=2, autoraise=True)
    except Exception as exc:
        log(f'Browser auto-open failed: {exc}. Open {URL} manually.')
        return
    if opened:
        log(f'Opened verified Django website in the default browser: {URL}')
    else:
        log(f'Could not launch a browser automatically. Open the verified Django website manually: {URL}')


def terminate_process_tree(proc):
    if proc.poll() is not None: return
    if os.name == 'nt':
        run(['taskkill','/PID',str(proc.pid),'/T','/F'],check=False)
    else:
        proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()


def run_smoke_qa(py, env):
    """Fast local QA on every automated run (full test suite stays optional)."""
    run([str(py), 'manage.py', 'check'], cwd=DJANGO, env=env)
    if (parsed_private_env().get('TALENTBRIDGEAI_FULL_TESTS') or '').strip() == '1':
        log('TALENTBRIDGEAI_FULL_TESTS=1 — running Django jobs tests (may take several minutes)...')
        run([str(py), 'manage.py', 'test', 'jobs', '--verbosity', '1'], cwd=DJANGO, env=env)
    else:
        log('Smoke QA: system check only (set TALENTBRIDGEAI_FULL_TESTS=1 in .env for full tests).')


def publish():
    script = ROOT / 'tools' / 'publish_live.py'
    if not script.is_file():
        log('publish_live.py missing; skipping live publish step.')
        return
    run([sys.executable, str(script)], cwd=ROOT)


def install():
    sync_previous_checkout_data()
    ensure_private_env(); validate_private_env(); py=ensure_env(); env=launcher_env(); pip_ready(py)
    django_checks(py,migrate=True,collect=True,env=env)
    prepare_local_auth(py, env)
    register_user_startup()
    register_portable_launcher()
    remember_active_checkout()
    run_smoke_qa(py, env)
    log('INSTALLATION CHECKS COMPLETED. Existing database and user rows were not reset.')


def auto():
    """One-shot: install, publish live assets, start Django (no extra prompts)."""
    install()
    publish()
    start()


def start():
    sync_previous_checkout_data()
    ensure_private_env(); validate_private_env(); py=ensure_env(); env=launcher_env()
    # Re-run safe preflight on every start/restart: dependencies, Django checks,
    # DB connectivity/migrations with backup, admin static collection and site config.
    pip_ready(py)
    django_checks(py,migrate=True,collect=True,env=env)
    prepare_local_auth(py, env)
    register_user_startup()
    register_portable_launcher()
    if port_open():
        pid=owned_pid()
        if not pid: raise RuntimeError(f'Port {PORT} became occupied by another process during startup. It was NOT terminated; retry to select another port.')
        if not wait_http(5):
            raise RuntimeError(f'Managed Django process {pid} is listening, but {URL} did not return HTTP 200.')
        PIDFILE.write_text(str(pid), encoding='ascii')
        PORT_FILE.write_text(str(PORT), encoding='ascii')
        remember_active_checkout()
        log(f'TalentBridgeAI already running and healthy (HTTP 200; managed PID {pid}).')
        print(f'DEVELOPMENT SERVER READY: {URL} (HTTP 200; already running)')
        print('Route health:', health_report())
        ensure_port_bridge()
        open_website()
        print('Mode: development (DEBUG and Django autoreload enabled)')
        print('The running process keeps the environment it started with.')
        print('Run RESTART_TALENTBRIDGEAI.bat to reload .env, then leave that window open.')
        print('Website:',URL,'\nLive preview:',URL+'__dev__/','\nAdmin:',ADMIN); return
    lock = acquire_launch_lock()
    launch = False
    try:
        if port_open():
            launch = False
        else:
            launch = not port_open()
            if launch:
                LOGDIR.mkdir(exist_ok=True)
                log_start = (LOGDIR / 'server.log').stat().st_size if (LOGDIR / 'server.log').exists() else 0
                STOP_MARKER.unlink(missing_ok=True)
                out=(LOGDIR/'server.log').open('a',encoding='utf-8')
                print(f'Starting Django development server at {URL}...',flush=True)
                proc=subprocess.Popen([str(py),'manage.py','runserver',f'{HOST}:{PORT}'],
                                      cwd=DJANGO,stdout=out,stderr=subprocess.STDOUT,
                                      stdin=subprocess.DEVNULL,env=env)
                PIDFILE.write_text(str(proc.pid),encoding='ascii')
    finally:
        release_launch_lock(lock)
    if not launch:
        return start()
    try:
        if not wait_http(35,proc):
            code=proc.poll()
            checks = health_report()
            if code is None:
                raise RuntimeError(f'Django did not pass homepage/login/signup health checks within 35 seconds. Statuses: {checks}')
            raise RuntimeError(f'Django exited with code {code} before health checks passed. Statuses: {checks}')
        remember_active_checkout()
        PORT_FILE.write_text(str(PORT), encoding='ascii')
        try:
            GLOBAL_PID_FILE.write_text(str(proc.pid), encoding='ascii')
        except OSError:
            pass
        log(f'DEVELOPMENT SERVER READY: {URL} (homepage/login/signup healthy; PID {proc.pid}; Django autoreload enabled)')
        print('Route health:', health_report())
        ensure_port_bridge()
        open_website()
        print('Mode: development (DEBUG and Django autoreload enabled)')
        print('Website:',URL,'\nLive preview:',URL+'__dev__/','\nAdmin:',ADMIN)
        print('Django is running in this terminal. Press Ctrl+C to stop it.',flush=True)
        try:
            code=proc.wait()
        except KeyboardInterrupt:
            print('\nStopping the managed Django server...',flush=True)
            terminate_process_tree(proc)
            return
        if code:
            # taskkill makes Django exit 1. A real crash writes a traceback; a managed stop writes the marker first.
            for _ in range(50):
                stopped = STOP_MARKER.exists()
                crashed = server_log_has_traceback(log_start)
                if stopped and not crashed:
                    STOP_MARKER.unlink(missing_ok=True)
                    log('Django server stopped by the managed stop command.')
                    return
                if crashed:
                    break
                if not port_open() and not managed_roots():
                    time.sleep(.1)
                    if STOP_MARKER.exists() and not server_log_has_traceback(log_start):
                        STOP_MARKER.unlink(missing_ok=True)
                        log('Django server stopped by the managed stop command.')
                        return
                time.sleep(.1)
            if server_log_has_traceback(log_start):
                raise RuntimeError(f'Django crashed with exit code {code}. The traceback is in logs/server.log.')
            raise RuntimeError(f'Django server exited with code {code}. See logs/server.log.')
        log('Django server stopped.')
    finally:
        if proc.poll() is None:
            terminate_process_tree(proc)
        try:
            if PIDFILE.read_text(encoding='ascii').strip() == str(proc.pid):
                PIDFILE.unlink()
        except FileNotFoundError:
            pass
        out.close()


def stop():
    stop_port_bridge()
    roots=managed_roots()
    if not roots:
        if PIDFILE.exists(): PIDFILE.unlink(missing_ok=True)
        if port_open(): raise RuntimeError(f'Port {PORT} belongs to an unmanaged process. It was not stopped.')
        log('No managed TalentBridgeAI server is running.'); return
    STOP_MARKER.write_text(','.join(str(pid) for pid in roots), encoding='ascii')
    errors=[]
    for pid in roots:
        if os.name=='nt':
            result=subprocess.run(['taskkill','/PID',str(pid),'/T','/F'],
                                  capture_output=True,text=True)
            if result.returncode:
                errors.append((result.stderr or result.stdout).strip())
        else:
            import signal
            os.kill(pid, signal.SIGTERM)
    for _ in range(40):
        if not port_open() and not managed_roots(): break
        time.sleep(.25)
    if port_open() or managed_roots():
        detail=(' ' + '; '.join(errors)) if errors else ''
        raise RuntimeError(f'Managed Django process tree {", ".join(map(str, roots))} did not release port {PORT}; PID file retained for retry.{detail}')
    PIDFILE.unlink(missing_ok=True)
    log(f'Stopped managed Django process tree {", ".join(map(str, roots))}.')


def restart():
    if port_open() or managed_roots():
        stop()
    start()


def status():
    pid=owned_pid()
    if port_open():
        print(f'Port {PORT}: LISTENING; managed PID: {pid or "no (external process)"}')
        print('HTTP health:', health_report())
    else:
        print(f'Port {PORT}: NOT LISTENING')
    bridge_pid = _bridge_pid()
    for alias in CANONICAL_ALIAS_PORTS:
        if alias == PORT:
            continue
        with socket.socket() as sock:
            sock.settimeout(0.3)
            alias_open = sock.connect_ex((HOST, alias)) == 0
        if alias_open:
            print(
                f'Port {alias}: LISTENING '
                f'({"port bridge PID " + str(bridge_pid) if bridge_pid else "external/other"}); '
                f'use http://{HOST}:{alias}/ as an alias for {URL}'
            )
        else:
            print(f'Port {alias}: not bridging (open {URL})')
    static = socket.socket()
    static.settimeout(.3)
    static_port_open = static.connect_ex((HOST, 5500)) == 0
    static.close()
    if static_port_open:
        print('Port 5500: static preview is also listening (optional only; do not use it for Django workflows).')
    print('DEFAULT WEBSITE:',URL,'\nLive preview dashboard:',URL+'__dev__/','\nAdmin:',ADMIN)


def repair():
    ensure_private_env(); validate_private_env(); py=ensure_env(); env=launcher_env(); pip_ready(py)
    for d in (ROOT/'database',ROOT/'private_media',ROOT/'logs',ROOT/'backups',DJANGO/'staticfiles'): d.mkdir(parents=True,exist_ok=True)
    django_checks(py,migrate=False,collect=False,env=env)
    prepare_local_auth(py, env)
    log('Repair checks completed. No user/password/database reset was performed.')


def update():
    ensure_private_env(); validate_private_env(); py=ensure_env(); db_backup(py)
    # Snapshot application source excluding private/runtime directories before dependency update.
    BACKUP.mkdir(exist_ok=True)
    archive=BACKUP/('source_before_update_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in ROOT.rglob('*'):
            if not p.is_file() or any(x in {'.venv','venv','.git','__pycache__','logs','backups','private_media'} for x in p.parts): continue
            if p.name.lower()=='.env' or p.suffix.lower() in {'.sqlite3','.db','.pyc'}: continue
            z.write(p,p.relative_to(ROOT))
    log(f'Created pre-update source snapshot: {archive.relative_to(ROOT)}')
    env=launcher_env(); pip_ready(py); django_checks(py,migrate=True,collect=True,env=env)
    prepare_local_auth(py, env)
    log('Dependency update workflow completed using the local requirements file; no remote application updater is configured.')


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('action',choices=['install','start','stop','restart','status','repair','update','open','bridge','publish','auto']); a=ap.parse_args()
    try:
        configure_server_port(a.action)
        if a.action == 'open':
            if not wait_http(2): raise RuntimeError(f'Django is not healthy at {URL}; start it with START_TALENTBRIDGEAI.bat first.')
            open_website()
        elif a.action == 'bridge':
            if not wait_http(2):
                raise RuntimeError(f'Django is not healthy at {URL}; start it before enabling the port bridge.')
            ensure_port_bridge()
            print(f'Django: {URL}')
            print(f'Alias ports: {[p for p in CANONICAL_ALIAS_PORTS if p != PORT]} redirect here when free.')
        else:
            globals()[a.action]()
    except subprocess.CalledProcessError as e:
        log(f'Command failed with exit code {e.returncode}: {e.cmd}'); sys.exit(e.returncode or 1)
    except Exception as e:
        log(f'ERROR: {e}'); sys.exit(1)
if __name__=='__main__': main()
