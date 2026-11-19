# TalentBridgeAI activity

Updated: 2026-11-13

Status: WORKING
Phase: Remaining public and account pages
Page, file, or feature: Deployment security and account recovery
Last completed action: Verified password reset end-to-end, corrected account navigation, passed all 133 Django tests, inspected the actual Django pages, and checked responsive behavior across 27 public/auth routes.
Current action: Continue the local security/responsive audit while preserving the database and signed-in owner data.
Next action: Continue remaining local public/account work; before any public deployment, select the TLS/reverse-proxy topology and configure HTTPS redirects, secure cookies, and HSTS.
Error or blocker: Owner confirmed local-only use for now. Production `check --deploy` warns that HSTS, HTTPS redirect, secure session cookies, and secure CSRF cookies are unset; these were not enabled on the local HTTP site. SMTP is not configured, first-time Google signup and owner Super Admin setup require owner actions, AI requires a provider, and final delivery remains unfinished.

Files changed in the previous dashboard/Admin increment:
- `css/dashboard/cdashboard.css`
- `css/dashboard/jdashboard.css`
- `css/dashboard/jdashboard-redesign.css`
- `js/dashboard/cdashboard.js`
- `pages/dashboard/jdashboard.html`
- `pages/admin-dashboard.html`
- `legacy-django/jobs/views.py`
- `legacy-django/jobs/tests.py`

Files changed in the homepage and Job Search/Company increments:
- `index.html`
- `css/tb-homepage.css`
- `legacy-django/jobs/templates/jobs/home.html`
- `legacy-django/jobs/templates/companies/list.html`
- `legacy-django/jobs/templates/companies/detail.html`
- `css/portal-pages.css`
- `legacy-django/jobs/tests.py`
- `TALENTBRIDGEAI_PROGRESS.md`
- `DEVELOPMENT_PROGRESS.md`
- `ACTIVITY_NOW.md`

Verification: All 10 focused authentication/recovery tests passed on a temporary test database; the actual `/forgot-password/`, `/signup/`, `/signup/job-seeker/`, and `/login/` pages were inspected on Django. These plus employer signup showed no horizontal overflow at the configured 390px viewport. The complete Django suite passed all 133 tests; `manage.py check` and `_check_links.py` (64 HTML / 37 CSS) passed. No live user records were changed and signup forms were not submitted. Previously, 8 Resume Upload/Library tests passed and live routes redirected to login; homepage (5), dashboard/Admin (23), and Job Search/Company (7) tests passed.

Progress estimate: prior coarse estimate remains overall 59%; implementation 85%; testing 63%; verification 72%.
Page inventory: 53 documented workflow/page entries — 12 complete, 39 partial, 0 blocked, 2 not implemented; 51 active and 2 inactive.
Resume Upload remains complete for private PDF/DOC/DOCX uploads up to 5 MB, validation, PDF preview, download, replacement, and deletion; its 8 focused acceptance tests were re-run successfully.
Other remaining work: first-time Google signup and direct Cloud Console review, email verification/MFA, connected AI features until a provider is configured, remaining public/account workflows, final PDF, genuine screenshots, and clean ZIP.

The static server on port 5500 is a separate preview and has no Django API; backend actions must be verified on port 8000. The live database and records were not modified in this increment; automated tests used Django's temporary test database.

Chat cannot add a message while a tool call is still running. This file is the live status. logs/activity.log keeps the history. When tools/activity_pulse.ps1 is running, it sends a Windows balloon about every 2 minutes while the activity heartbeat is fresh. Sounds and short spoken announcements are sent only for marked milestones, not routine file edits.


## 14 November 2026 — Critical preview, authentication route and reference-image repair
- Confirmed the supplied design board and inspected all image assets in `images/`, `logo/`, and `legacy-django/static/`.
- Root cause of VS Code preview mismatch: `.vscode/tasks.json` called `.vscode/start-django.ps1`, which contained a hardcoded old Windows workspace path and looked for the virtual environment in the wrong directory. Updated the folder-open task to call the project-managed `START_TALENTBRIDGEAI.bat` / `tools/windows_manager.py` lifecycle instead. Replaced the PowerShell file with a portable wrapper.
- Login page itself already uses Django `login_view`, CSRF token, POST `/login/`, email/password authentication and session login. Existing automated tests cover valid email/password login, invalid credentials, session creation, logout and `/pages/login.html`. The observed Firefox error is a server-not-listening condition, not proof of a broken password form.
- Integrated the supplied office image into homepage, login visual and employer banner; supplied avatar SVG into homepage candidate card; supplied Manhattan skyline into About page.
- Added `docs/homepage/REFERENCE_IMAGE_IMPLEMENTATION.md` and Django regression tests for image URLs.
- Runtime/browser test status: not run in this environment (Django package unavailable; no dependency installation/network). Do not treat local template/source checks as proof that the user's Windows server is running.

## 14 November 2026 — Reference images, login route and Django-first startup
- Replaced the stale `.vscode/start-django.ps1` task target with the project-managed `START_TALENTBRIDGEAI.bat` lifecycle. The old hardcoded workspace path was the confirmed VS Code folder-open startup defect.
- The login view is already a real Django email/password POST flow with CSRF, session login and logout. Existing auth tests verify valid login/session, invalid credentials and logout; no real user/admin password was changed.
- Added supplied office image to homepage/login/employer banner, supplied avatar SVG to the homepage candidate preview and supplied skyline image to About page. Full inventory: `docs/homepage/REFERENCE_IMAGE_IMPLEMENTATION.md`.
- Added regression tests for image markup and Django-served asset endpoints.
- Fixed `build_static.py` mapping for `resume-builder`; fixed visible field-level Resume Builder validation; fixed About canonical home link.
- Django system check: PASS. Django test suite: 138/138 PASS. Static build: PASS. Python compileall: PASS.
- QA Django server on port 8000 returned HTTP 200 for homepage, login, legacy login URL, both signup URLs, supplied image URLs and shared integration CSS. Tests used a temporary QA copy of SQLite and that copy was removed afterward.
- Browser screenshot automation was blocked by Chromium policy; actual visual browser rendering is not claimed. Windows VS Code automatic task still needs first-run confirmation on the user's PC.
- Package DB preserves user/profile/social identity rows while clearing OAuth secrets and session rows. Private `.env`, signing key, private media, backups, logs, venvs and caches are excluded.
