# Bug Fix Summary — 14 November 2026

## Confirmed root causes
1. `.vscode/tasks.json` invoked `.vscode/start-django.ps1`, whose `ROOT` was hardcoded to an old machine-specific directory and whose virtual-environment lookup expected the venv at the repository root. The actual managed environment is `legacy-django/.venv`.
2. The sign-in URL was being opened while Django was not listening on port 8000. The login view and route already existed; the Firefox message was a connection-refused/server-startup symptom, not an authentication form error.
3. `build_static.py` did not map the `resume-builder` Django URL tag, so static-site generation stopped on that template.
4. Resume Builder rendered the form controls but omitted field-level form errors, so invalid email feedback was not visible.
5. About page branding linked to a relative `../index.html` instead of the canonical Django homepage route.

## Changes
- VS Code folder-open task now calls `START_TALENTBRIDGEAI.bat`, which delegates to `tools/windows_manager.py` for venv, dependency, migration, server lifecycle and HTTP health checks.
- `.vscode/start-django.ps1` is now a portable wrapper; no hardcoded E: drive path remains.
- Live Server is listed as an unwanted extension; its automatic browser launch is disabled. Static preview is retained as optional output.
- Supplied office, avatar and skyline images are wired into actual Django templates/CSS.
- Employer dashboard banner now uses the supplied local office image instead of a remote Unsplash URL.
- Added reference image inventory and regression tests.
- Added missing static route mapping and visible resume field errors.
- Fixed About page home navigation to `/`.

## Security and data preservation
- Original upload archive not modified.
- Existing SQLite user/profile/social identity rows preserved in the packaged DB.
- Packaged DB has OAuth client secrets and old sessions cleared.
- `.env`, signing key file, private media, backups, logs, venvs and caches excluded from delivery.
