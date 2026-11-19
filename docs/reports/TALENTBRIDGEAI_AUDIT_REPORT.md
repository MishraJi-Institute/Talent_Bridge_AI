# TalentBridgeAI audit report

Date: 2026-11-12  
Mode: inspection, backup, and documentation only. No feature code was changed.  
Backup: `backups/audit_20261112_154417/`

This report records what was inspected and what was executed in this step. Earlier checkpoints reported a 78-test suite. That suite was not re-run during this step, so those older results are historical only.

## Architecture

TalentBridgeAI is one Django project plus a root-level frontend. It is not a multi-app suite.

| Area | Location |
| --- | --- |
| Django project | `legacy-django/` (`manage.py`, `config/`) |
| Application | `legacy-django/jobs/` |
| Settings and routes | `legacy-django/config/settings.py`, `legacy-django/config/urls.py` |
| Models | `legacy-django/jobs/models.py` |
| Views, forms, auth adapters | `legacy-django/jobs/views.py`, `forms.py`, `adapters.py`, `backends.py`, `google_oauth.py` |
| Migrations | `legacy-django/jobs/migrations/0001` through `0007` |
| Page templates | `pages/` (also on the Django template path) |
| Django-only templates | `legacy-django/templates/`, `legacy-django/jobs/templates/jobs/home.html` |
| CSS, JavaScript, images | `css/`, `js/`, `images/` |
| Generated static preview | `site/` (not the live Django source) |
| Uploads | `private_media/` (empty at audit time) |
| Database | `database/TalentBridgeAI.sqlite3` |
| Local launcher | `tools/windows_manager.py` and the root `.bat` / `.ps1` scripts |
| Python environment | `legacy-django/.venv` |
| Dependencies | `legacy-django/requirements.txt`: Django 5.2.x, django-allauth 65.x, python-dotenv, Pillow, PyMySQL |

`settings.py` still comments that it was generated with Django 6.1. The installed and pinned release is Django 5.2. `manage.py check` passed on 5.2.

There is no Git repository in this folder.

### Authentication and roles

- Email/password registration for `job_seeker` and `employer` in `jobs/views.py`.
- Employer companies stay unapproved until a staff user approves them.
- Login accepts email or username through `jobs/backends.py`, then Django and django-allauth.
- Sessions use the database (`SESSION_ENGINE = django.contrib.sessions.backends.db`) and a 14-day cookie.
- Google sign-in is implemented with django-allauth, but new Google users must finish a role form (`SOCIALACCOUNT_AUTO_SIGNUP = False`).
- Roles stored on `Profile`: `job_seeker` and `employer`. Staff/superuser is Django's own `is_staff` / `is_superuser`. There is no separate Admin user model.

### AI integrations

No application code calls an AI provider. `reportlab` is present in the virtual environment and is not imported by `jobs` and is not listed in `requirements.txt`. Resume handling stores a file. It does not parse one.

### Startup scripts

| Script | Role |
| --- | --- |
| `START_TALENTBRIDGEAI.bat` | Starts Django through `tools/windows_manager.py start` |
| `STOP_TALENTBRIDGEAI.bat` | Stops the managed process tree |
| `RUN_DJANGO_WINDOWS.bat` | Calls the start script |
| `SETUP_AND_RUN_WINDOWS.bat`, `INSTALL_TALENTBRIDGEAI.bat`, `REPAIR_TALENTBRIDGEAI.bat`, `UPDATE_TALENTBRIDGEAI.bat` | Install, repair, and update wrappers |
| `ENABLE_AUTO_STARTUP.bat`, `DISABLE_AUTO_STARTUP.bat` | Optional Windows logon task |
| `CONNECT_GOOGLE_OAUTH.ps1`, `CONNECT_GOOGLE_OAUTH.bat` | Writes OAuth values into the private `.env` and syncs the provider |
| `.vscode/tasks.json` | Runs the launcher when the folder opens |

The launcher is a foreground console process. It is not a Windows service. After a reboot, port 8000 stays closed until the launcher, VS Code task, or logon task starts it. That is the `ERR_CONNECTION_REFUSED` condition.

## Checks executed in this step

- `manage.py check`: no issues.
- Migration plan: no unapplied migrations.
- ORM counts on the live SQLite file: 0 users, 0 profiles, 0 companies, 0 jobs, 0 applications, 0 Google `SocialApp` rows.
- Django site row: id 1, domain `example.com`.
- SQLite backup API copy: `PRAGMA integrity_check` = `ok`. Original file size unchanged at 323,584 bytes.
- Live HTTP, with the server already running: `/login/` 200, `/admin/login/` 200, `/jobs/` 200.
- The live login page renders the Google button disabled and shows the not-configured notice.
- `.env` was not printed. Key presence only: database settings are set; both Google OAuth fields are non-empty; `DJANGO_SECRET_KEY` appears twice, first empty and second populated. A fresh `load_dotenv` resolves a 64-character secret. `.django_secret_key` does not exist.

The process listening on port 8000 was started before `.env` was last written (parent start 11:43, `.env` write 11:53, autoreload worker 12:02). django-allauth therefore still behaves as if Google credentials are absent. A code reload does not replace environment variables the parent already loaded.

## Feature status

| # | Feature | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Job seeker registration, login, and dashboard | PARTIAL | Signup and login views persist `User` and `Profile`. The seeker dashboard at `pages/dashboard/jdashboard.html` stores profile, jobs, and applications in `localStorage` (`js/dashboard/jdashboard.js`). The database has no users, so no seeker session exists to resume. |
| 2 | Employer registration, login, and dashboard | PARTIAL | Employer signup creates an unapproved `Company` and blocks publishing until staff approval. `pages/dashboard/cdashboard.html` is a browser demo (hard-coded “TechSphere Solutions”, `localStorage`, Reset demo). It is not the database recruitment workspace. |
| 3 | Admin login and dashboard | BROKEN | `/admin/login/` returns 200, and `pages/admin-dashboard.html` is wired for staff users. `auth_user` has 0 rows, so no superuser can sign in. `legacy-django/_reset_admin.py` and `_change_admin_password.py` look up username `mishraji`, which is not in this database. `legacy-django/templates/admin/login.html` has a stray CSS line after the background URL. |
| 4 | Google Sign-In and Sign-Up | BROKEN | Routes, adapters, signup form, and tests exist from the earlier checkpoint. The running server still disables the button. No `SocialApp` row exists. Site domain is `example.com`. Live Google consent was not tested. |
| 5 | Job posting, search, and details | PARTIAL | `create_job`, `job_list`, and `job_detail` are database-backed. The jobs table is empty. With DEBUG on, `/jobs/` shows in-memory sample roles and does not save applications for those samples. |
| 6 | Job applications and tracking | PARTIAL | `Application` plus apply, applied-jobs, status update, and notifications exist. There are 0 applications. Sample roles cannot be submitted. The seeker dashboard application list is local demo data. |
| 7 | Resume upload and Resume Library | PARTIAL | One resume can be uploaded on `resume-management` with extension, 5 MB, and file-signature checks. There is no multi-file library model. The page also always shows a fake “Demo_Candidate_Frontend_Resume.pdf” card. `private_media/` is empty. |
| 8 | AI Resume Builder and resume parsing | NOT IMPLEMENTED | No parser, provider client, or generated-resume pipeline in `jobs` or the dashboard scripts. |
| 9 | AI Smart Profile Card | PARTIAL | The card UI in the seeker dashboard renders and saves to `localStorage`. It is not generated by an AI service and is not stored on `Profile`. |
| 10 | Employer recruitment and candidate management | PARTIAL | Database pages exist for manage jobs, applications, candidate details, interviews, and company approval. The visual employer dashboard does not use those records. |
| 11 | Database models, migrations, and connectivity | COMPLETE | SQLite connects, `manage.py check` passed, and no migrations are pending. Models cover company, job, profile, application, contact, saved job, notification, and interview. |
| 12 | Frontend responsiveness, navigation, and buttons | PARTIAL | Login, admin login, and jobs respond over HTTP. Dashboard buttons and several unmapped page forms are browser-only. This step did not click through every breakpoint. |
| 13 | Server startup, shutdown, and restart | PARTIAL | The server was listening during this audit and earlier `logs/setup.log` shows successful starts. Pip install failed twice before a later success. Closing the launcher console stops Django. `.env` edits are ignored until a full process restart. The launcher does not call `seed_demo_data` or `ensure_superuser`, despite older docs saying demo rows are inserted. |

Status counts: COMPLETE 1, PARTIAL 9, BROKEN 2, NOT IMPLEMENTED 1, BLOCKED 0.

## Authentication and OAuth

- Password hashing uses Django's `create_user` / `set_password`. Reset helpers do not embed a password; they prompt with `getpass`. They still fail today because `mishraji` does not exist.
- Sessions survive a process restart only while `DJANGO_SECRET_KEY` stays stable. The duplicate empty key line is unsafe if a loader keeps the first value. Current python-dotenv uses the populated value.
- Google credentials are present in the private `.env` and absent from `.env.example`. The running process has not loaded them. `docs/troubleshooting/REMAINING_ISSUES.md` still says both values are empty. That document is stale.
- Required Google redirect URI remains `http://127.0.0.1:8000/accounts/google/login/callback/`. This audit could not see the Google Cloud client, so that console setting is unverified.
- `SITE_ID` 1 points at `example.com`. Password-reset and other absolute links can be built for the wrong host until that row is corrected.

## Database

- Engine: SQLite, file `database/TalentBridgeAI.sqlite3`.
- Original file was not opened for writes. The backup used SQLite's backup API in read-only mode.
- Schema is migrated. Business tables are empty.
- `README_RUN_DJANGO.md` says the launcher seeds demo users and jobs. `tools/windows_manager.py` does not call `seed_demo_data`.

## Missing or mismatched pieces

- No superuser.
- No Google `SocialApp` row.
- Site domain still `example.com`.
- No AI provider package in `requirements.txt`.
- No Resume Library model.
- No job-match scoring model. Job search is keyword and location only.
- `reportlab` is installed outside `requirements.txt` and unused.
- Admin login stylesheet has a broken extra CSS line.
- Node.js is not installed. Earlier notes already recorded that `node --check` could not run.

## Files that later work should touch

Do not change these until the next approved step.

- `tools/windows_manager.py` — reload environment on restart; align seed/superuser behavior with the docs.
- `legacy-django/config/settings.py` — DEBUG/env loading only if a restart fix belongs there.
- `legacy-django/jobs/google_oauth.py` and the site fixture/data — domain and SocialApp sync after a clean restart.
- `legacy-django/templates/admin/login.html` — CSS typo.
- `legacy-django/jobs/models.py` and a new migration — only if Resume Library or matching is approved.
- `legacy-django/jobs/views.py` — connect dashboard actions that should hit the database.
- `pages/dashboard/jdashboard.html`, `js/dashboard/jdashboard.js` — seeker dashboard data source.
- `pages/dashboard/cdashboard.html`, `js/dashboard/cdashboard.js` — employer dashboard data source.
- `pages/resume-management.html` — separate the sample card from a real upload.
- `docs/troubleshooting/REMAINING_ISSUES.md`, `README_RUN_DJANGO.md` — correct the empty-credential and auto-seed statements.

## External requirements

- A full Django restart after `.env` changes, with your approval, before Google can be retested.
- Google Cloud authorized JavaScript origin `http://127.0.0.1:8000` and redirect URI `http://127.0.0.1:8000/accounts/google/login/callback/`.
- Your choice of admin username and password. This step did not create an account.
- An AI provider and API key if resume parsing, resume generation, or match scoring is in scope. None is configured.
- SMTP settings only if password-reset email must leave the console backend.

## Security notes (no secret values)

- `.env` is gitignored. This folder is not a Git repo. The backup excluded `.env` and any secret-key file.
- `.env.example` contains empty placeholders only.
- Resume download is gated by ownership or by the employer who owns the application. Uploads are not served from a public `/media/` route.
- Upload checks cover extension, size, and PDF/OLE/DOCX signatures. There is no malware scanner.
- The launcher forces `DJANGO_ENV=development` and `DJANGO_DEBUG=true` for its own process. A raw `manage.py runserver` without those variables stays in the production DEBUG-off path because `DJANGO_ENV` defaults to `production`.
- Static files are served by `django.views.static.serve` even when DEBUG is off. That is acceptable locally and unsafe as a public deployment.
