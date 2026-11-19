# TalentBridgeAI — Step 1 Verification

Date: 2026-11-18

## Checks performed

| Check | Result |
| --- | --- |
| Django `manage.py check` | **PASS** (0 issues) |
| `showmigrations jobs` | **PASS** — 0001–0014 all applied `[X]` |
| Live DB integrity after moves | **PASS** — users=2, superusers=1, companies=3, jobs=0, apps=0 (unchanged pattern) |
| Venv runnable at new path | **PASS** — Django 5.2.19 imports |
| `PROJECT_ROOT` resolution | **PASS** — resolves to repo root, not `backend/` |
| Startup via `tools/windows_manager.py` | **PASS** — port 8000 listening |
| HTTP `/` | **200** |
| HTTP `/login/` | **200** |
| HTTP `/pages/login.html` | **200** |
| HTTP admin login / signup routes | **200** (manager health) |
| Full `manage.py test jobs` | **169 tests, 3 failures** (see below) |

## ERR_CONNECTION_REFUSED diagnosis

`ERR_CONNECTION_REFUSED` on `/pages/login.html` means **no process accepted TCP on that host/port** — it is not caused by HTML file location.

After Step 1:

- With Django running on `http://127.0.0.1:8000`, `/pages/login.html` returns **200**.
- Valid login UX URL remains `http://127.0.0.1:8000/login/` (same view).
- Opening static Live Server / `file://` / stopped Django will still refuse or fail auth.

## Test failures (honest)

Ran: `python manage.py test jobs` → **FAILED (failures=3)** / 169 tests / ~345s.

1. `test_homepage_renders_supplied_candidate_and_office_assets` — expects `/images/avatar_rahul.svg` on homepage; current homepage no longer embeds that asset (prior UX work). **Not caused by folder moves** (asset file still exists on disk).
2. `test_employer_can_update_only_own_application` — expects text `Notification center` in history response.
3. `test_published_matching_job_creates_one_alert_and_notification` — matched_fields list assertion mismatch (`[['title']]` vs `[['skills', 'work mode']]`).

These are deferred to **Step 2** stabilization (fix/expectation alignment), not treated as incomplete file moves.

## Step 1 completion decision

**Step 1 organization is verified for runtime:** structure relocated, references updated, DB preserved, server starts, critical URLs return 200.

Proceeding to Step 2 to stabilize backend tests and document database integrity.
