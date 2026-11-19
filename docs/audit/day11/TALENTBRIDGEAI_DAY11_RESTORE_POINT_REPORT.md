# TalentBridgeAI — Day 11 Restore Point Report

**Date:** 2026-11-19  
**Roadmap day:** 11 (Safe restore point + root-file dependency mapping)  
**Status:** COMPLETE (with documented Git limitation)  
**Constraint honored:** No project files moved, renamed, or reorganized.

---

## 1. Actual project root

| Field | Value |
|-------|--------|
| Detected root | `E:\Job POrtal\TalentBridgeAI` |
| Detection basis | Presence of `database/`, `frontend/`, `backend/legacy-django/manage.py`, `.env.example`, `README.md` |
| Django BASE_DIR | `E:\Job POrtal\TalentBridgeAI\backend\legacy-django` |
| `settings.PROJECT_ROOT` | `E:\Job POrtal\TalentBridgeAI` |
| `FRONTEND_ROOT` | `E:\Job POrtal\TalentBridgeAI\frontend` |

---

## 2. Git repository status

| Check | Result |
|-------|--------|
| `.git` directory present | **No** |
| `git` executable on PATH | **Not found** |
| Common install paths checked | `C:\Program Files\Git\...`, LocalAppData Git — **not installed** |
| Current branch | N/A |
| Suggested branch `backup/day11-pre-organization` | **Could not create** (no Git) |
| Checkpoint commit hash | **None** |

### Implication

A Git branch/commit restore point was **not** possible in this environment. Day 11 restore capability is provided by the **independent filesystem backup** below.

**Recommended before Day 12 (user action, not done today):** install Git for Windows, `git init` (or clone remote if one exists), add a proper `.gitignore` review, and create branch `backup/day11-pre-organization` from this verified tree. Do not force-push or rewrite history.

---

## 3. Working-tree / prior work preservation

Uncommitted homepage and animation work remains in the live tree and was copied into the backup, including:

- `frontend/index.html` (candidate orbit markup, AI Matching Visuals)
- `frontend/js/core/tb-match-score.js` (orbit → approach → zoom state machine)
- `frontend/css/pages/tb-hero-visuals.css` (orbit + visuals layout)
- Related homepage CSS (`tb-homepage*.css`, layout-lock, coherence)
- Day 1–10 audit docs under `docs/audit/`
- Phase 1 gate docs under `docs/audit/phase1/`

No `git reset`, `git clean`, or destructive cleanup was run.

---

## 4. Active processes at checkpoint

| Process | Observation |
|---------|-------------|
| Managed Django launcher | Active VS Code/Cursor task: `start-talentbridge.ps1` |
| Django PID | `17324` (from `.talentbridge_django.pid`) |
| Live port | **8000** (from `.talentbridge_django.port`) |
| Port bridge | `:8001` → `:8000` (documented by launcher) |
| Homepage smoke | `GET http://127.0.0.1:8000/` → **200** |
| Agent file moves | None for Day 11; only documentation + external backup |

Server was **not** stopped for Day 11.

---

## 5. Independent backup restore point

| Field | Value |
|-------|--------|
| Location | `E:\Job POrtal\TalentBridgeAI_Day11_PreOrganization_Backup_2026-11-19_08-38-38` |
| Relation to project | **Sibling folder** under `E:\Job POrtal\` (outside project root) |
| Method | `robocopy /E /COPY:DAT /XJ` |
| Robocopy exit | `3` (success: files copied; extras/log present) |
| Approx size | **33.94 MB** |
| Manifest | `DAY11_BACKUP_MANIFEST.md` inside the backup folder |

### Included

- Source: `frontend/`, `backend/legacy-django/` (no venv), `docs/`, `scripts/`, `tools/`, `tests/`
- Data: `database/TalentBridgeAI.sqlite3`, `private_media/`
- Config: `.env`, `.env.example`, `.gitignore`, workspace/Netlify/README
- Editor/CI: `.vscode/`, `.github/`

### Excluded (and why)

| Exclusion | Reason |
|-----------|--------|
| `.venv` / `venv` | Recreatable; large; path-bound |
| `site/`, `staticfiles/` | Generated artifacts |
| `releases/`, nested `backups/`, `logs/` | Avoid recursive/heavy non-source copies; Day 5 DB backup already exists separately under project `backups/` |
| Root junctions (`css`, `js`, `images`, `pages`, `legacy-django`) | `/XJ` — canonical content already under `frontend/` / `backend/` |
| `__pycache__`, `*.pyc`, `*.log` | Transient |

### Sensitive files

- `.env` **was copied** into the local backup for restore fidelity.
- Secrets are **not** printed in this report.
- Treat the backup folder as private; do not upload to public remotes.

---

## 6. Backup verification

| Verification | Result |
|--------------|--------|
| Backup folder exists | Yes |
| `manage.py` present | Yes |
| Homepage + orbit JS/CSS present | Yes |
| SHA256 `tb-match-score.js` live == backup | **Match** `4C9A8986…75194B` |
| SHA256 `tb-hero-visuals.css` live == backup | **Match** `AEA9B019…5853F9` |
| SQLite size live == backup | **405504 == 405504** |
| Live junctions intact after copy | Yes |
| Original project unchanged by restore test | Yes (no restore-over-live performed) |
| Django `manage.py check` | **0 issues** |

---

## 7. Database

| Item | Value |
|------|--------|
| Engine (active) | SQLite |
| Path | `database/TalentBridgeAI.sqlite3` |
| Modified by Day 11? | **No** |
| Migrations run? | **No** |
| Flush/reset? | **No** |

---

## 8. Limitations (honest)

1. **No Git checkpoint** — Git not installed; no `.git` directory.
2. Backup excludes generated `site/` and nested historical `backups/` (recover those from existing `E:\Job POrtal\TalentBridgeAI\backups\` if needed).
3. Virtualenv not backed up — reinstall via existing installer/lifecycle scripts after restore.
4. Day 11 markdown deliverables were written **after** the backup snapshot; copy them into the backup folder if a single archive must include them (optional post-step).

---

## 9. Safe next step

Do **not** start Day 12 until explicit user approval.  
When approved: follow `TALENTBRIDGEAI_DAY12_PROPOSED_FOLDER_STRUCTURE.md` and prefer installing Git first so each move group can be committed.
