# TalentBridge AI — Windows setup

## First run and automatic startup

1. Extract this ZIP to a writable folder.
2. Open the extracted `TalentBridgeAI` folder in VS Code.
3. If VS Code asks whether to allow automatic tasks, choose **Allow**. The workspace task runs `START_TALENTBRIDGEAI.bat` when the folder opens. This invokes `tools/windows_manager.py` from the extracted workspace root; the old machine-specific PowerShell path is no longer used.
4. The launcher creates/uses the project virtual environment, installs the Django dependencies, creates `.env` only if missing, prepares the database, applies pending migrations, and checks the homepage, login, and both signup routes. It opens the browser at `http://127.0.0.1:8000/` only after those HTTP checks pass. It does not insert demo records.
5. Django runs attached to the VS Code task terminal, which remains active while the server is running. Press Ctrl+C in that terminal to stop it. Closing the terminal or VS Code also stops the development server.

If automatic tasks are not enabled, double-click `START_TALENTBRIDGEAI.bat` or run it from PowerShell; that terminal stays open while Django runs. Startup failures are reported in the terminal and recorded in `logs/setup.log` and `logs/server.log`. Python 3.11, 3.12, or 3.13 and an internet connection are required on first setup. The virtual environment is created locally and is not bundled in the ZIP.

## Live development preview

Open [http://127.0.0.1:8000/__dev__/](http://127.0.0.1:8000/__dev__/) for the development status dashboard. It reports the local server, frontend assets, Django checks, current website URL, and the active server start time.

- The Windows launcher sets `DJANGO_DEBUG=true` for its local Django process and starts the normal Django autoreloader. Saving Python code restarts Django automatically.
- Saving a template or JavaScript file refreshes the open page. CSS-only changes replace local stylesheets in place, without a full-page refresh.
- If Django is temporarily unavailable after a backend edit, the browser preview reports the connection error and retries. Check `logs/server.log` for Python tracebacks or startup errors.
- Django's detailed debug pages and this dashboard are available only when `DEBUG` is enabled. Production processes must set `DJANGO_DEBUG=false`; do not use the local launcher as a production server.
- This project uses ordinary browser JavaScript rather than a frontend bundler, so framework-style component HMR is not available. The static preview in `site/` is generated output; Django-served pages use the root `pages/`, `css/`, and `js/` source folders.

## Database

The default local database is SQLite at `database/TalentBridgeAI.sqlite3`. Django migrations create all application and framework tables automatically. The database file is generated on first run and is deliberately not bundled, so no old or machine-specific database is carried into a fresh install.

To use MySQL instead:
1. Install and start MySQL Server.
2. Edit the project-root `.env` and set `DB_ENGINE=mysql`, `DB_NAME=TalentBridgeAI`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`.
3. Run `RUN_DJANGO_WINDOWS.bat` again. The launcher creates the database if needed and then Django migrations create the tables.

The SQL file `database/create_mysql_database.sql` is also provided. Do not delete your existing database to reinstall this project. The setup scripts never drop or erase existing tables.

## Demo data

Startup does not insert demo users, companies, or jobs. Do not run `seed_demo_data` unless you explicitly want sample rows. The launcher never deletes or recreates the SQLite file.

## Administrator account

If no superuser exists, double-click `CREATE_SUPERUSER.bat` and enter the username, email, and password in that window. The command does nothing when a superuser is already present, and it never resets an existing password. Do not put the password in a file or in chat.

## Restart after configuration changes

`START_TALENTBRIDGEAI.bat` leaves an already-running server in place. `.env` changes, including Google OAuth values, are loaded only by a new process. Double-click `RESTART_TALENTBRIDGEAI.bat` and leave that window open. Automatic logon startup is not turned on by the repair.

## URLs

- Home: http://127.0.0.1:8000/
- Sign in: http://127.0.0.1:8000/login/
- Admin: http://127.0.0.1:8000/admin/
- Jobs: http://127.0.0.1:8000/jobs/

Use the Django URLs on port 8000 for authentication and database-backed workflows. Do not use `file://` or VS Code Live Server on port 5500 to test login, signup, employer approval, or database operations. The `site/` directory is only a static visual preview and cannot run Django workflows.

## Google sign-in

Google sign-in is optional. Both `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` must be set in the private project-root `.env`. Restart Django after changing them. In Google Cloud Console, open the OAuth Web client and verify:

- Authorized JavaScript origin: `http://127.0.0.1:8000`
- Authorized redirect URI: `http://127.0.0.1:8000/accounts/google/login/callback/`

The local Django callback route is that same path. An enabled button only means Django loaded both values. It does not prove the Google consent screen succeeded. Never commit or share `.env`. Without valid credentials, email/password login remains available.

## Important limits

This is a local development launcher, not a production deployment service. It starts when VS Code opens the trusted workspace and stops when the server terminal or VS Code is closed. Windows restart requires opening the project again. Production deployment needs HTTPS, production secrets, secure cookie settings, configured email delivery, and a production web server.


## Django-first VS Code preview

See [DJANGO_DEFAULT_PREVIEW_FIX.md](DJANGO_DEFAULT_PREVIEW_FIX.md) for the default VS Code task, browser health gate, status/open/stop/restart commands, and optional static-preview behavior. The workspace no longer recommends VS Code Live Server; port 5500 remains optional and is not the application preview.

## Reference-image implementation
The design board is a specification, not a static website replacement. Actual local images are wired into the Django homepage, login visual, About page and employer dashboard. See `docs/homepage/REFERENCE_IMAGE_IMPLEMENTATION.md` for filenames and paths.

## Verification and limitations
See `docs/reports/FEATURE_VERIFICATION_REPORT.md` and `docs/troubleshooting/BUG_FIX_SUMMARY.md`. The Django test suite and local HTTP checks passed in the QA environment. Google OAuth needs private owner credentials. AI resume generation is not connected until an AI provider is configured. The Windows VS Code automatic task must be allowed on first folder open.
