# TalentBridgeAI — Day 9 Security and Dependency Audit

**Date:** 2026-11-18  
**Roadmap day:** Day 9 only  
**Status:** COMPLETE  
**Constraint honored:** Audit and documentation only. No secret rotation, no `.env` edits, no dependency upgrades, no auth/permission/upload rewrites, no Git history rewrite, no migrations, no destructive tests.

**Machine artifact:** `docs/reports/_day9_security_inventory.json`  
**Helper (read-only inventory):** `tools/_day9_security_inventory.py`

**Prior docs consulted (verified against current code):** Day 3 structure, Day 4 settings, Day 5 DB inventory, Day 6 URL map, Day 7 data dictionary, Day 8 frontend audit (DEBUG 404 note).

**Safety checkpoint:** Managed app on `http://127.0.0.1:8000` left running. No parallel agent was actively rewriting security-sensitive app files during this audit. Uncommitted work was not discarded.

---

## A. Audit scope

| Item | Verified value |
| --- | --- |
| Project root | `E:\Job POrtal\TalentBridgeAI` |
| Django project | `backend\legacy-django` |
| Settings | `config.settings` → `backend\legacy-django\config\settings.py` |
| Python (venv) | **3.12.10** |
| Django (installed) | **5.2.19** |
| Dependency file | `backend\legacy-django\requirements.txt` (alias tree `legacy-django\requirements.txt`) |
| Env template | `.env.example` (keys only; no live secrets) |
| Private env | `.env` present (values **not** reproduced) |
| Apps / workflows | `jobs` views/models/tests; allauth Google; resume upload/download/preview/delete; job/application ownership; admin company approve; contact; login/signup |
| Runtime probe host | `http://127.0.0.1:8000` (existing managed server) |

**Not a penetration test.** No malware uploads, brute force, credential theft, or destructive scans.

---

## B. Secrets audit

### Approach
- Secrets loaded via environment / `.env` / optional `.django_secret_key` (Day 4 pattern re-verified).
- Inventory script records **presence and length only**, never values.
- `.env` contents were **not** dumped into reports or terminals.

### Handling summary

| Control | Result |
| --- | --- |
| `DJANGO_SECRET_KEY` in env | SET (len=50); not `django-insecure-*` |
| Hardcoded `SECRET_KEY` in settings | **No** |
| `.env` / `.django_secret_key` in `.gitignore` | **Yes** |
| `.django_secret_key` file present | **No** (env used) |
| `.env.example` real credentials | **No** (empty placeholders) |
| OAuth secrets in env this audit shell | `GOOGLE_CLIENT_ID`/`SECRET` names UNSET; settings expect `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET` |
| SMTP / DB password | UNSET (SQLite path) |
| Frontend bundles with API secrets | No evidence of embedded production secrets in scanned app JS |

### Findings

#### D9-S01 — Packaging verification uses a fixed `DJANGO_SECRET_KEY` string in source
- **Severity:** MEDIUM  
- **Confidence:** CONFIRMED  
- **File:** `tools/package_release.py` (release extraction check env)  
- **Evidence:** Process env for portable verification sets `DJANGO_SECRET_KEY` to a fixed non-production placeholder string (value not reproduced here beyond noting it is a constant in source).  
- **Impact:** If that packaging path were ever used as a real deploy without overriding the key, sessions/CSRF signing would be predictable. Local live `.env` key is separate.  
- **Remediation:** Generate ephemeral random key for verification runs; never ship the constant into production env.  
- **Approval required:** Yes  

#### D9-S02 — Secret-generation helpers write into private `.env`
- **Severity:** INFORMATIONAL  
- **Confidence:** CONFIRMED  
- **Files:** `tools/windows_manager.py`, `tools/bootstrap_env.py`  
- **Evidence:** Generate `secrets.token_urlsafe(...)` into `.env` when missing; logs say key generated without echoing it.  
- **Impact:** Acceptable local bootstrap; ensure production always supplies operator-managed key.  

#### D9-S03 — Test fixtures use literal test passwords
- **Severity:** INFORMATIONAL  
- **Confidence:** CONFIRMED  
- **File:** `backend/legacy-django/jobs/tests.py` (and related tests)  
- **Evidence:** Pattern scan hit many `password="..."` **test** assignments only.  
- **Impact:** Normal for unit tests; not production credentials.  

**No CRITICAL live credential committed to application settings was confirmed.** Git history could not be inspected (no `.git` directory in this workspace copy).

---

## C. Upload security audit

### Entry points / fields

| Model field | Storage | Notes |
| --- | --- | --- |
| `jobs.Profile.resume` | `FileField` → `resumes/` under `MEDIA_ROOT`=`private_media/` | Primary sensitive upload |
| `jobs.Company.logo` | `ImageField` → `company_logos` | Field exists; `company_profile_view` does **not** currently accept logo file POSTs |

**URLconf:** No public `MEDIA_URL` static mount (reconfirmed). Resume access via `resume_download` / `resume_preview` / `resume_delete`.

### Resume upload (`resume_management`) — `jobs/views.py`

| Control | Status |
| --- | --- |
| Auth | `@login_required` |
| Extensions | `.pdf`, `.doc`, `.docx` |
| Size (view) | ≤ 5 MiB |
| Content signatures | PDF `%PDF-`; DOC OLE magic; DOCX ZIP + required OOXML members |
| Rejects mismatched contents | Yes (covered by existing tests) |
| Replacement | Saves new file; deletes previous storage name if changed |
| Delete | Owner-only `@require_POST` |
| Download | Owner **or** employer owning the related application (`job__company__owner=request.user`) |
| Preview | Owner-only; PDF only; `X-Content-Type-Options: nosniff` |
| Direct `/media/...` | Test expects 404; no media route |

### Findings

#### D9-U01 — Request body limit vs resume 5 MB policy mismatch
- **Severity:** MEDIUM  
- **Confidence:** CONFIRMED  
- **Settings:** Django defaults `DATA_UPLOAD_MAX_MEMORY_SIZE` / observed **2621440** (2.5 MiB)  
- **View:** Allows up to **5 MiB**  
- **Impact:** Uploads between ~2.5–5 MiB may fail at the request parser before view validation, or behave inconsistently vs UX copy.  
- **Remediation:** Raise `DATA_UPLOAD_MAX_MEMORY_SIZE` (and related limits) above the resume cap, or lower the advertised/enforced resume max to ≤ request limit.  
- **Approval required:** Yes  

#### D9-U02 — Company logo lacks a dedicated validated upload path
- **Severity:** LOW / INFORMATIONAL  
- **Confidence:** CONFIRMED  
- **Evidence:** `ImageField` on model; company profile POST updates text fields only.  
- **Impact:** Low today (unused path). If logo upload is added later, require size/type checks and authz.  

**Positive:** Resume validation goes beyond browser `Content-Type` / extension-only checks. Private storage + gated download is the right pattern.

---

## D. Authentication and permission audit

### Authentication
- Login: custom `login_view` + allauth/Google start.  
- Logout: `@require_POST` `logout_view` (GET cannot logout).  
- Password validators: 4 Django validators configured.  
- Signup password rules: length + upper/lower/digit/symbol in `_register`.  
- `next` redirects validated with `url_has_allowed_host_and_scheme` (login, social, saved-job).  
- Dashboard HTML under `/pages/dashboard/` requires authentication in `page_file`.

### Role / object ownership (source-verified)
| Operation | Enforcement |
| --- | --- |
| Create/edit/toggle job | `Company` owned by `request.user`; job scoped to that company |
| Update application status | `job__company__owner=request.user` + POST only |
| Candidate details | Same ownership filter on `application_id` |
| Candidate search | Approved company owner only |
| Resume download via `application_id` | Employer must own job’s company |
| Admin dashboard / approve company | `is_staff` (+ `jobs.change_company` for approve) |
| Profile POST | Updates **own** user/profile only; **does not** accept `role` from POST |
| Signup role | Fixed by view (`jobseeker_signup` / `employer_signup`), not client-chosen free text beyond those endpoints |

### Findings

#### D9-A01 — Custom email/password login has no rate limiting
- **Severity:** HIGH  
- **Confidence:** CONFIRMED  
- **File:** `jobs/views.py` → `login_view`  
- **Evidence:** Authenticates via `authenticate`/`login` with no `ratelimit`, lockout, or backoff. Project code has no django-axes/defender. allauth rate limits do **not** wrap this custom view.  
- **Impact:** Online password guessing against known emails if the service is network-reachable.  
- **Remediation:** Add server-side rate limits / lockout on failed logins (and consider same for signup, contact, password reset).  
- **Approval required:** Yes  

#### D9-A02 — Email verification effectively disabled
- **Severity:** MEDIUM  
- **Confidence:** CONFIRMED  
- **Evidence:** `ACCOUNT_EMAIL_VERIFICATION = "none"`; `resend_verification` tells users verification is temporarily disabled; `_register` does not require verified email before job-seeker sign-in; login path can activate inactive unverified password accounts when password matches.  
- **Impact:** Weaker assurance that mailbox ownership is proven; easier disposable-email account abuse.  
- **Remediation:** Re-enable verification for production; remove auto-activate shortcut; align allauth + custom signup.  
- **Approval required:** Yes  

#### D9-A03 — `SOCIALACCOUNT_LOGIN_ON_GET = True`
- **Severity:** MEDIUM  
- **Confidence:** CONFIRMED  
- **File:** `config/settings.py`  
- **Impact:** OAuth login can start via GET (CSRF tradeoff common with allauth). Prefer POST-only start where UX allows.  
- **Approval required:** Yes  

**Object-level IDOR (sampled):** Employer-scoped filters on application/job/resume paths are present and match Day 6 intent. No CONFIRMED broken ownership check found in the reviewed sensitive views. Full authenticated exploit runtime not performed (no foreign-user credentials used).

---

## E. DEBUG and error leakage audit

| Context | `DEBUG` |
| --- | --- |
| Audit `django.setup()` after `.env` (no `DJANGO_ENV`) | **False** |
| Managed server on :8000 | Behaves as **DEBUG True** (404 technical page + `/__dev__/` 200) |

#### D9-D01 — Unauthenticated DEBUG 404 discloses URLconf
- **Severity:** HIGH if host is reachable beyond trusted admins; **MEDIUM** for localhost-only lab (report as **HIGH** for deployment readiness)  
- **Confidence:** CONFIRMED on live `:8000`  
- **Evidence:** `GET /no-such-page-day9-xyz/` → 404 HTML containing “Django tried these URL patterns” / URLconf listing (including password-reset route **names**, not secret values). No `SECRET_KEY` string observed in body. Screenshot lineage also in Day 8 (`day8_contact_relative_link_404.png`).  
- **Impact:** Attack surface mapping for anonymous users whenever DEBUG is on.  
- **Remediation:** Ensure production `DJANGO_ENV=production` and `DJANGO_DEBUG=false`; never expose managed launcher DEBUG to the public Internet; custom 404 when DEBUG is off.  
- **Approval required:** Yes (config/process); no silent `.env` change made  

#### D9-D02 — `/__dev__/` available under DEBUG
- **Severity:** MEDIUM  
- **Confidence:** CONFIRMED  
- **Evidence:** `GET /__dev__/` → 200 live-preview dashboard HTML.  
- **Impact:** Dev-only tooling exposed whenever DEBUG is on.  
- **Remediation:** Gate to staff/local only or disable outside development.  

#### D9-D03 — Dual DEBUG gate / `.env.example` omits `DJANGO_ENV`
- **Severity:** LOW  
- **Confidence:** CONFIRMED (also Day 4)  
- **Impact:** Operator confusion between CLI and launcher DEBUG.  

---

## F. Django security configuration

| Setting / middleware | Observed (audit shell) | Notes |
| --- | --- | --- |
| SecurityMiddleware, CsrfViewMiddleware, Auth, Sessions, XFrame | Present | Good baseline |
| `SESSION_COOKIE_HTTPONLY` | True | Good |
| `SESSION_COOKIE_SAMESITE` / CSRF SameSite | Lax | OK local |
| `SESSION_COOKIE_SECURE` / `CSRF_COOKIE_SECURE` | False | Expected local HTTP |
| `SECURE_SSL_REDIRECT` | False | Expected local |
| `SECURE_HSTS_SECONDS` | 0 | Expected local |
| `SECURE_CONTENT_TYPE_NOSNIFF` | True | Good |
| `SECURE_REFERRER_POLICY` | same-origin | Good |
| `X_FRAME_OPTIONS` | DENY | Good |
| CSP | Not configured | Defense-in-depth gap |
| `MEDIA_URL` | Implicit `'/'` | Unusual; media not publicly routed |
| `check --deploy` | 4 warnings (W004, W008, W012, W016) | HTTPS cookie/HSTS/redirect |

#### D9-C01 — Production HTTPS cookie/HSTS settings unset
- **Severity:** MEDIUM (for internet HTTPS deploy); INFORMATIONAL for current local HTTP  
- **Confidence:** CONFIRMED  
- **Remediation:** Before public HTTPS deploy, set Secure cookies, SSL redirect (or proxy), HSTS carefully.  
- **Approval required:** Yes  

---

## G. Common vulnerability review

| Class | Result |
| --- | --- |
| CSRF | Middleware on; logout/state changes use POST where reviewed; no project `csrf_exempt` in `jobs/` app code |
| XSS | Template `|safe` only on Django password help_text (`account-security.html`) — generally framework HTML; no app `mark_safe` on user content found in `jobs/` |
| SQL injection | No app `RawSQL`/`cursor.execute` in `jobs`/`config`; ORM used |
| Open redirect | `next` validated with `url_has_allowed_host_and_scheme` in reviewed paths |
| Unsafe GET state change | Logout requires POST; status toggles use `@require_POST` |
| Rate limiting / abuse | **Missing** on custom login/signup/contact (see D9-A01 / D9-R01) |

#### D9-R01 — No application-level abuse controls on public POST endpoints
- **Severity:** MEDIUM  
- **Confidence:** CONFIRMED  
- **Evidence:** Contact creates DB rows; signup/login unrestricted beyond validation.  
- **Remediation:** Rate limit by IP/account; captcha optional for public forms.  

---

## H. Dependency audit

### Declared (`requirements.txt`)
```
Django>=5.2,<5.3
django-allauth[socialaccount]>=65.21,<66
python-dotenv>=1.0,<2
Pillow>=10.0,<13
PyMySQL>=1.1,<2
```

### Installed (venv `pip list`, 2026-11-18)

| Package | Installed | Notes |
| --- | --- | --- |
| Django | 5.2.19 | Current 5.2 security release (fixes CVE-2026-108147 and related 2026-11-03 issues **in this version**) |
| django-allauth | 65.22.1 | Latest line; Snyk reports no known direct vulns on 65.22.1; older CVEs fixed earlier |
| Pillow | 12.3.0 | Within declared range |
| python-dotenv | 1.2.4 | |
| PyMySQL | 1.2.4 | |
| requests / urllib3 / cryptography / PyJWT / oauthlib | Present (allauth transitive) | |
| reportlab | 5.1.0 | **Installed but not declared** in requirements.txt |
| pip | 26.3 | |

### Vulnerability tooling
- `pip audit` / `pip-audit` **not installed** — **NOT VERIFIED** via automated advisory DB in-venv.  
- Advisory status for Django/allauth taken from official Django weblog / allauth release notes / Snyk package page (scan date 2026-11-18).  
- **No automatic upgrades performed.**

#### D9-P01 — `reportlab` installed but undeclared
- **Severity:** LOW  
- **Confidence:** CONFIRMED  
- **Impact:** Reproducible builds / supply-chain inventory gap.  

#### D9-P02 — Django/allauth currently on patched lines
- **Severity:** INFORMATIONAL  
- **Confidence:** STRONG EVIDENCE  
- **Note:** Stay on maintained releases; re-run advisory checks when tools are approved.

---

## I. Git and repository security

| Check | Result |
| --- | --- |
| `.git` directory present in workspace | **No** |
| History secret scan | **NOT VERIFIED** (no git) |
| `.gitignore` excludes `.env`, `.django_secret_key`, `private_media/`, `*.sqlite3`, `backups/`, `logs/` | **Yes** |
| `git` CLI on PATH | Not available in audit shell |

#### D9-G01 — No local Git metadata to prove tracking status
- **Severity:** INFORMATIONAL  
- **Confidence:** CONFIRMED  
- **Remediation:** When a remote repo exists, verify with `git ls-files` that `.env` / DB / `private_media` are untracked; rotate if history ever contained secrets.  

---

## J. Prioritized security backlog

| ID | Severity | Confidence | Summary | Approval |
| --- | --- | --- | --- | --- |
| D9-A01 | HIGH | CONFIRMED | Custom login lacks rate limiting | Yes |
| D9-D01 | HIGH* | CONFIRMED | DEBUG 404 URLconf disclosure on managed server | Yes |
| D9-A02 | MEDIUM | CONFIRMED | Email verification disabled / weak verify path | Yes |
| D9-A03 | MEDIUM | CONFIRMED | `SOCIALACCOUNT_LOGIN_ON_GET` | Yes |
| D9-U01 | MEDIUM | CONFIRMED | Upload size limit mismatch (2.5 vs 5 MB) | Yes |
| D9-S01 | MEDIUM | CONFIRMED | Fixed packaging verification secret in source | Yes |
| D9-C01 | MEDIUM | CONFIRMED | Deploy HTTPS cookie/HSTS unset | Yes |
| D9-R01 | MEDIUM | CONFIRMED | No abuse limits on public POSTs | Yes |
| D9-D02 | MEDIUM | CONFIRMED | `/__dev__/` exposed when DEBUG | Yes |
| D9-U02 | LOW | CONFIRMED | Logo upload path unused / unvalidated | Yes |
| D9-D03 | LOW | CONFIRMED | `.env.example` missing `DJANGO_ENV` | Yes |
| D9-P01 | LOW | CONFIRMED | Undeclared `reportlab` | Yes |
| D9-S02/S03/P02/G01 | INFO | CONFIRMED / STRONG | Bootstrap/tests/patched deps/no git | — |

\*Treat D9-D01 as blocking for any non-local exposure while DEBUG remains forced by the launcher.

**Counts:** CRITICAL **0** · HIGH **2** · MEDIUM **7** · LOW **3** · INFORMATIONAL **4**

---

## K. Verification evidence

| Check | Result |
| --- | --- |
| `python tools/_day9_security_inventory.py` | Wrote inventory JSON; Django 5.2.19; DEBUG False in CLI |
| `manage.py check` | No issues |
| `manage.py check --deploy` | 4 security warnings (W004/W008/W012/W016) |
| `pip list` | Versions recorded above |
| `pip audit` / `pip-audit` | Unavailable (not installed; not installed per policy) |
| HTTP `GET` unknown path on :8000 | 404 with URLconf markers |
| HTTP `GET /__dev__/` | 200 |
| Source review | settings, views upload/auth ownership, urls media absence, package_release, `.gitignore`, `.env.example` |
| Existing tests (read) | Resume content validation + download ACL tests present |

### Unverified / blockers
- Authenticated cross-user runtime IDOR suite (source-reviewed only).  
- Full CVE database scan via pip-audit/Safety (tool missing).  
- Git history secret search (no `.git`).  
- Production HTTPS behavior (no production host).  
- Destructive upload/malware tests (intentionally not run).

---

## L. Day 9 completion status

**COMPLETE** — Required Day 9 categories were inspected with evidence and clear verification limits. No risky remediations applied.

**Day 10 was not started.**

---

## Recommended next actions (await approval)

1. Keep DEBUG off for any shared/network exposure; document launcher DEBUG risk.  
2. Add login (and public POST) rate limiting.  
3. Align `DATA_UPLOAD_MAX_MEMORY_SIZE` with resume 5 MB policy.  
4. Plan email-verification re-enable for production.  
5. Before public HTTPS: address `check --deploy` warnings.  
6. Optionally install an approved `pip-audit` and declare `reportlab` if required.  
7. Proceed to Day 10 phase-gate only after explicit approval.
