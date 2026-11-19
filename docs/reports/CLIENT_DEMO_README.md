# TalentBridge AI - Client Demo Build

## IMPORTANT: use the Django server, not VS Code Live Server
Real email/password authentication, Google OAuth, CSRF protection, and database writes are served by Django.

1. Extract/merge this archive into your existing `TalentBridgeAI` project folder.
2. Do NOT delete or replace your existing `.env` or `database/TalentBridgeAI.sqlite3`.
   This update archive intentionally does not contain either file, so your local OAuth
   credentials and existing users remain in place when merging/extracting over the project.
3. Double-click `FINAL_CLIENT_DEMO.bat`, or run it from PowerShell.
4. Open http://127.0.0.1:8000/ and use the site's Sign In / Sign Up links.
5. Do not use http://127.0.0.1:5500/ for authentication. That is a static preview server.
   If opened there, the page now explains that real authentication must use Django.

## Google OAuth
The Django Google provider requests `prompt=select_account` so the account chooser is shown.
The existing `.env` must contain:
- GOOGLE_OAUTH_CLIENT_ID
- GOOGLE_OAUTH_CLIENT_SECRET

In Google Cloud Console, the Web OAuth client must include this Authorized redirect URI:
`http://127.0.0.1:8000/accounts/google/login/callback/`

Never commit/share `.env` or screenshots showing the Client Secret. Rotate any secret previously exposed.

## Validation performed on this update
- Python source compilation: passed (41 Python files).
- JavaScript syntax checks: passed for the four updated JS files.
- Static HTML/CSS local-reference audit: passed (55 HTML files, 33 CSS files).
- Django runtime checks/tests were not rerun in this packaging environment because the uploaded
  Windows virtual environment cannot execute here. Run the launcher on the target Windows machine;
  it installs dependencies if needed, migrates without deleting the database, runs Django checks,
  and starts the server. A successful `manage.py check` is not a substitute for testing real
  Google OAuth with the configured Google Cloud client.
