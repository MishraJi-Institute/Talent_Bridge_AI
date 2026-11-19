# TalentBridgeAI — Day 1 Environment Audit

**Date:** 2026-11-18  
**Status:** COMPLETED  
**Auditor:** Existing Cursor development agent (resumed session)  
**Roadmap:** 120-Day TalentBridgeAI Development Roadmap — Day 1 only  
**Re-verified:** 2026-11-18 (second pass after CSS/JS script review; Day 1 not assumed complete from that script)

---

## 1. Actual project root

| Item | Value |
| --- | --- |
| Confirmed workspace root | `E:\Job POrtal\TalentBridgeAI` |
| Workspace indicator | `TalentBridgeAI.code-workspace` present |
| Django project directory | `E:\Job POrtal\TalentBridgeAI\backend\legacy-django` |
| `manage.py` | `E:\Job POrtal\TalentBridgeAI\backend\legacy-django\manage.py` |
| Settings module | `config.settings` |
| Settings file | `backend\legacy-django\config\settings.py` |
| `PROJECT_ROOT` (runtime) | `E:\Job POrtal\TalentBridgeAI` |
| `FRONTEND_ROOT` (runtime) | `E:\Job POrtal\TalentBridgeAI\frontend` |
| `BASE_DIR` (runtime) | `E:\Job POrtal\TalentBridgeAI\backend\legacy-django` |

Root was identified from the open Cursor workspace path and verified by presence of `manage.py`, `config/settings.py`, `frontend/`, `database/`, and `.env` (present; contents not inspected for secrets).

---

## 2. Overview of current project structure

Hybrid Django + static HTML layout (post file-organization finish pass):

| Path | Role |
| --- | --- |
| `frontend/` | Canonical HTML/CSS/JS/assets (`index.html`, `pages/`, `css/`, `js/`, `assets/images/`) |
| `backend/legacy-django/` | Django app (`jobs`), `config/`, `.venv/`, `requirements.txt` |
| `database/` | SQLite database file |
| `private_media/` | Uploaded / private media (preserved) |
| `docs/` | Architecture, setup, reports, troubleshooting |
| `scripts/` | Install, startup, shutdown, backup, diagnostics |
| `tools/` | `windows_manager.py`, `build_static.py`, helpers |
| `backups/` | Structure and Day 1 checkpoints |
| `site/` | Static preview build output |
| Root junctions | `css`, `js`, `images`, `pages`, `legacy-django` → frontend/backend paths (compat) |

Primary Django installed apps (runtime): `django.contrib.*`, `allauth` (+ Google social), `jobs`.

---

## 3. Previous work status (resumed first)

| Item | Detail |
| --- | --- |
| Prior task | File organization finish + homepage display restore + jobs test triage |
| Interrupted item | Full `jobs` suite had 1 remaining failure after fingerprint path update; homepage CSS restore was mid-verification |
| Action taken for Day 1 | **No further redesign.** Existing uncommitted/local edits preserved. Inventory checkpoint created. Server left running. |
| Previous work status | **SAFELY CHECKPOINTED** (homepage CSS / intro / `dev_preview.py` changes kept as-is) |

Checkpoint (hash inventory only; no `.env`, DB, or media copied):

`backups/day1_checkpoint_20261118_084445/CHECKPOINT_INVENTORY.txt`

Related earlier structure backup: `backups/structure_finish_20261118_081801/`  
Related report: `docs/reports/TALENTBRIDGEAI_FILE_MOVE_LOG_FINISH.md`

---

## 4. Python and Django versions

| Component | Verified value |
| --- | --- |
| Python | **3.12.10** (MSC v.1943, 64-bit) |
| Interpreter | `backend\legacy-django\.venv\Scripts\python.exe` |
| Django | **5.2.19** |

Versions were read from the project venv. No upgrades were performed.

---

## 5. Virtual environment status

| Item | Status |
| --- | --- |
| Location | `E:\Job POrtal\TalentBridgeAI\backend\legacy-django\.venv` |
| Exists | Yes |
| Usable | Yes (`python -c` / `manage.py` / `pip freeze` succeeded) |

---

## 6. Dependencies and requirements files

| File | Notes |
| --- | --- |
| `backend/legacy-django/requirements.txt` | Canonical (also mirrored via `legacy-django` junction) |
| Declared pins (file) | `Django>=5.2,<5.3`, `django-allauth[socialaccount]`, `python-dotenv`, `Pillow`, `PyMySQL` |
| Installed package count | **19** (`pip freeze`) |

Installed packages (names/versions only; no credentials):

- Django==5.2.19  
- django-allauth==65.22.1  
- python-dotenv==1.2.4  
- pillow==12.3.0  
- PyMySQL==1.2.4  
- reportlab==5.1.0  
- requests==2.34.2  
- plus supporting libs: asgiref, certifi, cffi, charset-normalizer, cryptography, idna, oauthlib, pycparser, PyJWT, sqlparse, tzdata, urllib3  

No dependency upgrades were performed.

---

## 7. Django settings module and startup

| Item | Value |
| --- | --- |
| Settings module | `config.settings` |
| Documented startup | `scripts/startup/START_TALENTBRIDGEAI.bat` → `tools/windows_manager.py` |
| VS Code | `.vscode/start-talentbridge.ps1` / folder-open task |
| Manager CLI | `python tools/windows_manager.py {install,start,stop,restart,status,repair,update,open}` |
| Docs | `docs/setup/README_RUN_DJANGO.md`, root `README.md` |

**Note:** Docs often mention port **8000**; this machine’s managed server is currently on **8001**.

---

## 8. Database type and connection status

| Item | Verified value |
| --- | --- |
| Engine | `django.db.backends.sqlite3` |
| Database file | `E:\Job POrtal\TalentBridgeAI\database\TalentBridgeAI.sqlite3` |
| Connection | **OK** (`connection.ensure_connection()`) |
| Vendor | sqlite |
| Migrations (sampled) | Applied markers present for `jobs`, `auth`, `admin`, `sessions`, `sites`, `account`, `socialaccount` |

No flush/reset/drop operations were run. Database contents were not modified. Credentials are not applicable for local SQLite.

`.env` is present at project root (existence only verified). Secrets were not read into this report.

---

## 9. Server status and port

| Item | Verified value |
| --- | --- |
| Managed port file | `.talentbridge_django.port` → **8001** |
| Managed PID file | `.talentbridge_django.pid` → **15268** |
| `windows_manager status` | Port 8001 LISTENING; managed PID 15268 |
| Homepage | `http://127.0.0.1:8001/` → **HTTP 200** |
| Health (manager) | `/`, `login/`, `admin/login/`, signup routes, admin static CSS → **200** |
| Spot checks | `/jobs/` 200, `/login/` 200, `/__dev__/` 200 |
| Action | Server **left running** (not restarted for Day 1) |

---

## 10. Git branch and working-tree status

| Item | Status |
| --- | --- |
| `.git` directory | **Not present** (`DOT_GIT=False`) |
| Git CLI on PATH / common install paths | **Unavailable** during audit |
| Branch / latest commit | **N/A — not a Git working tree in this folder** |
| Safe branch creation | Skipped (would not apply without Git) |

### Backup / checkpoint approach used instead

1. Existing structure backups under `backups/` (including `structure_finish_20261118_081801`).  
2. New Day 1 inventory checkpoint: `backups/day1_checkpoint_20261118_084445/`.  
3. No deletion of `.env`, database, migrations, media, or source.  
4. All local edits from the prior session were left in place.

---

## 11. Django system-check results

Command executed:

```text
backend\legacy-django\.venv\Scripts\python.exe manage.py check
```

Result: **System check identified no issues (0 silenced).**

---

## 12. Errors and unresolved issues

1. **No Git repository / Git CLI unavailable** — version control and branch workflow blocked until Git is installed and/or the project is initialized/cloned with a remote.  
2. **Docs vs runtime port mismatch** — documentation frequently cites `8000`; live managed server is `8001`.  
3. **Prior interrupted test debt (not fixed in Day 1):**  
   - `jobs.test_dev_preview.LivePreviewTests.test_state_uses_request_origin_and_port` was made to pass earlier.  
   - `jobs.test_dev_preview.LivePreviewTests.test_source_fingerprints_skip_environment_and_collected_static_directories` still **FAIL** (`counts['scripts']` 26 != 1) after `source_fingerprints` was pointed at `FRONTEND_ROOT`. Needs a focused Day 2+ test/path fix — not a redesign.  
4. **Static file name collision warning** (observed in VS Code start task logs): duplicate `jobseaker.js` collection path — non-blocking warning.  
5. **Shell `DEBUG` probe returned `False`** when settings were loaded from a non-launcher shell; the managed Windows launcher is documented to set `DJANGO_DEBUG=true` for its process. Treat launcher-managed status as authoritative for the live server.  
6. Homepage visual CSS edits from the prior session remain uncommitted local changes; Day 1 did not continue redesign work.

---

## 13. Day 2 prerequisites and recommended next steps

Day 2 should stay within roadmap “safe baseline → inventory features,” not large redesign:

1. Install or locate Git; optionally initialize/connect remote **only with owner approval**.  
2. Produce a feature inventory of public Naukri-comparable capabilities already present vs missing (auth, jobs list/detail/apply, employer flows, resume, search/filters).  
3. Fix the remaining `source_fingerprints` unit test without changing product UX.  
4. Align startup docs with the actual managed port behavior (8000 vs 8001).  
5. Keep the running server; use `windows_manager status` before any restart.  
6. Do **not** reset DB, rewrite migrations, or overwrite `.env`.

**Await explicit approval before starting Day 2.**

---

## 14. Day 1 completion checklist

| Requirement | Result |
| --- | --- |
| Correct project root identified | Yes |
| Previous work / changes preserved | Yes |
| Backup/checkpoint documented | Yes (`day1_checkpoint_20261118_084445`) |
| Python / Django / env verified | Yes |
| Startup commands identified | Yes |
| Django checks executed | Yes — pass |
| Day 1 audit report created | Yes (this file) |
| Remaining issues + Day 2 steps documented | Yes |

**Day 1 status: COMPLETED**

---

## 15. Re-verification addendum (same day, post script review)

Commands re-run and confirmed:

| Check | Result |
| --- | --- |
| Python / Django | 3.12.10 / 5.2.19 |
| `manage.py check` | 0 issues |
| SQLite connect | OK (`database/TalentBridgeAI.sqlite3`) |
| Server | `windows_manager status` → port **8001** LISTENING; homepage/login/signup health **200** |
| Git | Still **no** `.git`; Git CLI still unavailable |
| Checkpoint | `backups/day1_checkpoint_20261118_084445` still present |
| Venv / requirements / `.env` presence | Present (secrets not read) |

**Related but separate:** CSS/JS organizer review documented in `docs/reports/TALENTBRIDGEAI_CSS_JS_ORGANIZE_SCRIPT_REVIEW.md` — verdict **NEEDS FIXES**. That review does **not** replace or invalidate this Day 1 environment audit.

**Noted non-blocking issue:** root `index.html` is **0 bytes**; live homepage is served from `frontend/index.html` (HTTP 200). Fix root stub in a later maintenance task — not required to mark Day 1 complete.
