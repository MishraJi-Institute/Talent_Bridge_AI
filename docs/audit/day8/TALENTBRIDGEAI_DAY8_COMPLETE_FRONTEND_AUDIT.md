# TalentBridgeAI — Day 8 Complete Frontend Audit

**Date:** 2026-11-18  
**Roadmap day:** Day 8 only  
**Status:** PARTIALLY COMPLETE  
**Constraint honored:** Audit and documentation only. No redesign, no CSS/JS rewrites, no route/model/auth changes, no package installs, no speculative app fixes.

**Machine artifacts:**
- `docs/reports/_day8_frontend_scan.json`
- `docs/reports/_day8_relative_hrefs.json`
- `docs/reports/_day8_http_asset_probe.json`
- `docs/reports/day8_screenshots/`

**Prior roadmap inputs used:** Day 2 baseline, Day 3 structure inventory, Day 6 URL map (verified against live `config/urls.py` and runtime).

---

## 1. Project root and frontend architecture overview

| Item | Value |
| --- | --- |
| Project root | `E:\Job POrtal\TalentBridgeAI` |
| Django project | `backend\legacy-django` |
| Settings | `config.settings` |
| URLconf | `backend\legacy-django\config\urls.py` |
| Frontend root | `frontend\` (`FRONTEND_ROOT`) |
| Public HTML | `frontend\index.html` + `frontend\pages\**\*.html` |
| CSS | `frontend\css\` (served at `/css/…`) |
| JS | `frontend\js\` (served at `/js/…`) |
| Images | `frontend\assets\images\` (served at `/images/…`) |
| Runtime instance | `http://127.0.0.1:8000` (existing managed launcher; not restarted for this audit) |

**Rendering model (verified):**
- Explicit FBVs (home, jobs, login, etc.) plus `PAGES` slug → `page_view` / `page_file`.
- Most HTML responses pass through `_render_page()` which injects `<base href="/pages/">` (unless a `<base>` already exists) and a premium stylesheet.
- Homepage `home()` uses `django_render` **without** `_render_page` base injection; homepage nav mostly uses absolute `/pages/…` and named routes.
- Client script `frontend/js/core/site-experience.js` rewrites many relative `*.html` hrefs to slug paths (e.g. `about.html` → `/about/`).

**Safety checkpoint before audit:** Existing managed server on port 8000 was in use. No parallel agent was actively rewriting the same templates during the audit window; prior CSS/JS organize terminals had already succeeded. Uncommitted app work was not discarded. No production data changes. Form POSTs that would create records or send email were not executed.

---

## 2. Pages discovered and inspected

### 2.1 Discovery counts

| Source | Count | Notes |
| --- | ---: | --- |
| HTML files under `frontend/` (excl. unslop) | **77** | Static scan |
| `PAGES` slug entries | **50** | `config/urls.py` |
| Explicit public/app routes HTTP-probed | **23+** | See scan + probes |
| Pages with runtime browser visit | **8** | `/`, `/login/`, `/jobs/`, `/contact/`, `/about/`, `/signup/` (prior), `/pricing/` (HTTP), mobile variants |
| Auth-gated destinations | Many | Redirect to `/login/?next=…` without test credentials |

### 2.2 Representative page inventory (discovered)

| Page name | URL | Template / view target | CSS / JS (primary) | Opens? | Audit status |
| --- | --- | --- | --- | --- | --- |
| Homepage | `/` | `frontend/index.html` via `home` | `/css/pages/tb-homepage*.css`, `/js/core/*` | Yes 200 | ISSUE FOUND (stats empty vs demo jobs) |
| Sign in | `/login/` | `pages/login.html` | auth page CSS/JS | Yes 200 | PARTIALLY VERIFIED (structure OK; submit not POSTed) |
| Sign up role | `/signup/` | `signup-role.html` | page CSS | Yes 200 | PARTIALLY VERIFIED |
| Job seeker signup | `/signup/job-seeker/` | view + template | — | Yes 200 | PARTIALLY VERIFIED (HTTP) |
| Employer signup | `/signup/employer/` | view + template | — | Yes 200 | PARTIALLY VERIFIED (HTTP) |
| Jobs list | `/jobs/` | `jobs/home.html` via `job_list` | jobs search CSS | Yes 200 | ISSUE FOUND (demo vs homepage counts) |
| Job search alias | `/job-search/`, `/search/` | redirects / same listing | — | Yes 200 | PARTIALLY VERIFIED |
| Remote / startup jobs | `/remote-jobs/`, `/startup-jobs/` | `job_list` variants | — | Yes 200 | PARTIALLY VERIFIED (HTTP) |
| Companies | `/companies/` | `companies/list.html` | — | Yes 200 | PARTIALLY VERIFIED |
| Contact | `/contact/` | `contact.html` | tb foundation | Yes 200 | PARTIALLY VERIFIED (form not POSTed) |
| About | `/about/` | `about.html` | — | Yes 200 | PASS (public content) |
| Pricing | `/pricing/` | `pricing.html` | — | Yes 200 | PARTIALLY VERIFIED |
| Employer marketing | `/employer/` | `employer.html` | large page CSS | Yes 200 | PARTIALLY VERIFIED |
| Job seeker marketing | `/jobseaker/` | `jobseaker.html` | has own `<base>` | Yes 200 | PARTIALLY VERIFIED |
| FAQ / Help / Trust / etc. | `/faq/`, `/help/`, … | matching `PAGES` | — | Yes 200 | PARTIALLY VERIFIED |
| Forgot password | `/forgot-password/` | `forgot-password.html` | — | Yes 200 | PARTIALLY VERIFIED |
| Post a job | `/posting-job/` | `posting-job.html` | — | Yes 200 | PARTIALLY VERIFIED (public GET; submit not tested) |
| Job detail (DB) | `/jobs/<id>/` | `job_detail` | — | No live DB job id in this env | NOT TESTED (no non-demo approved job) |
| Job detail page slug | `/job-detail/` | `job-detail.html` | — | Yes 200 | PARTIALLY VERIFIED |
| Application form | `/application-form/` | redirects to `/jobs/` when no job | — | Redirect | ISSUE FOUND (action `#` when no job in template) |
| Profile / edit / resume / saved / applied / notifications / interviews / dashboards / admin | matching slugs | page templates | — | Redirect → login | PARTIALLY VERIFIED (auth gate only) |
| Access denied | `/access-denied/` | `access_denied_view` | — | 403 | PASS (permission state) |
| 404 page | `/404/` | `404.html` | — | Yes 200 | PARTIALLY VERIFIED |
| Page directory “Site error page” | labeled as error → `/404/` | `site-experience.js` | — | Yes | ISSUE FOUND (mislabel) |
| Dashboards under `/pages/dashboard/…` | e.g. `jdashboard.html` | page_file | dashboard CSS/JS | Redirect → login | NOT TESTED (authenticated UI) |

---

## 3. Page-by-page audit matrix

Legend: **PASS** / **ISSUE FOUND** / **PARTIALLY VERIFIED** / **NOT TESTED** / **NOT APPLICABLE**

| Page | URL | Template | Links | Forms | Responsive | Console | Network | Missing States | Overall Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Homepage | `/` | `frontend/index.html` | PASS | N/A | PARTIALLY VERIFIED (desktop + 390) | PASS* | PASS | ISSUE FOUND | ISSUE FOUND |
| Login | `/login/` | `pages/login.html` | PASS | PARTIALLY VERIFIED | PARTIALLY VERIFIED (390) | PASS* | PASS | PARTIALLY VERIFIED | PARTIALLY VERIFIED |
| Signup role | `/signup/` | `signup-role.html` | PASS | N/A | NOT TESTED | NOT TESTED | PASS | NOT TESTED | PARTIALLY VERIFIED |
| Jobs | `/jobs/` | `jobs/home.html` | PASS | PASS (GET `/jobs/`) | PARTIALLY VERIFIED (390) | PASS* | PASS | ISSUE FOUND (demo empty DB) | ISSUE FOUND |
| Contact | `/contact/` | `contact.html` | PASS† | PARTIALLY VERIFIED | NOT TESTED (mobile) | NOT TESTED | PASS | PARTIALLY VERIFIED | PARTIALLY VERIFIED |
| About | `/about/` | `about.html` | PASS | N/A | NOT TESTED | NOT TESTED | PASS | N/A | PASS |
| Pricing | `/pricing/` | `pricing.html` | PASS | N/A | NOT TESTED | NOT TESTED | PASS | NOT TESTED | PARTIALLY VERIFIED |
| Employer | `/employer/` | `employer.html` | PASS† | N/A | NOT TESTED | NOT TESTED | PASS | NOT TESTED | PARTIALLY VERIFIED |
| Job seeker | `/jobseaker/` | `jobseaker.html` | PASS† | PARTIALLY VERIFIED | NOT TESTED | NOT TESTED | PASS | NOT TESTED | PARTIALLY VERIFIED |
| Companies | `/companies/` | companies list | PASS | N/A | NOT TESTED | NOT TESTED | PASS | PARTIALLY VERIFIED | PARTIALLY VERIFIED |
| FAQ | `/faq/` | `faq.html` | PASS | N/A | NOT TESTED | NOT TESTED | PASS | N/A | PARTIALLY VERIFIED |
| Forgot password | `/forgot-password/` | `forgot-password.html` | PASS | PARTIALLY VERIFIED | NOT TESTED | NOT TESTED | PASS | NOT TESTED | PARTIALLY VERIFIED |
| Posting job | `/posting-job/` | `posting-job.html` | PARTIALLY VERIFIED | PARTIALLY VERIFIED | NOT TESTED | NOT TESTED | PASS | NOT TESTED | PARTIALLY VERIFIED |
| Auth-gated candidate/employer pages | `/profile/`, `/saved-jobs/`, `/dashboard/`, … | various | PASS (redirect) | NOT TESTED | NOT TESTED | NOT TESTED | PASS (login HTML) | PASS (login required) | PARTIALLY VERIFIED |
| Job seeker dashboard | `/pages/dashboard/jdashboard.html` | `jdashboard.html` | ISSUE FOUND (`#` placeholders) | NOT TESTED | NOT TESTED | NOT TESTED | PASS (redirect) | NOT TESTED | ISSUE FOUND |
| Access denied | `/access-denied/` | `access-denied.html` | N/A | N/A | NOT TESTED | NOT TESTED | 403 expected | PASS | PASS |
| 404 demo page | `/404/` | `404.html` | PARTIALLY VERIFIED | N/A | NOT TESTED | NOT TESTED | PASS | N/A | PARTIALLY VERIFIED |

\*Console: no failed resources / no captured JS exceptions on pages where CDP resource check ran (`/`, `/login/`, `/jobs/`). Full DevTools console stream was not persisted for every route.  
†Relative `*.html` in source are rewritten at runtime (`<base href="/pages/">` + `site-experience.js`). Direct nested paths like `/contact/about.html` 404 if requested literally.

---

## 4. Broken links findings

### D8-L01 — Residual relative `*.html` hrefs in templates (runtime mitigated)
- **Priority:** MEDIUM (maintenance / no-JS edge); not a primary nav outage when Django `_render_page` + JS run  
- **Pages:** 29 templates with same-directory relative `*.html` and no author `<base>` (e.g. `contact.html`, `employer.html`, `job-listings.html`, …)  
- **Evidence:** `docs/reports/_day8_relative_hrefs.json`; runtime contact nav hrefs resolve to `/about/`, `/help/`, etc. after JS; `_render_page` injects `<base href="/pages/">`  
- **Also observed:** Requesting `/contact/about.html` literally returns Django DEBUG 404 — screenshot `day8_contact_relative_link_404.png`  
- **Expected:** Prefer `{% url %}` / absolute slugs in source so links do not depend on base/JS  
- **Actual:** Source still uses static-site relative paths; runtime compensates  
- **Recommended correction:** Replace relative page hrefs with named URL tags or root-absolute slugs (implementation approval required)  
- **Approval needed:** Yes  

### D8-L02 — Job seeker dashboard profile outbound links are placeholders
- **Priority:** LOW  
- **Page:** Job seeker dashboard  
- **File:** `frontend/pages/dashboard/jdashboard.html`  
- **Links:** “Portfolio ↗”, “LinkedIn ↗”, “GitHub ↗”, “Resume ↗” → `href="#"`  
- **Evidence:** static scan `hash_or_placeholder_links` (4)  
- **Expected:** Real profile URLs or hidden until set  
- **Actual:** Dead hash links  
- **Recommended correction:** Bind to profile fields or omit until populated  
- **Approval needed:** Yes  

### D8-L03 — Page directory “Site error page” points at `/404/`
- **Priority:** LOW  
- **File:** `frontend/js/core/site-experience.js` (~line 131)  
- **Expected:** Dedicated 500/error preview if labeled “Site error page”  
- **Actual:** Same destination as “Page not found” (`/404/`)  
- **Approval needed:** Yes  

### D8-L04 — Auth-gated links correctly redirect (not broken)
- Dashboard, profile, saved jobs, admin dashboard, etc. return login with `next=` — **PASS** for anonymous users.

### False positives cleared
- Static `has_csrf: False` on many forms: templates use `{% csrf_token %}` (login/contact verified).  
- Probe “broken `/pages/`” matched `<base href="/pages/">`, not a user link.  
- Naive urljoin without honoring `<base>` overstated contact/employer 404s.

---

## 5. Forms audit findings

**Forms inventoried (static):** 59 form tags across frontend pages (`_day8_frontend_scan.json`).

| Form | Action | Method | CSRF in template | Runtime note |
| --- | --- | --- | --- | --- |
| Login | `/login/` | POST | Yes | Password `type=password`; Google social POST present; **submit not executed** |
| Contact | `{% url 'contact_submit' %}` → `/contact/submit/` | POST | Yes | Required fields present; page states email delivery not configured; **submit not executed** |
| Forgot password | `{% url 'forgot-password' %}` | POST | Yes | **not executed** |
| Jobs search (live `/jobs/`) | `/jobs/` | GET | N/A | OK |
| Static `job-listings.html` search | `job-listings.html` (relative) | GET | N/A | Live listing uses `jobs/home.html` instead |
| Resume upload | multipart + accept filters | POST | Yes | **not executed** (would write media) |
| Application form | `{% url 'apply_job' job.id %}` or `#` | POST | Yes | **D8-F01** when no job |
| Signup / posting / manage-* | named urls | POST | `{% csrf_token %}` present in sources checked | **not executed** |

### D8-F01 — Application form action becomes `#` without a job
- **Priority:** MEDIUM  
- **File:** `frontend/pages/application-form.html`  
- **Evidence:** `action="{% if job %}{% url 'apply_job' job.id %}{% else %}#{% endif %}"`; `/application-form/` redirects to `/jobs/` in this environment  
- **Expected:** Clear empty/error state; no dead submit  
- **Actual:** Template allows `#` fallback for demo/no-job path  
- **Approval needed:** Yes  

### D8-F02 — Form submit UX states not runtime-verified
- **Priority:** MEDIUM (coverage gap)  
- Login/contact/signup/posting: loading/disabled/duplicate-submit and server error rendering were **source-inspected only** (no POST).  
- Contact page copy already discloses email is not sent — honesty PASS for expectations.

### Security-related frontend observations (Day 8 only; Day 9 not started)
- Password fields use `type="password"` on login.  
- CSRF tokens present on POSTs inspected.  
- Resume accept attribute lists PDF/DOC/DOCX.  
- DEBUG 404 page exposes URLconf patterns — **future Day 9 observation**, not remediated here.

---

## 6. Responsive design findings

**Viewports tested with evidence:**
- Desktop ~default browser width (homepage screenshot; CDP ~921× height varies)  
- Mobile emulation **390×844** (homepage, jobs, login)

**Viewports not fully exercised:** 1440×900, 1280×800, 1024×768, 768×1024, 375×812, 360×800 (listed as gaps).

| ID | Priority | Viewport | Page | Finding |
| --- | --- | --- | --- | --- |
| D8-R01 | LOW | 390×844 | Login | Header still shows large Sign In / Sign Up row above the form (crowded first screen); hamburger present (“Open navigation”). No horizontal overflow (`scrollWidth === clientWidth`). |
| D8-R02 | — | 390×844 | Home, Jobs | No horizontal overflow; hamburger nav present. Jobs search stacks fields vertically (usable). |

Screenshots: `day8_homepage_mobile_390.png`, `day8_jobs_mobile_390.png`, `day8_homepage_desktop.png`.

---

## 7. Browser console errors

| Page | Result |
| --- | --- |
| `/`, `/login/`, `/jobs/` | No `performance` resources with status ≥400; no captured `Runtime` exceptions via CDP spot checks |
| Other pages | **NOT TESTED** with console listeners |

No CRITICAL/HIGH console defects documented from runtime evidence. Informational messages were not treated as errors.

---

## 8. Network errors

| Request | Status | Initiating context | Impact | Reproducible |
| --- | ---: | --- | --- | --- |
| `/contact/about.html` (literal) | 404 | Manual/path probe (ignores `<base>`) | Only if a client builds nested URLs | Yes |
| `/job-listings/` | 404 | Direct probe | Slug is `/jobs/`, not `/job-listings/` | Yes |
| `/jobs/1/` | 404 | Direct probe | No matching approved job id in DB for this env | Yes |
| `/css/base/site.css`, `/js/pages/home.js` | 404 | Auditor path guesses | **Not referenced** by homepage (homepage uses `/css/base/style.css`, `/js/core/…`) | N/A |
| Homepage CSS/JS listed in `index.html` | 200 | `/` | None | Yes |
| Auth pages | 200 body of login | `/dashboard/` etc. | Expected redirect behavior | Yes |

Homepage asset sample from link check: **0 broken** internals on `/`.

---

## 9. Missing UI states

| ID | Priority | Page/component | Expected | Current | Impact | Recommended |
| --- | --- | --- | --- | --- | --- | --- |
| D8-S01 | MEDIUM | Homepage stats | Reflect discoverable opportunities or explain demo | Shows **0** open jobs / companies / seekers while `/jobs/` shows DEBUG demo roles | Users may think the board is empty | Align counts with demo mode or label “live approved only” |
| D8-S02 | LOW | Login / contact submit | Loading / disabled during POST | Not verified at runtime | Unknown double-submit risk | Add/verify busy state after approval |
| D8-S03 | — | Saved jobs template | Empty state | Present in `saved-jobs.html` (`backend-empty`) | — | Source OK; runtime needs login |
| D8-S04 | — | Access denied | Permission state | `/access-denied/` → 403 | Clear | Keep |
| D8-S05 | MEDIUM | Application without job | Explicit empty/error | `#` action / redirect to jobs | Confusing apply entry | Dedicated empty state |
| D8-S06 | LOW | jdashboard social links | Disabled or real URLs | `href="#"` | Dead clicks when authenticated | Bind or hide |

---

## 10. Visual and usability inconsistencies (evidence-based only)

| ID | Priority | Finding |
| --- | --- | --- |
| D8-U01 | MEDIUM | Homepage live totals are zero while jobs page advertises sample/demo roles in DEBUG — inconsistent empty vs demo messaging |
| D8-U02 | LOW | Login mobile stacks auth CTAs and form (dense); functional but heavy above-the-fold |
| D8-U03 | LOW | Mixed URL styles in nav (`/pages/*.html` on homepage vs slug routes elsewhere) — works, but inconsistent for maintenance |

No redesign recommendations beyond documenting these.

---

## 11. Screenshots / evidence references

Directory: `docs/reports/day8_screenshots/`

| File | What it shows |
| --- | --- |
| `day8_homepage_desktop.png` | Homepage desktop; stats at **0**; page directory control |
| `day8_homepage_mobile_390.png` | Homepage mobile 390; hamburger; no overflow |
| `day8_jobs_mobile_390.png` | Jobs mobile search stack |
| `day8_contact_desktop.png` | Contact form desktop |
| `day8_contact_relative_link_404.png` | Django DEBUG 404 for literal `/contact/about.html` |

JSON evidence: `_day8_frontend_scan.json`, `_day8_relative_hrefs.json`, `_day8_http_asset_probe.json`.

---

## 12. Prioritized issue backlog

| ID | Priority | Summary | Approval needed |
| --- | --- | --- | --- |
| D8-S01 / D8-U01 | MEDIUM | Homepage zero counts vs DEBUG demo jobs | Yes |
| D8-F01 / D8-S05 | MEDIUM | Application form `#` / weak no-job state | Yes |
| D8-L01 | MEDIUM | Relative HTML hrefs depend on base/JS | Yes |
| D8-F02 | MEDIUM | Form submit UX not runtime-verified | Yes (testing + any fix) |
| D8-L02 / D8-S06 | LOW | jdashboard `#` links | Yes |
| D8-L03 | LOW | “Site error page” → `/404/` | Yes |
| D8-R01 / D8-U02 | LOW | Login mobile density | Yes |
| D8-U03 | LOW | Mixed `/pages/` vs slug link style | Yes |

**Counts:** CRITICAL **0** · HIGH **0** · MEDIUM **4** · LOW **4**  
(Coverage gaps recorded separately; not inflated to CRITICAL.)

---

## 13. Recommended corrections (no implementation this day)

1. Replace residual relative `*.html` navigation with `{% url %}` / absolute slugs.  
2. When DEBUG demo jobs are shown on `/jobs/`, mirror messaging or counts on the homepage (or explicitly label live vs sample).  
3. Remove or gate `href="#"` dashboard outbound links.  
4. Harden application entry when `job` is missing (no `#` submit).  
5. Fix page-directory label/target for a real error page if one exists.  
6. After approval: authenticated pass for dashboards + full viewport matrix + safe form validation tests in a disposable DB.

---

## 14. Runtime verification limitations

- No candidate/employer test login used → authenticated dashboards, resume upload, apply, post-job, manage-apps **not** runtime-verified.  
- Form POSTs intentionally skipped (no email, no new applications/jobs).  
- Not every discovered HTML file received a browser session.  
- Full official viewport list not completed.  
- Console checked via CDP resource/error spot checks, not a continuous Console panel export for all routes.  
- `Job.objects` empty of approved non-demo jobs in the probe environment → live `/jobs/<id>/` detail not exercised.

---

## 15. Commands and tools actually used

- Read-only / audit helpers: `tools/_day8_frontend_static_scan.py`, `tools/_day8_relative_href_scan.py`, `tools/_day8_http_asset_probe.py`, `tools/_day8_check_base.py`, `tools/_day8_jobs_html_snip.py`  
- Python `urllib` HTTP probes against `http://127.0.0.1:8000`  
- Cursor IDE Browser MCP: navigate, snapshot, screenshot, CDP `Runtime.evaluate`, device metrics (mobile), unlock  
- Source inspection: `config/urls.py`, `jobs/views.py` (`_render_page`, `home`, `job_list`), key templates, `site-experience.js`  
- Prior docs: Day 2, 3, 6 reports  

**Not used:** package installs, DB writes, server kill/restart for preference, production credentials.

---

## 16. Day 8 completion status

**PARTIALLY COMPLETE**

Required audit categories were covered with a mix of static analysis and runtime checks on the live local app. Findings are evidenced. Authenticated workflows, full viewport matrix, and unsafe form POSTs remain open for a later approved pass.

**Day 9 (security/dependency audit) was not started.**

---

## Progress note (short)

Inspected 77 HTML files and 50 `PAGES` slugs; HTTP-probed core public routes; browser-tested home/login/jobs/contact/about with mobile 390 evidence. Documented relative-link mitigation via `_render_page` + JS; homepage zero-stats vs demo jobs; placeholder dashboard links; application `#` fallback; console/network clean on sampled public pages. Screenshots saved under `docs/reports/day8_screenshots/`. No application source modified for fixes. Waiting for approval before Day 9.
