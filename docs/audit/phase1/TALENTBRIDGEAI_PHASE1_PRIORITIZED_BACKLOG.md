# TalentBridgeAI — Phase 1 Prioritized Backlog

**Date:** 2026-11-18  
**Sources:** Days 1–9 audits + Day 10 test baseline  
**Policy:** Confirmed defects and security findings vs missing future features are labeled separately.

Effort scale (evidence-based, coarse): **S** ≤0.5 day · **M** 1–2 days · **L** multi-day / coordination.

---

## Priority summary

| Priority | Count |
| --- | ---: |
| P0 Critical | **0** |
| P1 High | **4** |
| P2 Medium | **11** |
| P3 Low | **8** |

---

## P1 — High

### TB-P1-LOGIN-RATELIMIT
- **Title:** Add rate limiting / lockout to custom email-password login  
- **Area:** Security / Auth  
- **Source:** Day 9 D9-A01  
- **Files:** `backend/legacy-django/jobs/views.py` (`login_view`)  
- **Problem:** Custom login has no server-side attempt throttling; allauth limits do not wrap this view.  
- **Evidence:** Source review Day 9  
- **Impact:** Password guessing if service is network-reachable  
- **Type:** Security finding  
- **Deps:** None  
- **Action:** Add IP/account rate limits; optional lockout messaging  
- **Effort:** M  
- **Acceptance:** Failed logins throttle; tests cover lockout path  
- **Approval:** Yes  

### TB-P1-DEBUG-LEAK
- **Title:** Prevent DEBUG URLconf disclosure on shared/network hosts  
- **Area:** Security / Ops  
- **Source:** Day 9 D9-D01, Day 8 screenshot E-D8-05  
- **Files:** Launcher `tools/windows_manager.py`; settings DEBUG gate; optional custom 404  
- **Problem:** Managed DEBUG 404 pages list URL patterns to anonymous users.  
- **Evidence:** HTTP 404 body markers; Day 8 screenshot  
- **Impact:** Attack-surface mapping  
- **Type:** Security finding  
- **Deps:** Settings separation (roadmap Day 14)  
- **Action:** Keep DEBUG off outside trusted local; document; harden launcher for shared use  
- **Effort:** S–M  
- **Acceptance:** Non-DEBUG 404 has no URLconf dump; prod checklist documented  
- **Approval:** Yes  

### TB-P1-TEST-COMPANIES-EMPTY
- **Title:** Align companies empty-state with demo fallback (or fix demo gating)  
- **Area:** Companies / Tests  
- **Source:** Day 10 test F1  
- **Files:** `jobs/views.py` `company_directory`; companies template; `jobs/tests.py`  
- **Problem:** Test expects “No approved companies yet”; DEBUG shows illustrative companies instead.  
- **Evidence:** `manage.py test` failure 2026-11-18  
- **Impact:** Broken CI confidence; UX inconsistency  
- **Type:** Confirmed defect (test vs behavior drift)  
- **Deps:** TB-P2-DEMO-EMPTY  
- **Action:** Update empty copy **or** hide demo cards in test/non-demo modes consistently  
- **Effort:** S  
- **Acceptance:** Test passes; empty vs demo messaging consistent  
- **Approval:** Yes  

### TB-P1-EMAIL-VERIFY
- **Title:** Re-enable coherent email verification for production path  
- **Area:** Auth  
- **Source:** Day 9 D9-A02  
- **Files:** `config/settings.py` (`ACCOUNT_EMAIL_VERIFICATION`); `resend_verification`; `_register` / `login_view`  
- **Problem:** Verification disabled; auto-activate path weakens mailbox proof.  
- **Evidence:** Settings + views Day 9  
- **Impact:** Account abuse / weaker identity assurance  
- **Type:** Security finding  
- **Deps:** SMTP configuration  
- **Action:** Production verification on; remove unsafe shortcuts  
- **Effort:** M–L  
- **Acceptance:** Unverified users cannot fully use gated features per policy  
- **Approval:** Yes  

---

## P2 — Medium

| ID | Title | Source | Type | Effort | Approval |
| --- | --- | --- | --- | --- | --- |
| TB-P2-UPLOAD-LIMIT | Align `DATA_UPLOAD_MAX_MEMORY_SIZE` with 5 MB resume policy | D9-U01 | Defect/config | S | Yes |
| TB-P2-DEMO-EMPTY | Homepage 0 stats vs DEBUG demo jobs/companies messaging | D8-S01, Day 10 F1 | UX/defect | M | Yes |
| TB-P2-REL-HREFS | Replace residual relative `*.html` nav with `{% url %}` / slugs | D8-L01 | Tech debt | M | Yes |
| TB-P2-APPLY-HASH | Application form `#` action when no job | D8-F01 | Defect | S | Yes |
| TB-P2-PUBLIC-POST-LIMIT | Rate-limit contact/signup/password-reset POSTs | D9-R01 | Security | M | Yes |
| TB-P2-OAUTH-GET | Review `SOCIALACCOUNT_LOGIN_ON_GET` | D9-A03 | Security hardening | S | Yes |
| TB-P2-DEV-ENDPOINT | Restrict `/__dev__/` outside trusted DEBUG | D9-D02 | Security | S | Yes |
| TB-P2-PACK-SECRET | Ephemeral key for `package_release` verification | D9-S01 | Security/tech debt | S | Yes |
| TB-P2-HTTPS-COOKIES | Production Secure cookies / HSTS / SSL redirect checklist | D9-C01 | Ops | M | Yes |
| TB-P2-FORM-UX | Verify login/contact submit loading/disabled states | D8-F02 | Unverified gap | M | Yes |
| TB-P2-FRONTEND-AUTH | Authenticated dashboard/runtime frontend audit pass | Day 8 partial | Unverified | L | Yes |

---

## P3 — Low

| ID | Title | Source | Type | Effort |
| --- | --- | --- | --- | --- |
| TB-P3-JDASH-HASH | jdashboard Portfolio/LinkedIn/GitHub/Resume `href="#"` | D8-L02 | Defect | S |
| TB-P3-ERROR-LABEL | Page directory “Site error page” → `/404/` | D8-L03 | Defect | S |
| TB-P3-LOGIN-MOBILE | Login mobile CTA density | D8-R01 | UX | S |
| TB-P3-MIXED-URLS | Mixed `/pages/*.html` vs slug nav | D8-U03 | Tech debt | S |
| TB-P3-ENV-EXAMPLE | Document `DJANGO_ENV` in `.env.example` | D4/D9-D03 | Docs | S |
| TB-P3-MEDIA-URL | Explicit private `MEDIA_URL` convention | D4 | Config | S |
| TB-P3-REPORTLAB | Declare `reportlab` in requirements if required | D9-P01 | Inventory | S |
| TB-P3-TEST-BRITTLE-HEADER | Fix jobs header string assertion | Day 10 F2 | Test debt | S |

---

## Future roadmap work (not bugs)

| Item | Maps to roadmap | Notes |
| --- | --- | --- |
| Folder/template/static organization | Days 11–12 | Structure already partially organized; remaining cleanup |
| README/setup polish beyond Day 10 guide | Day 13 | Guide exists; Day 13 may deepen |
| Dev/test/prod settings split | Day 14 | Dual DEBUG gate today |
| DB connection/migration workflow UX | Day 15 | SQLite works; MySQL documented |
| Shared base template / nav | Day 16 | Multiple header patterns |
| Design tokens | Day 17 | CSS variables partial |
| Error/loading states | Day 18 | Gaps in Day 8 |
| Static/media behavior | Day 19 | Private media pattern OK; polish later |
| AI resume / provider | Later roadmap | Explicitly not connected |

---

## Unverified assumptions (do not treat as defects)

- Full authenticated cross-tenant IDOR runtime suite not exhausted beyond unit tests.  
- Git history secret scan blocked (no `.git` in this workspace copy).  
- `pip-audit` not run (tool not installed).
