# Step 2 change report

Date: 2026-11-12

Foundation repair only. No dashboard redesign, no AI resume work, no demo data, and no schema migration.

## Data protection

- `database/TalentBridgeAI.sqlite3` was not deleted, recreated, or migrated. `showmigrations` reported every migration applied, and the launcher logged “No pending migrations; database left untouched.”
- User count stayed 0 before and after the repair. No password was set or reset.
- `.env` was not printed, rewritten, or copied. The Step 1 backup `backups/audit_20261112_154417/` was not modified.
- Two non-schema database updates were required by this step: the placeholder site domain `example.com` became `127.0.0.1:8000`, and one Google social-app row was created from the existing private environment values. The secret was not displayed.

## Changed files

- `tools/windows_manager.py` — a new process receives the current `.env` (last non-empty value wins for duplicate keys). Start recognizes this project’s already-running server, including the autoreload worker. Stop ends that process tree and refuses to kill an unrelated program on port 8000. `restart` stops and starts. Automatic logon startup was not enabled.
- `RESTART_TALENTBRIDGEAI.bat` — runs that restart and keeps the server window open.
- `CREATE_SUPERUSER.bat` — interactive first-admin setup. It does not run unless you open it.
- `legacy-django/jobs/management/commands/prepare_local_auth.py` — updates only a placeholder site domain, syncs Google when both values load, and prints yes/no status without secrets.
- `legacy-django/jobs/management/commands/ensure_superuser.py` — creates an account only in an interactive terminal when none exists. An existing superuser is left alone.
- `legacy-django/templates/admin/login.html` — removed the stray CSS line after the background image.
- `legacy-django/jobs/tests.py` — admin login test now rejects that broken CSS line.
- `README_RUN_DJANGO.md`, `STARTUP_README.md`, `docs/troubleshooting/REMAINING_ISSUES.md` — startup, restart, superuser, and Google Cloud steps. The old claim that startup seeds demo data was removed from the run guide.

## Not changed

- Job seeker and employer dashboard behavior.
- Resume upload behavior and the sample resume card.
- AI parsing and resume generation.
- `requirements.txt`.
- Existing user rows. There were none to modify.
