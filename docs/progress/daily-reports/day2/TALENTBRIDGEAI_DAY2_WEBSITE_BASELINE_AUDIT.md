# TalentBridgeAI — Day 2 Website Baseline Audit

**Date:** 2026-11-18  
**Status:** COMPLETED  
**Project root:** `E:\Job POrtal\TalentBridgeAI`  
**Basis:** Day 1 audit `docs/audit/day1/TALENTBRIDGEAI_DAY1_ENVIRONMENT_AUDIT.md` (COMPLETED; no Day 1 blockers that prevent this audit)

---

## Part A — Resume notes

| Item | Finding |
| --- | --- |
| Day 1 | Completed; Python 3.12.10, Django 5.2.19, SQLite OK |
| CSS/JS organizer | Hardened dry-run; prior no-op log + later dry-run log under `backups/` |
| Git | No `.git` in workspace; no branch workflow available |
| Incomplete ops | None blocking; server already healthy |
| Changes preserved | No redesign, no DB changes, no restarts performed for this audit |

---

## 1. Startup and server

| Item | Verified value |
| --- | --- |
| Startup (documented) | `scripts/startup/START_TALENTBRIDGEAI.bat` → `tools/windows_manager.py start` · VS Code `.vscode/start-talentbridge.ps1` |
| Venv | `backend\legacy-django\.venv\Scripts\python.exe` |
| Server already running | **Yes** — left running (not restarted) |
| Actual port | **8001** (`.talentbridge_django.port`) |
| Website URL | **http://127.0.0.1:8001/** |
| `windows_manager status` | LISTENING; health routes 200 |
| Django `manage.py check` | **0 issues** |
| `__dev__/state/` | `server.status=ok`, `frontend.status=ok` |
| Database | SQLite connected; **0 Job rows**, **3 Company**, **1 Profile**, **0 Application** (counts only; no data modified) |

---

## 2. Screenshots

Saved under `docs/reports/day2_screenshots/`:

- Homepage capture (hero/nav)
- Login page capture (`login.png` / timestamped PNGs)

---

## 3. Page inspection matrix

Statuses used only after HTTP and/or browser verification.

| # | Page | Actual URL(s) | Status | Notes |
| --- | --- | --- | --- | --- |
| 1 | Homepage | `/` | **WORKING** | Renders hero, nav, CTAs; 15 CSS + 8 JS; 0 broken images in browser check |
| 2 | Login | `/login/`, `/pages/login.html` | **WORKING** | Email/password form + Google button + CSRF present |
| 3 | Candidate signup | `/signup/job-seeker/`, `/pages/jobseeker-signup.html` | **WORKING** | HTTP 200 |
| 4 | Employer signup | `/signup/employer/`, `/pages/company-signup.html` | **WORKING** | HTTP 200 |
| 5 | Signup role chooser | `/signup/`, `/pages/signup-role.html` | **WORKING** | HTTP 200 |
| 6 | Jobs listing | `/jobs/` | **PARTIALLY WORKING** | Search UI + **demo/sample** listings when DB has 0 jobs; not live DB jobs |
| 7 | Job details (DB) | `/jobs/<id>/` e.g. `/jobs/1/` | **NOT FOUND** | 404 — no Job rows in DB |
| 8 | Job details (static/demo) | `/job-detail/`, `/pages/job-detail.html` | **WORKING** | Static page route 200; demo apply uses relative `application-form.html?...` |
| 9 | Job search page | `/job-search/`, `/pages/job-search.html` | **WORKING** | HTTP 200 |
| 10 | Candidate dashboard | `/dashboard/`, `/pages/dashboard/jdashboard.html` | **PARTIALLY WORKING** | Redirects to `/login/` when anonymous (expected auth gate); **authenticated UI NOT VERIFIED** (no test login performed) |
| 11 | Candidate profile | `/profile/`, `/edit-profile/` | **PARTIALLY WORKING** | Auth redirect to login; authenticated state NOT VERIFIED |
| 12 | Resume builder / management | `/resume-builder/`, `/resume-management/`, `/pages/resume-builder.html` | **PARTIALLY WORKING** | Static HTML 200; Django resume-builder redirects to login; upload/download NOT VERIFIED |
| 13 | Employer dashboard | `/pages/dashboard/cdashboard.html`, `/pages/dashboard/dindex.html` | **PARTIALLY WORKING** | Auth redirect; authenticated UI NOT VERIFIED |
| 14 | Job posting | `/jobs/create/`, `/pages/posting-job.html`, `/posting-job/` | **PARTIALLY WORKING** | Static posting page 200; create_job requires login |
| 15 | Application management | `/manage-applications/`, `/applied-jobs/` | **PARTIALLY WORKING** | Auth redirect; no applications in DB |
| 16 | Django admin login | `/admin/login/` | **WORKING** | HTTP 200 (credentials not used) |
| 17 | Django admin dashboard | `/admin/` | **PARTIALLY WORKING** | Redirects to login when anonymous; authenticated admin **NOT VERIFIED** |
| 18 | Companies directory | `/companies/` | **PARTIALLY WORKING** | HTTP 200 but very small body (~2KB); appears empty/minimal despite 3 Company rows |
| 19 | Pricing | `/pricing/`, `/pages/pricing.html` | **WORKING** | HTTP 200 |
| 20 | Employer marketing | `/pages/employer.html`, `/employer/` | **WORKING** | HTTP 200 |
| 21 | Job seeker marketing | `/pages/jobseaker.html`, `/jobseaker/` | **WORKING** | HTTP 200 |
| 22 | Remote / startup jobs | `/remote-jobs/`, `/startup-jobs/` | **WORKING** | HTTP 200 (likely same demo/list patterns) |
| 23 | Password reset | `/forgot-password/`, `/password-reset/` | **WORKING** | HTTP 200 |
| 24 | Dev preview | `/__dev__/`, `/__dev__/state/` | **WORKING** | Development only |
| 25 | FAQ | `/faq/` | **WORKING** | 200 |
| 26 | FAQ alias | `/faqs/` | **NOT FOUND** | 404 (footer/directory may link wrong slug) |
| 27 | Trust / status short aliases | `/trust/`, `/status/`, `/ai-audit/`, `/cookies/` | **NOT FOUND** | 404; correct slugs are `/trust-center/`, `/platform-status/`, `/ai-audit-center/`, `/cookie-preferences/` |
| 28 | Search alias | `/search/` | **NOT FOUND** | 404; use `/job-search/` or `/jobs/` |
| 29 | Applications alias | `/applications/` | **NOT FOUND** | 404; related routes are `/applied-jobs/` etc. |
| 30 | Logout | `/logout/` | **PARTIALLY WORKING** | GET → 405; POST without CSRF → 403 (expected CSRF); full logout flow NOT VERIFIED |
| 31 | Categories / about / contact / help / blog / careers / privacy / terms | various `/{slug}/` | **WORKING** | HTTP 200 where listed in `PAGES` |
| 32 | Page directory panel links | many `/js/pages/...` hrefs on homepage | **BROKEN** | Browser DOM showed directory links incorrectly prefixed with `/js/pages/` instead of `/pages/` |

---

## 4. Frontend asset status

| Asset class | Sample URL | Result |
| --- | --- | --- |
| CSS | `/css/base/style.css`, `/css/pages/tb-homepage.css` | **200** |
| JS | `/js/core/script.js` | **200** |
| Images | `/images/talentbridge-mark.svg`, `/images/tb-hero-candidate.jpg` | **200** |
| Homepage images | browser check | **0 broken** (`imgCount=13`) |
| Collectstatic | prior logs | Duplicate basename warnings from root junctions + `frontend/` (non-blocking for Django `dev_static` serving) |

---

## 5. Workflow inspection (safe / anonymous)

| Workflow | Result |
| --- | --- |
| Browse homepage → Jobs / Pricing / Sign in | Links present; pages load |
| Login form render | WORKING (no credential test) |
| Registration forms render | WORKING (no account creation) |
| Job search controls on `/jobs/` | WORKING UI; results are demo when DB empty |
| Job apply (live DB) | NOT VERIFIED / blocked by no Job rows + auth |
| Candidate/employer dashboards | Auth wall only verified |
| Admin access | Login page only; no credential use |
| Logout | Method/CSRF behavior noted; not fully exercised |

---

## 6. Backend / browser / link errors

1. **Empty Job table** — live `/jobs/<id>/` 404; listing falls back to demo content.  
2. **Companies directory thin/empty rendering** despite 3 companies in DB — needs future investigation.  
3. **Broken page-directory hrefs** (`/js/pages/...`) — navigation defect.  
4. **Slug mismatches:** `/faqs/`, `/trust/`, `/status/`, `/search/`, `/applications/`, `/cookies/` → 404.  
5. **Auth-gated pages** redirect to login — correct, but authenticated UX unverified.  
6. Homepage stats showed **0** open jobs in earlier sessions (consistent with DB).  

No 500s observed on inspected routes. Django system check clean.

---

## 7. Issues requiring future fixes (priority)

| Priority | Issue |
| --- | --- |
| P0 | Fix page-directory base/href generation (`/js/pages/` → `/pages/`) |
| P0 | Clarify demo vs live jobs; seed or document empty-DB demo mode |
| P1 | Companies directory empty/minimal rendering with existing Company rows |
| P1 | Add redirects for common alias 404s (`/faqs/`→`/faq/`, trust/status/cookies aliases) |
| P2 | Authenticated workflow audit with disposable test accounts (Day 4+) |
| P2 | Resolve collectstatic duplicate warnings from junctions |
| P3 | Git init/remote for change tracking |

---

## 8. Counts summary

| Metric | Count |
| --- | --- |
| Pages/routes inspected (HTTP and/or browser) | **50+** distinct URLs |
| WORKING | ~28 |
| PARTIALLY WORKING | ~14 |
| BROKEN | 1 class (page-directory links) + related wrong hrefs |
| NOT FOUND | 7+ alias routes |
| NOT VERIFIED | Authenticated dashboards, real apply, admin after login, email/OAuth |

**Day 2 status: COMPLETED**
