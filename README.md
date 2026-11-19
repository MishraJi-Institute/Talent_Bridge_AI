# TalentBridge AI

TalentBridge AI uses Django for server-side authentication, Google sign-in, user/profile data, and job workflows. Run the Django server and configure Google's OAuth app for working social sign-in. Static output is a demo preview and does not provide server-backed authentication or account data.

## Run locally

Follow [README_RUN_DJANGO.md](./docs/setup/README_RUN_DJANGO.md) to install dependencies, configure the environment, migrate the database, and start Django. Use **`http://127.0.0.1:8000/`** (preferred) or **`http://127.0.0.1:8001/`** — the lifecycle manager keeps both ports working via an automatic redirect bridge. Login is **`/login/`** (for example `http://127.0.0.1:8000/login/`), not a raw filesystem HTML open. Do not open source HTML files directly or use Live Server for Django pages: those methods cannot process Django template tags or form actions. The page will show a setup message if opened this way. Do not use the static build to test authentication.

For save-and-refresh development behavior and the local status dashboard, see [LIVE_PREVIEW_SETUP.md](./docs/setup/LIVE_PREVIEW_SETUP.md). The source layout and non-destructive verification findings are documented in [PROJECT_LAYOUT.md](./docs/architecture/PROJECT_LAYOUT.md) and [PROJECT_STRUCTURE_REPORT.md](./docs/architecture/PROJECT_STRUCTURE_REPORT.md).

## Configure Google sign-in

Create OAuth apps with all providers you want to enable. Register these authorized redirect URIs with the matching apps:

```text
http://127.0.0.1:8000/accounts/google/login/callback/
```

Copy `.env.example` to `.env` in the project root and set `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET`. Keep all secrets in the server-side `.env`; never put them in JavaScript or commit them. For production, use the matching HTTPS callback URL and configure `DJANGO_ALLOWED_HOSTS`, a persistent `DJANGO_SECRET_KEY`, the database, and SMTP. See [README_RUN_DJANGO.md](./docs/setup/README_RUN_DJANGO.md) for setup details.

## Deploy

### GitHub Pages

The workflow at `.github/workflows/static.yml` builds the site and publishes only the generated `site/` directory when changes are pushed to `main`. Enable GitHub Pages with **GitHub Actions** as the build and deployment source in the repository settings.

### Netlify

Import the repository into Netlify. `netlify.toml` sets the build command to `python tools/build_static.py` and publishes `site/`. No server functions or dependency installation are required.

Only static assets are copied into `site/`; local configuration, SQLite data, Django code, and repository documentation are not included in the deployed artifact. A static-hosted copy cannot provide Django authentication or server-backed account data.

The static build adds a compact, responsive page-directory control to every HTML page. Its links are grouped by task and open in a floating panel, leaving each page's existing layout and design intact. Django-only page sections are omitted from this preview, sample content remains visible, and demo forms clearly state that they do not save data.

## Static preview

The static build remains available for visual previews. It does not include Django, database access, Google OAuth, or server-backed account workflows.

For a static preview with VS Code Live Server, install the workspace-recommended **Live Server** extension if VS Code prompts you, run `python tools/build_static.py` from the project folder, and select **Go Live** in the status bar. If **Go Live** is missing, open Extensions, search for `ritwickdey.LiveServer`, install it, and reload VS Code. The workspace config serves the generated `site/` folder, so `/pages/login.html` opens the rendered preview instead of the Django source template. On localhost, the Google sign-in button forwards to Django at `127.0.0.1:8000`; start Django and configure the Google credentials first. Restart Live Server after changing its root or rebuilding the preview.

When Django is running with `DJANGO_ENV=development` and `DJANGO_DEBUG=true` and no matching live jobs are available, the jobs page shows clearly labeled sample roles. Sample application links open a preview only and never create or submit an application. Production mode does not show these fallback job records.

## Latest repair and reference-image integration (14 November 2026)

The VS Code folder-open task starts the managed Django launcher via `tools/windows_manager.py` (`scripts/startup/START_TALENTBRIDGEAI.bat`). Port 8000/8001 is the primary development site. Port 5500 / `site/` is an optional static preview only.

Supplied office, avatar and skyline assets are wired into actual Django-rendered pages. The design board remains a blueprint rather than a static screenshot replacement. See:
- [Reference image implementation inventory](docs/homepage/REFERENCE_IMAGE_IMPLEMENTATION.md)
- [Bug-fix summary](docs/troubleshooting/BUG_FIX_SUMMARY.md)
- [Feature verification report](docs/reports/FEATURE_VERIFICATION_REPORT.md)
- [Database backup and recovery](docs/setup/DATABASE_BACKUP_AND_RECOVERY.md)
- [Django startup guide](docs/setup/README_RUN_DJANGO.md)
- [Docs index](docs/README.md) · [Folder map](docs/FOLDER_MAP.md)

The Django system check, all 138 jobs tests, local HTTP route/image checks and static-site build passed in the QA environment. Windows VS Code automatic startup and browser-visible rendering still require confirmation on the target PC; Google OAuth requires the owner's private credentials, and AI resume generation is not connected without an AI provider.


## Google OAuth

See [GOOGLE_OAUTH_SETUP.md](./docs/setup/GOOGLE_OAUTH_SETUP.md) for Google Cloud setup, secure local credential configuration, and callback URLs.

## Project layout (Step 1 organization)

- `frontend/` — pages, css, js, assets (images/logos/videos)
- `backend/legacy-django/` — Django project (root `legacy-django` is a compatibility junction)
- `docs/` — START_HERE + topic folders (audit, homepage, setup, troubleshooting, reports, development, …)
- `scripts/` — install, startup, maintenance, backup, diagnostics (root `*.bat` wrappers remain)
- `database/`, `private_media/`, `backups/` — preserved at repo root

