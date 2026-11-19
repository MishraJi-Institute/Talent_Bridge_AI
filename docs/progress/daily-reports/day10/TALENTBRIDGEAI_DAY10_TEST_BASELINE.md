# TalentBridgeAI — Day 10 Test Baseline

**Date:** 2026-11-18  
**Python:** 3.12.10 (`backend/legacy-django/.venv`)  
**Django:** 5.2.19  
**Settings:** `config.settings`  
**Test runner:** Django `manage.py test` (isolated test database; development DB not modified)

---

## 1. Test infrastructure discovered

| Item | Location / notes |
| --- | --- |
| Primary suite | `backend/legacy-django/jobs/tests.py` |
| Additional modules | `test_dev_preview.py`, `test_new_quality_features.py`, `test_acceptance_flows.py`, `test_email_login_backend.py` |
| pytest config | **Not present** as project standard (Django DiscoverRunner used) |
| CI | `.github/workflows/static.yml` builds static `site/` — not the Django test suite |
| Fixtures | Created inside TestCase methods; no separate fixture package required for this run |

---

## 2. Baseline results (executed 2026-11-18)

| Test / Check | Command or Method | Result | Evidence | Notes |
| --- | --- | --- | --- | --- |
| Django system check | `manage.py check` | **PASS** | CLI: “0 silenced” | No issues |
| Deploy security check | `manage.py check --deploy` (Day 9) | **WARN** | W004, W008, W012, W016 | Expected for local HTTP |
| `jobs` test suite | `manage.py test jobs --verbosity=1` | **FAIL (2)** | See §3 | **171** discovered/executed |
| Route smoke (running server) | HTTP GET sample routes on `:8000` | **PASS** | `docs/reports/_day10_route_smoke.json` | Public 200; auth redirects |
| Managed server availability | Existing VS Code / `windows_manager` task | **PASS** | Terminal task active | Not restarted for Day 10 |
| Startup guide dry-run kill/restart | — | **NOT RUN** | — | Avoided disrupting live managed server |

### Suite totals (accurate for this run)

| Metric | Count |
| --- | ---: |
| Tests discovered/executed (`jobs`) | **171** |
| Passed | **169** |
| Failed | **2** |
| Skipped | **0** (none reported) |
| Errors | **0** |
| Duration | ~307 s |

---

## 3. Failed tests (baseline defects — not fixed on Day 10)

### F1 — `ApprovedCompanyDirectoryTests.test_directory_is_empty_without_approved_employers`
- **Expected:** Response contains `No approved companies yet`
- **Actual:** DEBUG/demo illustrative company cards (Google, Northstar Studio, …) when no approved employers
- **Impact:** Empty-state copy/tests drifted from demo-company fallback behavior
- **Backlog:** TB-P2-DEMO-EMPTY (also related D8-S01)

### F2 — `LandingPageTests.test_jobs_route_keeps_job_search_page`
- **Expected:** `href="/">TalentBridge AI</a>` markup
- **Actual:** Logo markup is `<a href="/">` + image + `TalentBridge<span class="logo-accent">AI</span>` (string mismatch)
- **Impact:** Brittle assertion vs redesigned header; page itself loads
- **Backlog:** TB-P3-TEST-BRITTLE-HEADER

---

## 4. Known test gaps (not claimed as coverage %)

- No browser/E2E automation suite in-repo for Day 10.
- Authenticated multi-role IDOR scenarios covered partially by unit tests; not re-run as a separate security harness.
- `pip-audit` not available (Day 9).
- Static GitHub Pages workflow does not gate Django tests.

---

## 5. Day 10 test-baseline status

**ESTABLISHED** with **2 known failures**. Development database and private media were not modified by the test run (Django created/destroyed a temporary test DB).
