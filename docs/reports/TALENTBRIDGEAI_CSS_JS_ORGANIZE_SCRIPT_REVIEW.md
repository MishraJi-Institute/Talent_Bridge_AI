# CSS/JS Organization Script Review

**Script reviewed:** `tools/_organize_frontend_assets.py`  
**Date:** 2026-11-18  
**Execution log:** `backups/structure_resume_20261118_062859/css_js_move_log.json`  
**Review verdict:** **NEEDS FIXES** (initial review) → **FIXES APPLIED (dry-run ready)** on 2026-11-18  
Do **not** run `--apply` unless a dry-run log is reviewed and approved.

No file moves or reference rewrites were executed during this review.

---

## 1. Script identity and syntax

| Check | Result |
| --- | --- |
| File present | Yes |
| `py_compile` | **PASS** (exit 0) |
| Encoding | UTF-8 reads/writes; no BOM/malformed string literals found |
| Filenames in maps | Match current assets (including known typo `jobseaker.css` / `jobseaker.js`) |

---

## 2. Has the script already run?

**Yes.** Log exists and records this run:

| Action | Count |
| --- | --- |
| `mkdir` | 11 |
| `skip-missing` | 51 |
| `move` | **0** |
| `rewrite` | **0** |
| `skip-exists` | **0** |

`css_targets` and `js_targets` in the log are **empty `{}`**.

**Interpretation:** This script run was a **no-op**. Flat sources under `frontend/css/*.css` and `frontend/js/*.js` were already missing (files already lived in subfolders from earlier organization). Because targets stayed empty, the rewrite pass had nothing to rewrite.

Current tree state (verified separately): all **mapped** destinations exist under `frontend/css/{base,components,pages,responsive}/` and `frontend/js/{core,authentication,jobs}/` (33 CSS + 18 JS). Live HTML already uses nested paths. That organization was **not** accomplished by this logged run.

---

## 3. Destination verification (post-run tree)

| Check | Result |
| --- | --- |
| Mapped CSS destinations | **33/33 present** |
| Mapped JS destinations | **18/18 present** |
| Flat leftovers in `frontend/css` or `frontend/js` | **None** |
| Basename collisions inside `frontend/css` / `frontend/js` | **None** |
| HTTP resolve (sample nested assets on :8001) | **200** for style, site-header, tb-homepage, tb-layout-lock, responsive-fixes, script, landing-intro, login-10sec, posting-job |
| Live flat `/css/file.css` or `/js/file.js` refs in frontend + Django templates/jobs | **0 found** |

### Unmapped but present (script never moves these)

- CSS: `pages/tb-layout-lock.css`, `pages/tb-homepage-elevate.css`, entire `dashboard/**`
- JS: `core/tb-hero-network.js`, entire `dashboard/**`

These are fine if intentionally left out of `CSS_MAP` / `JS_MAP`, but the script docs/maps should list them explicitly.

---

## 4. Safety and correctness findings

### Critical / high

1. **No dry-run mode** — `main()` always moves/writes. Unsafe to re-run until a dry-run flag exists.  
2. **No backup / rollback** — no pre-move copy, no undo log of file contents, no restore helper.  
3. **Silent `skip-missing`** — treats missing sources as normal; empty target maps then skip all rewrites without failing the process.  
4. **Silent `skip-exists`** — if destination already exists, source is **left in place** and destination is assumed correct (no content hash compare). Can create duplicates on a partial tree.  
5. **Does not scan `frontend/index.html`** — roots list only `ROOT/index.html` and `frontend/pages/`. The live homepage is `frontend/index.html` (currently correct nested refs from other work, but this script would miss it).  
6. **Wrong `build_static.py` path** — scans `ROOT/build_static.py` (absent); real file is `tools/build_static.py`.  
7. **Does not scan Django Python modules** — `jobs/views.py`, `jobs/tests.py`, `jobs/dev_preview.py`, `config/urls.py` are outside rewrite roots (they currently already use nested paths from other edits).  
8. **No `{% static %}` rewriting** — e.g. `templates/admin/base_site.html` uses `{% static 'admin/css/login-motion.css' %}`; patterns only cover quoted `css/` / `js/` path prefixes.

### Medium

9. **Root `index.html` is 0 bytes** — not caused by this no-op log run, but dangerous if anything still points at root index; Django serves `FRONTEND_ROOT/index.html` (healthy).  
10. **Query-string / already-nested paths** — rewrite regexes are prefix-based (`css/` + filename). They do not match `/css/pages/foo.css`, which is good for idempotent nested paths, but also means the script cannot “fix” wrong nested folders.  
11. **CSS `@import` of local stylesheets** — not specially handled (current local CSS mostly imports Google Fonts / uses `/images/…`).  
12. **Does not scan** `site/`, `docs/`, `scripts/`, `tests/`, Netlify artifacts, root junctions’ duplicate trees beyond listed roots.  
13. **Collectstatic duplicate warnings** — root junctions + `frontend/` both contribute same basenames (observed earlier); script does not address `STATICFILES_DIRS` duplication.

### Low

14. Empty map folders (`layouts`, `components`, `dashboards`, `notifications`) only get README stubs — OK.  
15. Typo filenames (`jobseaker`) preserved — consistent with project, not a script bug.

---

## 5. Reference-rewriting pattern review

Implemented patterns (quoted only):

- `"/css/NAME"` or `"css/NAME"` → `"/css/folder/NAME"` / `"css/folder/NAME"`
- `"../css/NAME"` → `"../css/folder/NAME"`
- Same for `js/`

**Gaps:**

| Pattern type | Covered? |
| --- | --- |
| Absolute `/css/…` flat | Yes (if targets populated) |
| Relative `../css/…` flat | Yes |
| Unquoted URLs | No |
| `url(…)` in CSS to other CSS | No |
| `{% static '…' %}` | No |
| `frontend/index.html` | **Not scanned** |
| `tools/build_static.py` | **Wrong path** |
| Nested templates under `frontend/pages/**` | Yes (directory rglob) |
| Django `jobs/*.py` | No |

---

## 6. Required fixes before any re-run

1. Add `--dry-run` (default) and require `--apply` for writes.  
2. Backup tree (or copy-on-write inventory) before moves; write rollback manifest.  
3. Fail (non-zero exit) if required sources are missing unless `--allow-missing`.  
4. On `dst.exists()`, compare hashes; never leave ambiguous duplicates.  
5. Add scan roots: `frontend/index.html`, `tools/build_static.py`, `backend/legacy-django/jobs/**/*.py`, `config/**/*.py`.  
6. Document/unmapped files explicitly; decide whether `tb-layout-lock.css` etc. belong in `CSS_MAP`.  
7. Do **not** re-apply moves now — destinations already organized; re-run would mostly `skip-missing` / risk duplicate flats if any source reappears.

---

## 7. Recovery plan (if needed later)

- Prefer restore from `backups/structure_resume_20261118_062859/` / `structure_finish_20261118_081801/` after verifying hashes.  
- Do not delete destination trees without confirming `frontend/index.html` and page refs still resolve.  
- Live site currently healthy on nested paths; **no rollback recommended** unless a verified regression appears.

---

## Verdict

**A. CSS/JS organization script review (initial): NEEDS FIXES**  
**A. After hardening (2026-11-18 continue pass): PASS (safe dry-run default; no `--apply` executed)**

Hardening applied to `tools/_organize_frontend_assets.py`:
- Default **dry-run**; explicit `--apply` required for writes
- Timestamped hash inventory backup before `--apply`
- Hash compare on destination collisions (no blind overwrite)
- Scan roots include `frontend/index.html`, `tools/build_static.py`, Django `jobs/` + `config/`
- Maps include `tb-layout-lock.css`, `tb-homepage-elevate.css`, `tb-hero-network.js`
- Verified dry-run: `errors: 0`, 35 CSS + 19 JS targets already at destination

Do not run `--apply` unless a reviewed dry-run shows planned moves that are actually needed.
