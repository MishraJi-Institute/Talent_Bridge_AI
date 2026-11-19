# TalentBridgeAI — Windows setup

1. Install Python 3.11, 3.12 or 3.13 and enable PATH.
2. Extract the ZIP to a writable folder.
3. Double-click `START_TALENTBRIDGEAI.bat`.
4. Keep its terminal open and use http://127.0.0.1:8000/.

The launcher creates/uses `legacy-django/.venv`, installs dependencies from `legacy-django/requirements.txt` when needed, prepares the private environment, applies pending migrations without dropping tables, runs Django checks and opens the real Django site after health checks.

## Which preview should I use?

- Port 8000 is the real Django website.
- Port 5500 is an optional static preview only. Its yellow banner is expected. Sign-in, Google OAuth, uploads, sessions and database actions require Django on port 8000.

If Firefox says it cannot connect to 127.0.0.1:8000, start `START_TALENTBRIDGEAI.bat` and keep the terminal open. Refreshing the browser alone will not start Django.

## Database and private settings

This archive includes `database/TalentBridgeAI.sqlite3` to preserve the project database that was supplied with the source archive. Back it up before changing or migrating data. `.env` and credentials are intentionally excluded; the launcher creates `.env` from `.env.example` if it is missing. Never share passwords, `.env`, OAuth secrets or private resume documents.

## Sign in and Google OAuth

Use `http://127.0.0.1:8000/login/` for email/password login. Google OAuth is optional and requires valid credentials in the private root `.env` plus the authorized redirect URI `http://127.0.0.1:8000/accounts/google/login/callback/`.

## Administrator

If the database has no superuser, run `CREATE_SUPERUSER.bat` and enter credentials privately. It must not reset an existing administrator password.

## Production

This launcher is for local development. Public deployment requires HTTPS, production secrets, secure cookies, allowed hosts, a production database/server and configured email delivery.
