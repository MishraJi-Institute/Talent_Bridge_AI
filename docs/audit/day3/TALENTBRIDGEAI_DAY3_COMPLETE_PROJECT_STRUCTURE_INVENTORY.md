# TalentBridgeAI — Day 3 Complete Project Structure Inventory

**Date:** 2026-11-18  
**Status:** COMPLETED  
**Constraint honored:** No files moved, renamed, deleted, or reorganized during this audit.

**Project root:** `E:\Job POrtal\TalentBridgeAI`

Supporting lists (generated this day, non-secret):

- `docs/reports/_day3_html_pages_list.txt` (63 HTML under `frontend/pages`)
- `docs/reports/_day3_css_list.txt` (43 CSS)
- `docs/reports/_day3_js_list.txt` (26 JS)

---

## 1. Actual project root and high-level tree

```text
TalentBridgeAI/
├── frontend/                 # Canonical HTML/CSS/JS/assets
├── backend/legacy-django/    # Django project + jobs app + .venv
├── database/                 # SQLite DB
├── private_media/            # Uploads (empty at audit time)
├── docs/                     # Documentation & reports
├── scripts/                  # Install/startup/shutdown/backup/diagnostics
├── tools/                    # windows_manager, organizers, build_static
├── backups/                  # Structure & audit checkpoints
├── site/                     # Static preview build output
├── tests/                    # Extra test helpers
├── css/, js/, images/, pages/, legacy-django/   # Windows junctions → frontend/backend
├── .vscode/, .github/
├── .env, .env.example        # secrets present; contents not inventoried
├── netlify.toml, README.md, TalentBridgeAI.code-workspace
└── index.html                # Root stub redirecting to Django URL
```

### File counts (approximate, verified)

| Scope | Files | Dirs |
| --- | --- | --- |
| `frontend/` | 162 | 26 |
| `backend/legacy-django/` (excl. `.venv` / `staticfiles`) | 130 | 29 |
| `docs/` | 107 | 12 |
| `scripts/` | 37 | 6 |
| `tools/` | 18 | 1 |
| `backups/` | 60 | 24 |
| `site/` (generated preview) | 146 | 12 |
| Project total excl. `.venv`, `staticfiles`, `site`, `backups` | **~487** | — |

### By extension (excl. `.venv` / `staticfiles` / `site` / `backups`)

| Ext | Count | Ext | Count |
| --- | ---: | --- | ---: |
| `.md` | 82 | `.html` | 80 |
| `.py` | 66 | `.css` | 49 |
| `.bat` | 31 | `.js` | 27 |
| `.png/.jpg/.svg` | 39 | `.ps1` | 8 |
| `.sqlite3` | 1 | `.log` | 2 |

---

## 2. Django applications and purpose

| App | Purpose |
| --- | --- |
| `jobs` | Core portal: users/profiles, companies, jobs, applications, resumes, alerts, interviews, notifications, auth views, page serving |
| `django.contrib.admin` | Admin site |
| `django.contrib.auth` | Users/permissions |
| `django.contrib.sites` | Sites framework (allauth) |
| `allauth` / `account` / `socialaccount` (+ Google) | Email/social authentication |
| `config` | Project settings, root URLconf, WSGI/ASGI |

**Settings module:** `config.settings`  
**manage.py:** `backend/legacy-django/manage.py`

---

## 3. Python inventory (`jobs` + `config`)

### `backend/legacy-django/jobs/`

| File | Role |
| --- | --- |
| `models.py` | Domain models (see §5) |
| `views.py` | Primary HTTP views / page orchestration (~97KB) |
| `forms.py` | ResumeBuilderForm, JobAlertPreferenceForm, social signup form |
| `admin.py` | Model admin registrations |
| `adapters.py` | allauth adapters |
| `backends.py` | Custom auth backend(s) |
| `google_oauth.py` | Google OAuth helpers |
| `middleware.py` | Request/middleware helpers |
| `dev_preview.py` / `dev_preview_views.py` | Live preview fingerprints + dashboard |
| `tests.py` + `test_*.py` | Large automated suite |
| `migrations/0001`–`0014` | Schema history |

### `backend/legacy-django/config/`

`settings.py`, `urls.py`, `wsgi.py`, `asgi.py`, `settings.py.backup_*`

### Other tools Python

`tools/windows_manager.py`, `build_static.py`, `_organize_frontend_assets.py`, `_organize_root_finish.py`, `_organize_step1.py`, `bootstrap_env.py`, diagnostics/package helpers.

---

## 4. Models, forms, URLs

### Models (`jobs.models`)

Company, Job, Profile, SignupRecord, ResumeDraft, Application, ApplicationStatusEvent, ContactInquiry, SavedJob, Notification, JobAlertPreference, JobAlert, Interview.

### Forms

ResumeBuilderForm, JobAlertPreferenceForm, TalentBridgeSocialSignupForm.

### URL configuration

Single root URLconf: `config/urls.py`

- Explicit Django routes: home, jobs CRUD/apply, dashboards, auth, resume endpoints, admin-dashboard, notifications, interviews, etc.
- `PAGES` dict → `/{slug}/` via `views.page_view`
- Catch-alls: `/pages/<path>`, `/css/<path>`, `/js/<path>`, `/images/<path>`
- `admin/`, `accounts/` (allauth), `__dev__/`

No separate `jobs/urls.py`.

---

## 5. HTML / template inventory

| Location | Count | Notes |
| --- | ---: | --- |
| `frontend/pages/**/*.html` | 63 | Primary UI templates (see list file) |
| `frontend/index.html` | 1 | Homepage |
| `backend/.../jobs/templates/` | 6 | Django-side templates |
| `backend/.../templates/` | 8 | Admin/social/dev_preview/etc. |
| Root `index.html` | 1 | Stub redirect to :8001 |

Key page files include login, signup variants, job-listings, job-detail, dashboards (`jdashboard`, `cdashboard`, `dindex`), posting-job, resume-*, admin-dashboard, marketing pages.

---

## 6. CSS inventory

**Root:** `frontend/css/`

| Folder | Files | Status |
| --- | ---: | --- |
| `base/` | 6 | ACTIVELY REFERENCED |
| `components/` | 10 | ACTIVELY REFERENCED |
| `pages/` | 17 | ACTIVELY REFERENCED |
| `responsive/` | 2 | ACTIVELY REFERENCED |
| `dashboard/` | 8 | ACTIVELY REFERENCED (dashboard pages) |
| `layouts/` | 0 CSS (README only) | POSSIBLY UNUSED placeholder |

Full paths: `docs/reports/_day3_css_list.txt` (43).

---

## 7. JavaScript inventory

**Root:** `frontend/js/`

| Folder | Files | Status |
| --- | ---: | --- |
| `core/` | 10 | ACTIVELY REFERENCED |
| `authentication/` | 4 | ACTIVELY REFERENCED |
| `jobs/` | 5 | ACTIVELY REFERENCED |
| `dashboard/` | 7 | ACTIVELY REFERENCED |
| `components/` | README only | POSSIBLY UNUSED placeholder |
| `dashboards/` | README only | POSSIBLY UNUSED placeholder (note spelling vs `dashboard/`) |
| `notifications/` | README only | POSSIBLY UNUSED placeholder |

Full paths: `docs/reports/_day3_js_list.txt` (26).

---

## 8. Images and static assets

| Location | Count / notes |
| --- | --- |
| `frontend/assets/images/` | 19 files |
| `frontend/assets/icons|logos|videos/` | present |
| Root `images/` | Junction → `frontend/assets/images` |
| `backend/.../staticfiles/` | Collected static (generated; excluded from primary counts) |
| `private_media/` | **0 files** at audit |

---

## 9. Database and migrations

| Item | Value |
| --- | --- |
| Engine | SQLite |
| File | `database/TalentBridgeAI.sqlite3` |
| Migrations | `jobs` 0001–0014 (all applied per Day 1/2 checks) |
| Row counts (read-only) | Jobs **0**, Companies **3**, Profiles **1**, Applications **0** |
| SQL helper | `database/create_mysql_database.sql` (for optional MySQL) |

---

## 10. Scripts and configuration

| Area | Examples |
| --- | --- |
| Startup | `scripts/startup/START_TALENTBRIDGEAI.bat`, RESTART_*, OPEN_DJANGO_WEBSITE.bat |
| Shutdown | `scripts/shutdown/STOP_*`, DISABLE_* |
| Install | `scripts/install/*` |
| Backup | `scripts/backup/*` |
| Diagnostics | `scripts/diagnostics/*` |
| VS Code | `.vscode/tasks.json`, `start-talentbridge.ps1`, `launch.json` |
| Deploy | `netlify.toml`, `.github/workflows/static.yml` |
| Env | `.env` (present, not opened), `.env.example` |

Conflicting/overlapping startups: multiple BAT wrappers + `windows_manager` + VS Code folderOpen task — **POSSIBLE DUPLICATE** entrypoints (same manager underneath).

---

## 11. Documentation and tests

| Area | Notes |
| --- | --- |
| `docs/` | setup, architecture, reports, troubleshooting, Day1–Day3 audits |
| Tests | `jobs/tests.py`, `test_acceptance_flows.py`, `test_dev_preview.py`, `test_email_login_backend.py`, `test_new_quality_features.py`, `tools/test_windows_manager.py` |
| Duplicate docs | Multiple historical reports (BUG_FIX, FEATURE_VERIFICATION, PREMIUM_REDESIGN, etc.) — **POSSIBLE DUPLICATE** narrative overlap; keep as history |

---

## 12. Duplicate / unused findings

| Finding | Classification | Evidence |
| --- | --- | --- |
| Root junctions `css/js/images/pages` mirroring `frontend/` | **CONFIRMED DUPLICATE** paths (intentional compat) | Junction targets verified; causes collectstatic “another file with destination path” warnings |
| `legacy-django` junction → `backend/legacy-django` | **CONFIRMED DUPLICATE** path alias | Junction |
| `site/` static build vs live `frontend/` | **POSSIBLE DUPLICATE** deploy artifact | Generated preview; not runtime Django source of truth |
| `css/layouts`, `js/components`, `js/dashboards`, `js/notifications` | **POSSIBLY UNUSED** | README stubs only |
| `js/dashboards` vs `js/dashboard` | **POSSIBLE DUPLICATE** naming confusion | Empty plural folder |
| `jdashboard.css` + `jdashboard-redesign.css` | **NOT YET VERIFIED** which is primary | Both present |
| `tb-homepage*.css` variants (attract/elevate/premium/layout-lock) | **ACTIVELY REFERENCED** layered set | Homepage link tags |
| Page-directory hrefs `/js/pages/...` | Broken references (Day 2) | DOM inspection |
| No basename collisions inside `frontend/css` or `frontend/js` | Clean | Group-by name count |

**No deletions performed.**

---

## 13. Frontend-to-backend page mapping (important flows)

| Feature | Template / HTML | CSS | JS | Route | View | Models / auth |
| --- | --- | --- | --- | --- | --- | --- |
| Homepage | `frontend/index.html` | `css/base/*`, `pages/tb-homepage*.css`, `components/*`, `responsive-fixes` | `core/dark-mode`, `landing-intro`, `script`, `site-experience`, jerry-site | `/` | `views.home` | Job/Company counts; public |
| Login | `frontend/pages/login.html` (+ motion CSS) | `pages/login*.css`, header/dark-mode | `authentication/*`, `core/*` | `/login/`, `/pages/login.html` | `views.login_view` | User/Profile; anonymous |
| Job seeker signup | `jobseeker-signup.html` | `pages/jobseeker-signup.css` | signup + demo-forms | `/signup/job-seeker/` | `views.jobseeker_signup` | User, Profile, SignupRecord |
| Employer signup | `company-signup.html` | `pages/company-signup.css` | `authentication/company-signup.js` | `/signup/employer/` | `views.employer_signup` | User, Company, Profile |
| Jobs list | Django-rendered listing (portal CSS) + optional `job-listings.html` | `portal-pages`, listings CSS | search UI inline/page JS | `/jobs/` | `views.job_list` | Job, Company; public (+ demo fallback) |
| Job detail | DB: view template path; static: `job-detail.html` | portal/page CSS | — | `/jobs/<id>/`, `/job-detail/` | `views.job_detail` / `page_view` | Job; apply needs auth |
| Apply | `application-form.html` + `apply_job` | page CSS | — | `/jobs/<id>/apply/` | `views.apply_job` | Application; login required |
| Candidate dashboard | `pages/dashboard/jdashboard.html` | `dashboard/jdashboard*.css` | `dashboard/jdashboard.js`, `dashboard-guard.js` | `/dashboard/` → role redirect; `/pages/dashboard/jdashboard.html` | `dashboard_redirect` + page_file | Profile; login required |
| Employer dashboard | `cdashboard.html` / `dindex.html` | `cdashboard.css`, `dstyle.css` | `cdashboard.js`, `dscript.js` | dashboard pages | page_file + guards | Company; login + employer |
| Job posting | `posting-job.html` + `create_job` | `pages/posting-job.css` | `jobs/posting-job.js` | `/jobs/create/`, `/posting-job/` | `views.create_job` / page_view | Job; employer auth |
| Resume | `resume-builder.html`, `resume-management.html` | `resume-builder.css` | `jobs/resume-builder.js` | `/resume-builder/`, resume APIs | `resume_builder`, download/preview/delete | ResumeDraft, Profile; auth |
| Admin | Django admin templates + `admin-dashboard.html` | admin CSS | admin JS | `/admin/`, `/admin-dashboard/` | Django admin / `admin_dashboard` | staff/superuser |

Mappings verified via `config/urls.py`, `views.py` symbols, and live HTTP where noted in Day 2. Name similarity alone was not used as proof.

---

## 14. CSS/JS organization verification

| Check | Result |
| --- | --- |
| Expected CSS folders exist | Yes: base, components, layouts, pages, responsive (+ dashboard) |
| Expected JS folders exist | Yes: core, components, authentication, jobs, dashboard(s), notifications |
| Mapped files at destinations | Yes (Day 1/2 verification; dry-run targets 35 CSS / 19 JS) |
| Flat leftovers under `frontend/css|js` | None |
| Basename collisions in frontend trees | None |
| Live nested asset HTTP | 200 for sampled paths |
| Organizer script safety | Dry-run default; **no `--apply` during Day 2/3** |
| Remaining issues | Empty placeholder folders; junction-driven collectstatic duplicates; broken `/js/pages/` directory links (runtime href bug, not a missing file) |

---

## 15. Missing / unclear architecture areas

1. No Git repository in this workspace copy.  
2. Demo-job fallback vs empty Job table not documented in one place for operators.  
3. Companies directory rendering vs 3 DB companies unclear.  
4. Whether `site/` preview is still required in local workflow.  
5. Authenticated end-to-end paths not inventory-tested with real sessions.  
6. Optional MySQL path exists in docs/requirements but SQLite is active.

---

## 16. Recommended next development priorities

1. Repair page-directory link base (`/js/pages/` bug).  
2. Authenticated baseline pass (disposable test users) — natural Day 4 candidate.  
3. Companies list empty-state / query bug.  
4. Alias redirects for common 404 slugs.  
5. Introduce Git remote/backup discipline.  
6. Naukri-gap feature matrix using this inventory (after approval).

---

## Day 3 status: COMPLETED

| Metric | Value |
| --- | --- |
| Files inventoried (excl. venv/staticfiles/site/backups) | ~487 |
| Django apps | `jobs` + contrib/allauth stack |
| HTML pages (`frontend/pages`) | 63 |
| CSS files | 43 |
| JS files | 26 |
| Migrations | 14 (`jobs`) |
| CSS/JS organization | Present & serving; placeholders empty; no re-move |
| Frontend↔backend mapping | Documented for core flows |
| Report | `docs/audit/day3/TALENTBRIDGEAI_DAY3_COMPLETE_PROJECT_STRUCTURE_INVENTORY.md` |
