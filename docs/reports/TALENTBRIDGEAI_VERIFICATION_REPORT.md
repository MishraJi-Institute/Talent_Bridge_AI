# TalentBridgeAI — Verification Report

Date: 2026-11-18

## Live server

- Port file: **8001** (not 8000)
- Live site: **http://127.0.0.1:8001/**
- Manager health: `/`, `/login/`, admin, signup routes **200**

## ERR_CONNECTION_REFUSED diagnosis

Connection refused occurs when Django is **not listening**. It is unrelated to HTML being under `frontend/pages/`.

Verified while server running:

| URL | Result |
| --- | --- |
| `http://127.0.0.1:8001/` | 200 |
| `http://127.0.0.1:8001/login/` | 200 (Sign In page renders) |
| `http://127.0.0.1:8001/pages/login.html` | 200 |
| `http://127.0.0.1:8001/pages/signup-role.html` | 200 |
| `http://127.0.0.1:8001/jobs/` | 200 |
| `/css/pages/tb-homepage-elevate.css` | 200 |
| `/js/core/tb-hero-network.js` | 200 |
| `/images/tb-hero-candidate.jpg` | 200 |

Browser checks: homepage + login opened successfully in Cursor browser.

## Django checks

| Check | Result |
| --- | --- |
| `manage.py check` | PASS (0 issues) |
| Migrations 0001–0014 | Applied (prior verify) |
| `manage.py test jobs` | **169 tests OK** (~382s) after path/assertion updates |

## Remaining limitations

- Google OAuth still config-gated (button may be disabled without `.env` credentials)
- Email verification still disabled operationally
- Homepage match scene remains labelled DEMO DATA (no LLM provider)
- Port may vary (8000/8001); use `.talentbridge_django.port` or manager status
- `git` not on PATH here — no commit performed
