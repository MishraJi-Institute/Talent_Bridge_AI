# TalentBridgeAI — project layout

- `legacy-django/config/` — Django settings, WSGI/ASGI entry points, and URL routes.
- `legacy-django/jobs/` — the current modular Django app, models, views, tests, and migrations.
- `legacy-django/templates/` — Django-only templates, including the development preview dashboard.
- `legacy-django/static/` — Django-specific admin assets; `legacy-django/staticfiles/` is generated.
- `pages/` — source HTML pages used by Django routes and the static build.
- `css/` — shared source stylesheets, including development-preview styling.
- `js/` — shared source JavaScript, including live-preview refresh/status behavior.
- `images/`, `logo/`, `videos/` — visual assets.
- `database/` — the local SQLite database `TalentBridgeAI.sqlite3` and MySQL setup SQL.
- `docs/` — setup guides and project reports.
- `site/` — generated static deployment preview built by `build_static.py`; do not edit it as a source tree.
- `tools/` — local Windows lifecycle manager, backup, and portable-release tools.
- `private_media/`, `logs/`, `backups/` — runtime uploads, logs, and local backups; excluded from source archives.

```text
TalentBridgeAI/
├── legacy-django/
│   ├── config/
│   ├── jobs/
│   │   └── migrations/
│   ├── templates/
│   ├── static/
│   └── manage.py
├── pages/                 # Django/static-build HTML sources
├── css/                   # frontend CSS sources
├── js/                    # frontend JavaScript sources
├── images/ logo/ videos/  # frontend assets
├── database/              # database setup and local SQLite data
├── docs/                  # guides, architecture notes, reports
├── tools/                 # local lifecycle/maintenance tools
└── site/                  # generated static preview; not an editable source copy
```

The portable ZIP excludes `.env` credentials, SQLite databases, private uploads,
virtual environments, backups, logs, and generated `site/`/`staticfiles/`.
Create a separate protected backup with `CREATE_BACKUP.bat`; it contains private
data and is not encrypted. Build and verify a release with
`CREATE_PORTABLE_RELEASE.bat`. On first run, `RUN_DJANGO_WINDOWS.bat` creates a local `.env`,
installs dependencies, applies migrations, seeds repeatable demo data, checks the project,
collects static assets, and starts Django.

The included demo accounts are disabled and cannot sign in. Create your own administrator
once from the `legacy-django` folder:

```powershell
..\.venv\Scripts\python.exe manage.py createsuperuser
```

Keep OAuth credentials and other secrets in your private local `.env`; do not share that file.

Google Sign-In setup is documented in `GOOGLE_OAUTH_SETUP.md`. Credentials must be added privately to the local `.env` file; they are not included in this ZIP.
