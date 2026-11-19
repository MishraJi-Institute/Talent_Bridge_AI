# TalentBridgeAI — Reproducible Startup Guide (Day 10)

**Date:** 2026-11-18  
**Audience:** Another developer joining this workspace  
**Secrets:** Never commit or paste `.env` values. Use `.env.example` as a template only.

---

## 1. Prerequisites

| Requirement | Notes |
| --- | --- |
| OS | Windows 10/11 (this project’s primary launcher path) |
| Python | **3.11–3.13** supported by docs; this workspace verified **3.12.10** |
| Network | Needed on first install for `pip` packages |
| Editor (optional) | VS Code/Cursor with workspace folder open and **Allow** automatic tasks |

---

## 2. Project root discovery

Confirm you are in the folder that contains **all** of:

- `TalentBridgeAI.code-workspace` (or this folder opened as workspace)
- `backend\legacy-django\manage.py`
- `frontend\`
- `database\`
- `tools\windows_manager.py`
- `.env.example`

**Actual audited root:** `E:\Job POrtal\TalentBridgeAI`

Django project directory: `backend\legacy-django`  
Settings module: `config.settings`

---

## 3. Environment setup (safe)

1. Copy `.env.example` → `.env` **only if `.env` does not already exist**.  
   Do **not** overwrite an existing private `.env`.
2. Ensure `DJANGO_SECRET_KEY` is set (installer/launcher can generate one into `.env` without printing it).
3. Recommended local keys (names only):
   - `DB_ENGINE=sqlite`
   - `DB_NAME=TalentBridgeAI`
   - `DJANGO_DEBUG=true` **and** for non-launcher shells also `DJANGO_ENV=development` (settings require both for DEBUG)
   - `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,[::1]`
4. Optional Google OAuth: set **both** `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET`, then restart.

---

## 4. Dependency installation

Canonical file: `backend\legacy-django\requirements.txt`

```text
# From project root (PowerShell)
py -3 -m venv backend\legacy-django\.venv
.\backend\legacy-django\.venv\Scripts\python.exe -m pip install -r backend\legacy-django\requirements.txt
```

Or let the lifecycle manager install on first `start` / `install`.

---

## 5. Database preparation

- Default engine: **SQLite** at `database\TalentBridgeAI.sqlite3`
- Launcher / `windows_manager` applies pending migrations on start
- Manual (from `backend\legacy-django` with venv active):

```text
python manage.py migrate
```

Do **not** delete the SQLite file to “fix” unless you intentionally accept data loss.  
Do **not** run `seed_demo_data` unless you explicitly want sample rows.

---

## 6. Exact development startup commands

### Preferred (VS Code / Cursor)

1. Open the TalentBridgeAI folder.
2. Allow automatic tasks if prompted.
3. Task runs `.vscode\start-talentbridge.ps1` → `tools\windows_manager.py start`.

### Manual (project root)

```text
py -3 tools\windows_manager.py start
```

Wrappers also exist: `scripts\startup\START_TALENTBRIDGEAI.bat` / root batch wrappers.

### Stop safely

```text
py -3 tools\windows_manager.py stop
```

Or press **Ctrl+C** in the managed task terminal. Prefer manager `stop` over killing random PIDs.

### Restart after `.env` changes

```text
py -3 tools\windows_manager.py restart
```

(or `RESTART_TALENTBRIDGEAI.bat`)

---

## 7. Ports and URLs

| Item | Behavior |
| --- | --- |
| Canonical URLs | `http://127.0.0.1:8000/` and `http://127.0.0.1:8001/` |
| Manager | Keeps a bridge so both ports work; one is the live Django port |
| Port file | `.talentbridge_django.port` records the live port |
| Day 10 smoke | Routes verified via `http://127.0.0.1:8000/` → HTTP 200 |

**Verify success:**

1. Homepage returns 200.  
2. `/login/`, `/jobs/`, `/signup/` return 200.  
3. `/dashboard/` redirects to login when anonymous.  
4. Optional: `http://127.0.0.1:8000/__dev__/` status dashboard (DEBUG/development only).

Do **not** open raw `frontend\pages\*.html` via `file://` or Live Server for auth/DB workflows.

---

## 8. Common startup errors (safe troubleshooting)

| Symptom | Likely cause | Safe action |
| --- | --- | --- |
| “Python not found” | PATH / py launcher missing | Install Python 3.12+; retry |
| Import / package errors | venv incomplete | Re-run pip install from requirements |
| DisallowedHost | Host not in `DJANGO_ALLOWED_HOSTS` | Use 127.0.0.1/localhost or update env |
| Port in use | Another Django or bridge | `windows_manager status` then `restart`; do not kill unrelated apps |
| Google button unavailable | OAuth env incomplete | Set both OAuth vars or use email/password |
| DEBUG False in CLI but True in browser | Launcher forces `DJANGO_ENV=development` + debug | Expected; see Day 4/9 |

Check logs: `logs\setup.log`, `logs\server.log` when present.

---

## 9. Day 10 verification note

On 2026-11-18 the managed lifecycle task was **already running**. Day 10 **did not** stop it to force a cold start. Smoke checks against `http://127.0.0.1:8000/` succeeded for core public routes. A cold start should follow the commands above on a machine without a live managed process.

---

## 10. What this guide is not

- Not a production deployment runbook.  
- Not permission to enable DEBUG on the public Internet.  
- Not Day 13 “rewrite all docs/settings” implementation — documentation only for Phase 1 gate.
