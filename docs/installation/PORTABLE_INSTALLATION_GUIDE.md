# Portable Windows installation

## Requirements

- Windows 10/11 and Python 3.11 or newer available through the Python launcher
  (`py`) or `python`.
- Write access to the extracted folder.
- Internet access the first time, to install packages listed in
  `legacy-django\requirements.txt`.

## Install and start

1. Extract the portable release into a writable folder on any drive. Do not
   extract it over a project containing data you need.
2. Open that extracted folder in VS Code, or use File Explorer.
3. Run `INSTALL_TALENTBRIDGEAI.bat` once, or run `START_TALENTBRIDGEAI.bat`
   directly. The existing project manager finds its root from its own script
   location, creates `legacy-django\.venv` if needed, installs requirements,
   creates a private `.env` only when absent, generates a local signing key,
   checks the database, safely applies pending migrations, collects static
   files, and starts Django.
4. The launcher prints the actual website URL and opens it after its health
   checks succeed. Keep the launcher terminal open while using the server.

No previous checkout, fixed drive letter, or absolute workspace path is
required. If another process owns the default port, the launcher selects an
available local port in its bounded candidate range and prints the actual URL.
It never terminates an unrelated process. Set `TALENTBRIDGEAI_PORT` to choose
the preferred starting port; the launcher can select a later available port
if that one is occupied. Google OAuth callback configuration must match the
actual port printed at startup.

## Configuration and accounts

The release contains `.env.example`, never the original `.env`. The launcher
copies the template locally and generates `DJANGO_SECRET_KEY`; do not share the
resulting `.env`. Google sign-in requires the owner to configure both OAuth
values privately and add the actual callback URL to the Google OAuth client.
SMTP is optional for local development; without it, Django uses its configured
local email backend.

The distributable ZIP intentionally contains no database or user accounts.
After installation, create an administrator locally using
`CREATE_SUPERUSER.bat`. For an existing installation, keep its database,
credentials, and uploads; do not replace them with a clean-release copy.

## Updating

Before an update, create a protected backup as described in
[BACKUP_GUIDE.md](BACKUP_GUIDE.md). Extract the release to a new folder and
review [DATA_PROTECTION_GUIDE.md](DATA_PROTECTION_GUIDE.md) before transferring
any local data. Do not copy a release ZIP over a live project.
