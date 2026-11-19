# TalentBridgeAI — Day 11 Root-File Dependency Map

**Date:** 2026-11-19  
**Project root:** `E:\Job POrtal\TalentBridgeAI`  
**Scope:** Root-level files/folders only (plus how they connect into Django/frontend)  
**Method:** Live inspection of settings, URLconf, scripts, tools, README, junctions — **no file moves**

Evidence anchors:

- `backend/legacy-django/config/settings.py` (`PROJECT_ROOT`, `FRONTEND_ROOT`, `TEMPLATES`, `STATICFILES_DIRS`, `MEDIA_ROOT`, SQLite path)
- `backend/legacy-django/config/urls.py` (`FRONTEND_ROOT`, `PAGES` map)
- `tools/windows_manager.py`, `tools/build_static.py`
- Root junctions (`css`, `js`, `images`, `pages`, `legacy-django`)
- `README.md`, `netlify.toml`, `.vscode/tasks.json`, `scripts/**`

---

## Risk legend

| Label | Meaning |
|-------|---------|
| **KEEP IN ROOT** | Belongs at repo root by convention or runtime contract |
| **HIGH** | Core runtime / many references; relocate only with careful plan |
| **MEDIUM** | Multiple references; needs coordinated updates + tests |
| **LOW** | Limited references; safer candidate for later move |
| **UNKNOWN** | Insufficient evidence in this session |

---

## Root inventory + dependency table

| Root File / Folder | Current Purpose | Referenced By | Reference Type | Relocation Risk | Required Updates | Recommendation |
|--------------------|-----------------|---------------|----------------|-----------------|------------------|----------------|
| `.env` | Local secrets & env (Django, OAuth, DB) | `settings.py` `load_dotenv(PROJECT_ROOT / ".env")`; install/OAuth scripts | Filesystem path at repo root | **KEEP IN ROOT** | N/A (must stay discoverable at `PROJECT_ROOT`) | **Keep in root.** Never commit. |
| `.env.example` | Non-secret env template | README; `CONNECT_GOOGLE_OAUTH.ps1`; root detection in settings | Docs + installer | **KEEP IN ROOT** | If moved: update README + scripts + `_resolve_repo_root` heuristics | **Keep in root.** |
| `.gitignore` | Ignore rules | Future Git; already lists `.env`, sqlite, media, backups | Git | **KEEP IN ROOT** | Review before first commit | **Keep in root.** |
| `.gitattributes` | Line-ending / attribute rules | Git (when present) | Git | **KEEP IN ROOT** | None today | **Keep in root.** |
| `README.md` | Primary project docs | Humans; setup entry | Docs links to `docs/`, scripts | **KEEP IN ROOT** | Path updates if layout changes | **Keep in root.** |
| `netlify.toml` | Netlify build → `tools/build_static.py`, publish `site` | Netlify CI | Build config paths | **KEEP IN ROOT** | Update `command`/`publish` if tools/site move | **Keep in root.** |
| `TalentBridgeAI.code-workspace` | VS Code/Cursor multi-root workspace | Editor | Workspace paths | **KEEP IN ROOT** | Update folder paths if root children move | **Keep in root.** |
| `index.html` | Stub redirect to `:8000`/`:8001` | Users opening folder HTML; mentions `scripts/startup/...` | Hardcoded local URLs + script path text | **KEEP IN ROOT** / **LOW** | Update script path text if scripts move | **Keep in root** (convenience launcher). |
| `.talentbridge_django.pid` | Runtime PID of managed Django | Lifecycle manager | Runtime file | **KEEP IN ROOT** | Generated; already gitignored | **Keep generated at root**; do not relocate as source. |
| `.talentbridge_django.port` | Live Django port (observed `8000`) | Lifecycle manager | Runtime file | **KEEP IN ROOT** | Generated | Same as PID. |
| `.talentbridge_port_bridge.pid` | Port-bridge PID | Lifecycle manager | Runtime file | **KEEP IN ROOT** | Generated | Same as PID. |
| `.django_secret_key` | Optional secret fallback file | `settings.py` (`PROJECT_ROOT / '.django_secret_key'`) | Filesystem | **KEEP IN ROOT** | Must remain at `PROJECT_ROOT` if used | **Keep in root** (private). |
| `.vscode/` | Tasks, start script | Cursor/VS Code folderOpen task → `.vscode/start-talentbridge.ps1` | Editor automation | **KEEP IN ROOT** | Update task cwd/paths if scripts move | **Keep in root.** |
| `.github/` | GitHub Actions (static deploy) | GitHub Pages workflow | CI | **KEEP IN ROOT** | Update workflow paths if build layout changes | **Keep in root.** |
| `frontend/` | Canonical HTML/CSS/JS/assets | `settings.TEMPLATES`, `STATICFILES_DIRS`, `urls.PAGES`, `build_static.py`, homepage | Django templates + static dirs + build | **HIGH** | Moving requires settings, urls, build_static, many `/css` `/js` `/images` URL assumptions | **Do not move casually.** Organize *inside* `frontend/` if needed on Day 12+. |
| `backend/` | Contains `legacy-django` Django project | `windows_manager.py`, install BATs, manage.py path | Python package + scripts | **HIGH** | Nearly all ops scripts assume `backend\legacy-django\manage.py` | **Keep.** Internal tidy only with script updates. |
| `legacy-django/` *(junction)* | Compatibility junction → `backend/legacy-django` | Older docs/scripts; dual-layout support in settings/`windows_manager` | Windows junction | **HIGH** | Removing breaks dual-layout detection & legacy scripts | **Keep junction** until all refs use `backend/legacy-django`. |
| `css/` *(junction)* | → `frontend/css` | Static URL `/css/...` via Django static mapping + Live Server habits; some maintenance scripts use `js\`/`css\` at root | Junction + URL | **HIGH** | Must remain or recreate junction / change STATIC wiring + all asset URLs | **Keep junction** (compatibility). |
| `js/` *(junction)* | → `frontend/js` | Same as css; `FIX_STATIC_PREVIEW_BANNER.ps1` looks for `js\demo-forms.js` | Junction + scripts | **HIGH** | Same | **Keep junction.** |
| `images/` *(junction)* | → `frontend/assets/images` | Homepage `/images/...`; STATICFILES_DIRS images | Junction + URL | **HIGH** | Same | **Keep junction.** |
| `pages/` *(junction)* | → `frontend/pages` | Template DIRS; static build; some scripts scan `pages` | Junction | **HIGH** | Same | **Keep junction.** |
| `database/` | SQLite directory (`TalentBridgeAI.sqlite3`) | `settings.py` `PROJECT_ROOT / 'database'` | Django DB NAME path | **KEEP IN ROOT** / **HIGH** | If moved: change settings + all backup/install scripts | **Keep in root.** |
| `private_media/` | Uploads / MEDIA_ROOT | `settings.MEDIA_ROOT = PROJECT_ROOT / "private_media"` | Django media | **KEEP IN ROOT** / **HIGH** | Settings + backup scripts | **Keep in root.** |
| `docs/` | Documentation & audit reports | README links; Day 1–11 deliverables | Docs only | **LOW**–**MEDIUM** | Mostly self-contained; README links | May reorganize *inside* `docs/` freely; moving off-root needs README updates. |
| `scripts/` | Install/startup/backup/diagnostics BATs/PS1 | README; `index.html`; VS Code tasks; Windows startup | Relative paths to `backend\legacy-django` | **MEDIUM** | Many BATs expect CWD = project root | Keep folder at root; reorganize subfolders carefully. |
| `tools/` | `windows_manager.py`, `build_static.py`, audit helpers | Netlify; START bat; Day audits | `ROOT = parents[1]` | **HIGH** | Netlify + launcher hard-depend | **Keep at root.** |
| `tests/` | Extra test helpers README | Sparse (app tests live under `jobs/tests`) | Docs | **LOW** | Clarify vs Django app tests | Keep; optionally merge docs later. |
| `site/` | Generated static preview output | Netlify publish; Live Server; gitignore | Build output | **KEEP AS GENERATED** | Rebuild via `build_static.py` | Do not treat as source; safe to delete/rebuild. |
| `backups/` | Local structure/DB checkpoints | Day 5 DB backup; gitignored | Ops | **KEEP IN ROOT** | None for Day 12 moves | Keep; do not nest Day 12 work inside without care. |
| `logs/` | Runtime logs | Lifecycle manager | Runtime | **KEEP IN ROOT** | Generated | Keep. |
| `releases/` | Portable release artifacts | Release scripts | Ops | **KEEP IN ROOT** | None | Keep. |

---

## Critical dependency evidence (non-guess)

### A. Python / Django path resolution

```text
BASE_DIR = .../backend/legacy-django
PROJECT_ROOT = repo root (detected via database/ + .env.example|README)
FRONTEND_ROOT = PROJECT_ROOT / "frontend"
load_dotenv(PROJECT_ROOT / ".env")
SQLITE: PROJECT_ROOT / "database" / f"{DB_NAME}.sqlite3"
MEDIA_ROOT: PROJECT_ROOT / "private_media"
TEMPLATES DIRS: BASE_DIR/templates, FRONTEND_ROOT, FRONTEND_ROOT/pages
STATICFILES_DIRS: frontend/css, frontend/js, frontend/assets/images, BASE_DIR/static
```

**Verified** via `manage.py check` + runtime print of settings in Day 11 session.

### B. URL / template map

`config/urls.py` defines `FRONTEND_ROOT` and a large `PAGES` dict mapping route names → HTML filenames under `frontend/pages/`. Relocating `frontend/pages` without updating this map and template DIRS **breaks public pages**.

### C. Static asset URLs (homepage)

`frontend/index.html` references absolute paths such as:

- `/css/pages/tb-hero-visuals.css?...`
- `/js/core/tb-match-score.js?...`
- `/images/tb-match-*.jpg`

These rely on Django serving `STATICFILES_DIRS` roots as `/css`, `/js`, `/images` (and/or compatibility junctions). Changing folder names without URL/static config updates is **HIGH** risk for the new orbit animation.

### D. Scripts & tools

| Consumer | Expects |
|----------|---------|
| `tools/windows_manager.py` | `ROOT/backend/legacy-django` (fallback `ROOT/legacy-django`) |
| `scripts/install/*.bat` | `backend\legacy-django\manage.py` from project root CWD |
| `scripts/startup/START_TALENTBRIDGEAI.bat` | tools lifecycle from root |
| `.vscode/tasks.json` | `${workspaceFolder}\.vscode\start-talentbridge.ps1` |
| `tools/build_static.py` | `ROOT/frontend/{css,js,pages}` → `ROOT/site` |
| `netlify.toml` | `python tools/build_static.py`, publish `site` |

### E. Junctions

| Junction | Target |
|----------|--------|
| `css` | `frontend\css` |
| `js` | `frontend\js` |
| `images` | `frontend\assets\images` |
| `pages` | `frontend\pages` |
| `legacy-django` | `backend\legacy-django` |

Day 11 backup used `/XJ` so junctions were **not** duplicated; canonical trees were copied. Live junctions remain.

### F. Tests

Primary Django tests: `backend/legacy-django/jobs/tests*` (not under root `tests/`).  
Root `tests/` is ancillary (README). Day 10 baseline: 171 jobs tests, 169 pass / 2 fail — **unchanged by Day 11**.

### G. Unknowns

| Item | Why UNKNOWN |
|------|-------------|
| Any remote GitHub remote URL | No `.git`; cannot inspect remotes |
| Whether production deploy uses root junctions | Local Windows verified; Linux deploy may use `frontend/` only — confirm before removing junctions |
| Full inventory of every BAT under `scripts/` hardcoded absolute paths | Sampled high-traffic scripts; residual absolute paths may exist (e.g. old update scripts referencing other folders) |

---

## Homepage / animation assets (preserve)

These are **not** root files but are high-value uncommitted work captured in the Day 11 backup:

| Path | Role |
|------|------|
| `frontend/index.html` | Hero showcase + AI Matching Visuals |
| `frontend/js/core/tb-match-score.js` | Orbit state machine |
| `frontend/css/pages/tb-hero-visuals.css` | Orbit + visuals CSS |
| `frontend/css/pages/tb-homepage*.css` | Hero layout |

Relocation of parent `frontend/` without static/template updates would break them.

---

## Summary recommendations

1. **Must stay at root:** `.env*`, `.gitignore`, `README.md`, `netlify.toml`, workspace, `.vscode`, `.github`, `database/`, `private_media/`, `tools/`, runtime pid/port files.  
2. **Keep for compatibility:** junctions `css`, `js`, `images`, `pages`, `legacy-django`.  
3. **High caution:** `frontend/`, `backend/`, `scripts/`.  
4. **Safer Day 12 targets:** deepen organization *inside* existing `docs/`, `scripts/` subfolders, `frontend/` subfolders — avoid inventing a second parallel `templates/`/`static/` at root that duplicates Django’s already-wired paths unless settings are updated in the same change set.
