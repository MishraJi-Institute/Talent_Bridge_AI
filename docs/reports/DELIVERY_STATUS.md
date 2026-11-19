# TalentBridgeAI delivery status

This ZIP contains the supplied Django project with the current packaging-pass updates. See `docs/reports/DELIVERY_QA_REPORT.md` for exact changes, checks and runtime limitations.

## Current packaging-pass checks
- Python bytecode compilation: passed.
- JavaScript syntax: passed (48 files).
- Local HTML/CSS references: passed (64 HTML files and 39 CSS files).
- Static preview generation: passed.
- Updated avatar SVG copied to generated static output.
- ZIP integrity: checked after packaging.

## Important runtime boundary
A fresh Django runtime/test-suite run was not possible in the packaging environment because Django is not installed and package-network access is unavailable. Historical project notes report 138 Django tests passing at an earlier Windows QA checkpoint; that is not represented as a fresh test run of this final ZIP.

The Firefox `Unable to connect` screenshot indicates that Django was not listening at `127.0.0.1:8000` at that time. Start it using `START_TALENTBRIDGEAI.bat` or `OPEN_DJANGO_WEBSITE.bat` and keep the terminal open. Use port 8000 for sign-in and database-backed workflows. Port 5500 is an optional static preview.

## Local Windows startup
1. Extract the ZIP to a writable folder.
2. Open the `TalentBridgeAI` folder in VS Code/Cursor.
3. Double-click `START_TALENTBRIDGEAI.bat` or `OPEN_DJANGO_WEBSITE.bat`.
4. Keep the launcher terminal open.
5. Use `http://127.0.0.1:8000/`.

The existing SQLite database is preserved. Private `.env`, credentials, virtual environments, caches, backup folders, logs, and private media are excluded.
