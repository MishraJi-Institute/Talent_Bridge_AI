# Live preview

Open <http://127.0.0.1:8000/> while one Django development server is running. Start it with `START_TALENTBRIDGEAI.bat` only if port 8000 is not already listening; the launcher reuses a healthy managed server and does not start a duplicate.

The Django live-refresh monitor checks status every five seconds, times out a stalled health request, and backs off while Django is unavailable. It shows one persistent outage notice and clears it after a successful recovery check. Source fingerprints skip the virtual environment and collected static files.

Port 5500 is a separate static preview. Its informational banner explains which actions need Django; a 404 for `/__dev__/state/` on that port is expected and does not indicate a Django outage. Authentication, OAuth, uploads, dashboards, and database-backed features belong on port 8000.

CSS and JavaScript are served with `Cache-Control: no-store` on Django while DEBUG is on, so a normal reload picks up those files. Python and URL changes still need the development server to reload.

Progress notes are in `LIVE_PREVIEW_PROGRESS.md`.
