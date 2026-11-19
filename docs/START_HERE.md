# Start TalentBridgeAI (Windows)

## Start the real Django website

1. Extract the ZIP to a writable folder.
2. Open the extracted `TalentBridgeAI` folder in VS Code or Cursor.
3. Double-click **`START_TALENTBRIDGEAI.bat`** (or run it from a terminal).
4. Keep the launcher terminal open. It creates/uses `legacy-django/.venv`, checks dependencies, loads the project-root `.env`, applies pending migrations non-destructively, runs Django checks, starts the Django development server and opens the browser only after its health checks pass.
5. Use the actual website URL printed by the launcher (normally
   **http://127.0.0.1:8000/**).

If the browser says **Unable to connect**, Django is not currently running. Start it with `START_TALENTBRIDGEAI.bat`; a browser refresh cannot start the server.

## Important: do not use the static preview for login

- The launcher-printed URL (default port 8000) — real Django website; use
  this for sign-in, sign-up, uploads, dashboards and database-backed actions.
- `http://127.0.0.1:5500/site/` — optional static preview only. It cannot authenticate users or perform Django database operations. The yellow static-preview notice is expected there.

## Important files

- Django source: `legacy-django/`
- Public source pages: `pages/`
- Homepage source: `index.html`
- CSS / JavaScript / images: `css/`, `js/`, `images/`
- Generated static preview: `site/`
- SQLite database (if present in this package): `database/TalentBridgeAI.sqlite3`
- Private local settings: `.env` (not included; created from `.env.example` when needed)
- Start: `START_TALENTBRIDGEAI.bat`
- Restart: `RESTART_TALENTBRIDGEAI.bat`
- Stop: `STOP_TALENTBRIDGEAI.bat`
- Health/status: `CHECK_STATUS.bat`
- Safe repair checks: `REPAIR_TALENTBRIDGEAI.bat`

## Sign in

Open `/login/` at the launcher-printed website URL. The legacy URL
`/pages/login.html` is also routed to the same Django login view.
Email/password sign-in does not require Google OAuth. Google sign-in requires
valid owner-configured credentials in the private root `.env` and a matching
Google Cloud redirect URI using the actual running port:
`http://127.0.0.1:<port>/accounts/google/login/callback/`

Never share `.env`, passwords, OAuth client secrets or private resume documents.

## Administrator

If the included database already has a superuser, use the credentials you previously configured. If no superuser exists, run `CREATE_SUPERUSER.bat` and enter credentials privately in its terminal. The helper must not reset an existing account's password.

## Data and production notes

Do not delete or replace the SQLite database if it contains records you need. Make a backup before manual database changes. The local Django development server is not a production deployment; public hosting requires HTTPS, production secrets, secure cookies, allowed hosts, a production database/server and configured email delivery.

## Keep Django running automatically (Windows)

If you repeatedly see Firefox "Unable to connect" at the URL printed by the
launcher, Windows has no healthy Django process at that address. This is a
stopped-server condition, not a page-formatting problem.

1. Double-click **`FIX_SERVER_PERMANENTLY.bat` once**.
2. It registers a Windows logon task, launches the managed Django server hidden in the background, and waits for an HTTP 200 health check.
3. Keep the extracted project folder in the same location. Django will be started again automatically at future Windows sign-ins.
4. Use **`CHECK_DJANGO_SERVER.bat`** to check the server at any time.
5. Use **`DISABLE_AUTO_SERVER_STARTUP.bat`** if you later want to remove automatic startup.

This is a local-development setup: it starts when your Windows account signs in and the computer is on. It cannot serve the site while the computer is powered off, asleep, or disconnected. If startup fails, inspect `logs\\setup.log` and `logs\\server.log`; do not delete the database or `.env`.
