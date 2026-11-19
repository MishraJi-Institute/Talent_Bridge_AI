# TalentBridgeAI — Windows first-run setup and startup

## Requirements

- Windows 10/11
- Python 3.11, 3.12, or 3.13 installed from python.org with the Python Launcher (`py`) or PATH enabled
- Internet access for the first dependency installation

## First run (one time)

1. Extract the ZIP to a normal writable folder (for example `C:\TalentBridgeAI`).
2. Double-click `INSTALL_TALENTBRIDGEAI.bat` and wait for the checks to finish.
3. The installer creates `legacy-django\.venv`, creates `.env` from `.env.example` only when `.env` is absent, generates a persistent `DJANGO_SECRET_KEY` only when missing, checks dependencies and database connectivity, backs up an existing SQLite database before applying pending migrations, runs Django checks, and collects static files.
4. Double-click `START_TALENTBRIDGEAI.bat`.

The installer does not create, delete, reset, or rename user accounts. It does not seed demo data. Existing `.env` values are not overwritten.

## Everyday use

- Start: `START_TALENTBRIDGEAI.bat` (runs Django in the current terminal and reports readiness only after an HTTP 200 response from `http://127.0.0.1:8000/`; press Ctrl+C to stop). If this project is already serving port 8000, start reports that and does not reload `.env`.
- Restart: `RESTART_TALENTBRIDGEAI.bat` stops the managed server and starts a new process so the current `.env` is loaded. Leave that window open.
- Status: `CHECK_STATUS.bat`
- Stop: `STOP_TALENTBRIDGEAI.bat`
- First administrator: `CREATE_SUPERUSER.bat` (interactive; does not change an existing superuser)
- Diagnose safe configuration issues: `REPAIR_TALENTBRIDGEAI.bat`
- Update installed Python packages from the project's local `legacy-django\requirements.txt`: `UPDATE_TALENTBRIDGEAI.bat`

URLs:

- Website: http://127.0.0.1:8000/
- Django Admin: http://127.0.0.1:8000/admin/login/

The development server binds only to `127.0.0.1`; it is not exposed to the LAN or public internet. Port 8000 conflicts are reported and unrelated processes are never killed. Logs are written under `logs\setup.log` and `logs\server.log`.

## Admin login diagnosis and recovery

Run the read-only account audit from `legacy-django`:

```powershell
.\.venv\Scripts\python.exe manage.py audit_admin_auth
```

If an existing authorized admin account reports `password_usable=False`, Django has no usable password hash stored for it. The original plaintext password cannot be reconstructed from that state. Set a new password for that same account interactively (this does not delete or recreate the user):

```powershell
.\.venv\Scripts\python.exe manage.py changepassword YOUR_EXISTING_ADMIN_USERNAME
```

Do not paste passwords into scripts, source files, chat, or logs. The package never resets passwords automatically.

## Database and backups

- SQLite is configured by default at `database\TalentBridgeAI.sqlite3`.
- Before the installer/update applies migrations, it makes a timestamped copy of an existing SQLite database under `backups\`.
- Existing database files are not included in this source ZIP. Copy your original database into `database\` before first launch if you need its records.
- Preserve `private_media\` when moving an existing installation; this contains uploaded resumes and other user files.
- For MySQL, configure `DB_ENGINE=mysql` and the DB connection variables in `.env`; use your normal MySQL backup tooling. The local SQLite backup routine does not back up MySQL.

## Environment and Google OAuth

`.env.example` is a safe template. On first installation `.env` is created from it only if no `.env` exists. Existing `.env` values are not printed or overwritten. Add both `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` to enable Google sign-in, then run `RESTART_TALENTBRIDGEAI.bat`. Keep `.env` private. In Google Cloud Console, verify the authorized JavaScript origin `http://127.0.0.1:8000` and the redirect URI `http://127.0.0.1:8000/accounts/google/login/callback/`. A successful restart does not by itself prove the Google consent flow.

## Optional automatic startup after Windows sign-in

- Enable: double-click `ENABLE_AUTO_STARTUP.bat`.
- Disable: double-click `DISABLE_AUTO_STARTUP.bat`, or remove the task named `TalentBridgeAI Local Development Server` in Windows Task Scheduler.

This option starts the local development server at user logon. It is not enabled by default.

## Update behavior and limits

`UPDATE_TALENTBRIDGEAI.bat` creates a timestamped SQLite backup (when SQLite is configured) and a source snapshot before installing dependencies from the local requirements file and applying migrations. It does not fetch application source from a remote repository because no remote update endpoint/repository is configured in this project. Review dependency changes before using this on a production deployment.

## Clean installation and safety notes

The ZIP intentionally excludes real `.env` secrets, local databases, virtual environments, runtime logs, caches, and private uploads. This is source packaging, not a copy of your live data. Keep a separate backup of `.env`, the database, and `private_media` before replacing an existing project folder.


## Default Django browser preview (port 8000)

The VS Code folder-open task now starts Django as the default application and opens the browser only after homepage, login, and job-seeker/employer signup HTTP health checks pass. Do not use Live Server / port 5500 as the application preview. The optional static preview remains available without auto-opening a browser. See `DJANGO_DEFAULT_PREVIEW_FIX.md`.
