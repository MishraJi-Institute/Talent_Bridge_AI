# Django-first local preview and server reliability

## Default behavior

Opening this project folder in VS Code starts the `TalentBridgeAI: START DEFAULT DJANGO WEBSITE (8000)` task (after VS Code's workspace trust/automatic-task confirmation). The launcher creates/uses `legacy-django/.venv`, loads the project-root `.env`, uses `legacy-django/config/settings.py` and the project database configuration, applies only pending migrations after making a SQLite backup, then starts Django on `127.0.0.1:8000`.

The launcher does not open a browser until these endpoints respond successfully:

- `/` must return HTTP 200
- `/login/` must return a successful response or redirect
- `/signup/job-seeker/` must return a successful response or redirect
- `/signup/employer/` must return a successful response or redirect

After those checks pass, it opens `http://127.0.0.1:8000/` in the default browser. If checks fail, it prints the failing route/status and does not announce a successful launch or open the browser.

## Commands

- `START_TALENTBRIDGEAI.bat` — start or reuse the managed Django server; wait for health checks; open Django.
- `OPEN_DJANGO_WEBSITE.bat` — open Django only if the route health checks pass.
- `CHECK_STATUS.bat` — show port 8000 ownership and homepage/login/signup route health; also report if optional port 5500 is listening.
- `STOP_TALENTBRIDGEAI.bat` — stop only this project's managed Django process tree. It will not kill an unrelated process occupying port 8000.
- `RESTART_TALENTBRIDGEAI.bat` — stop and start the managed server so `.env` changes are reloaded.
- `REPAIR_TALENTBRIDGEAI.bat` — verify the local Python environment, dependencies and Django/database checks without resetting accounts.

Equivalent actions are available in VS Code's **Terminal → Run Task** menu.

## Static preview on port 5500

`site/` remains an optional generated static preview. VS Code Live Server is no longer recommended for this workspace; if it is already installed, its browser auto-open is disabled and its optional port remains 5500. Its static-preview notice is intentionally retained. It is not the primary application and does not support Django authentication, OAuth, uploads, sessions, or database actions. Do not use **Go Live** for normal development. Use port 8000.

## One-time VS Code setup

1. Open the extracted `TalentBridgeAI` project root (the folder containing `START_TALENTBRIDGEAI.bat`) in VS Code.
2. Trust the workspace when prompted.
3. If VS Code asks to allow automatic tasks, choose **Allow**. If declined, run `TalentBridgeAI: START DEFAULT DJANGO WEBSITE (8000)` from **Terminal → Run Task**.
4. Keep the task terminal open. The task starts the server and keeps its manager attached to the server lifecycle.

## Important limits

This is a local Windows development workflow. It does not configure production hosting, public DNS, HTTPS, mail delivery, or Google OAuth credentials. OAuth still requires valid client credentials in the private `.env`. No startup script can guarantee the absence of every application bug; use the Django test suite and browser acceptance checks for each feature change.
