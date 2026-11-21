# Start TalentBridgeAI (Windows)

## Super Admin login (local — use this first)

1. Run **`START_TALENTBRIDGEAI.bat`** and leave the terminal open.
2. Open in **Chrome or Edge** (not VS Code Simple Browser):

| What | URL |
|------|-----|
| **Django Admin (superuser)** | [http://127.0.0.1:8000/admin/login/](http://127.0.0.1:8000/admin/login/) |
| Admin after sign-in | [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) |
| Public sign-in | [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/) |
| Dev status | [http://127.0.0.1:8000/__dev__/](http://127.0.0.1:8000/__dev__/) |

Local database currently has **at least one superuser** configured. Use the username and password you set with `CREATE_SUPERUSER.bat` (passwords stay private — never commit `.env`). To create one if missing: **`scripts/install/CREATE_SUPERUSER.bat`**.

Live domain admin works only after you deploy **full Django on your VPS** with HTTPS, e.g. `https://talentbridge.qd.je/admin/login/`. GitHub Pages static site has **no** Django admin.

---

## Work order (files & tasks)

1. **Secrets** — edit project-root `.env` only (never GitHub).
2. **Django backend** — `backend/legacy-django/` (`manage.py`, migrations, `jobs/`).
3. **Pages / UI** — `frontend/pages/`, `frontend/css/`, `frontend/js/`, root `index.html`.
4. **Database** — `database/TalentBridgeAI.sqlite3` (local); run `RESTART_TALENTBRIDGEAI.bat` after schema changes.
5. **Static live preview** — after UI edits: `python tools/build_static.py` → output in `site/`.
6. **Domain / GitHub** — push `main` only when you confirm sync; set GitHub variable `GOOGLE_OAUTH_CLIENT_ID`.

Full tree: **`docs/FOLDER_MAP.md`**. Scripts: **`scripts/startup/`** (start, restart, stop).

---

## Start the real Django website

1. Extract the ZIP to a writable folder.
2. Open the extracted `TalentBridgeAI` folder in VS Code or Cursor.
3. Double-click **`START_TALENTBRIDGEAI.bat`** (or run it from a terminal).
4. Keep the launcher terminal open. It creates/uses `backend/legacy-django/.venv`, checks dependencies, loads the project-root `.env`, applies pending migrations non-destructively, runs Django checks, starts the Django development server and opens the browser only after its health checks pass.
5. Use the actual website URL printed by the launcher (normally
   **http://127.0.0.1:8000/**).

If the browser says **Unable to connect** or **connection refused**, Django is not running (often after a reboot). Run `START_TALENTBRIDGEAI.bat` or one-time `FIX_SERVER_PERMANENTLY.bat`; refreshing the browser cannot start the server.

## Important: do not use the static preview for login

- The launcher-printed URL (default port 8000) — real Django website; use
  this for sign-in, sign-up, uploads, dashboards and database-backed actions.
- `http://127.0.0.1:5500/site/` — optional static preview only. It cannot authenticate users or perform Django database operations. The yellow static-preview notice is expected there.

## Important files

- Django source: `backend/legacy-django/` (junction `legacy-django/` at repo root if present)
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

See **Super Admin login** at the top of this file. If no superuser exists, run `scripts/install/CREATE_SUPERUSER.bat`.

## Data and production notes

Do not delete or replace the SQLite database if it contains records you need. Make a backup before manual database changes. The local Django development server is not a production deployment; public hosting requires HTTPS, production secrets, secure cookies, allowed hosts, a production database/server and configured email delivery.

## Keep Django running automatically (Windows)

**`ERR_CONNECTION_REFUSED` / “This site can’t be reached”** at `http://127.0.0.1:8000/admin/` means **Django is not running** (common right after a PC restart). It is not a wrong password problem.

1. One-time (recommended): double-click **`FIX_SERVER_PERMANENTLY.bat`** at the project root.
2. It writes a portable launcher under `%LOCALAPPDATA%\\TalentBridgeAI\\boot_on_logon.cmd`, registers **Windows sign-in** startup (Startup folder + Task Scheduler, ~45s after login), and starts Django in the **background** now.
3. After you **move** this folder to another path or PC: open the folder once and run **`START_TALENTBRIDGEAI.bat`** (or FIX again) so auto-start points to the new location.
4. **`CHECK_DJANGO_SERVER.bat`** — is the server up?
5. **`scripts/shutdown/DISABLE_AUTO_SERVER_STARTUP.bat`** — turn off auto-start.

Every normal **`START_TALENTBRIDGEAI.bat`** also refreshes auto-start registration (unless `.env` has `TALENTBRIDGEAI_AUTO_LOGON=0`).

This is **local only**: the PC must be on and you must be signed in. It cannot serve admin while the machine is off or asleep. Failures: `logs/setup.log`, `logs/server.log`.
