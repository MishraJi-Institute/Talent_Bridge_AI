# TalentBridgeAI — Day 4 Django Settings Audit

**Date:** 2026-11-18  
**Roadmap day:** Day 4 only (settings audit)  
**Status:** COMPLETE  
**Auditor:** Senior Django settings audit (Cursor agent)  
**Constraint honored:** No `.env` edits, no SECRET_KEY rotation, no migrations, no database changes, no static/media reorganization, no Day 5+ work.

---

## 1. Project root and settings architecture

| Item | Verified value |
| --- | --- |
| Workspace / project root | `E:\Job POrtal\TalentBridgeAI` |
| Django project directory (`BASE_DIR`) | `E:\Job POrtal\TalentBridgeAI\backend\legacy-django` |
| `manage.py` | `backend\legacy-django\manage.py` |
| Settings module | `config.settings` |
| Canonical settings file | `backend\legacy-django\config\settings.py` |
| Junction alias | `legacy-django\` → same tree as `backend\legacy-django\` (not a second settings codebase) |
| Frontend root | `E:\Job POrtal\TalentBridgeAI\frontend` |
| Env file (private) | `E:\Job POrtal\TalentBridgeAI\.env` (loaded; values not reproduced) |
| Env template | `E:\Job POrtal\TalentBridgeAI\.env.example` |
| Requirements | `backend\legacy-django\requirements.txt` |
| Runtime Django | **5.2.19** (venv); header comment in settings still says “Generated … Django 6.1.1” (documentation drift only) |

**Architecture:** Single monolithic settings module (`config.settings`). There is **no** `settings/base.py` / `development.py` / `production.py` package split. Environment differences are driven by variables (and the Windows launcher override), not by alternate settings modules.

**Backup / historical copy inspected for comparison only (not loaded at runtime):**  
`backups\structure_20261118_002618\config_snapshot\settings.py`

---

## 2. Settings files and loaders inspected

| Path | Role |
| --- | --- |
| `backend/legacy-django/config/settings.py` | Sole runtime settings |
| `backend/legacy-django/manage.py` | Sets `DJANGO_SETTINGS_MODULE=config.settings` |
| `backend/legacy-django/config/wsgi.py` | Same settings module |
| `backend/legacy-django/config/asgi.py` | Same settings module |
| `tools/windows_manager.py` (`launcher_env`) | Forces `DJANGO_ENV=development`, `DJANGO_DEBUG=true` for managed runserver |
| `.env.example` | Template keys (no secrets) |
| `.gitignore` | Ignores `.env` and `.django_secret_key` |
| `scripts/install/CREATE_SUPERUSER.bat`, `CONNECT_GOOGLE_OAUTH.ps1` | Set development DEBUG flags for those scripts |
| `tools/package_release.py` | Portable packaging env (includes a non-production verification secret string in source — see §14) |

**Not present:** separate production settings module; Whitenoise; custom `STORAGES` override beyond Django defaults.

---

## 3. DEBUG audit

| Question | Finding |
| --- | --- |
| Where defined | `config/settings.py` — `DJANGO_ENV` + `DJANGO_DEBUG` |
| Hardcoded? | **No.** Computed from environment. |
| Default if env missing | `DJANGO_ENV` defaults to **`production`**; `DJANGO_DEBUG` defaults to **`false`** → **`DEBUG = False`** |
| Enable condition | `DJANGO_ENV ∈ {development, local}` **AND** `DJANGO_DEBUG ∈ {1,true,yes,on}` |
| Dev vs prod distinguishable? | **Yes**, via `DJANGO_ENV` / `DJANGO_DEBUG` (and launcher overrides). |
| Accidental production DEBUG? | **Low** if process env omits `DJANGO_ENV=development`. **Higher** for the managed Windows launcher, which **always** sets development + debug. |
| Sensitive error pages | With `DEBUG=False`, Django does not serve traceback pages to clients. With managed `DEBUG=True`, detailed error pages are possible on the local machine. |
| Consistency across modules | Only one settings module; consistent. |

### Runtime evidence (this audit)

| Context | `DJANGO_ENV` | `DJANGO_DEBUG` | Observed `DEBUG` |
| --- | --- | --- | --- |
| Audit shell (`django.setup()` after `load_dotenv`) | **UNSET** in process → settings default `production` | **SET** in `.env` (true) | **`False`** |
| Managed server (`windows_manager` / VS Code start) | Forced `development` by `launcher_env()` | Forced `true` | **`True`** (inferred: `/__dev__/` live-preview URL advertised and health 200; LivePreviewMiddleware only inserts when `DEBUG`) |

**.env.example gap:** documents `DJANGO_DEBUG=true` but **does not document `DJANGO_ENV`**. Copying the example alone does **not** enable `DEBUG` under the settings formula unless the launcher sets `DJANGO_ENV`.

**Classification:** C Configuration inconsistency (template vs dual-gate logic); E Improvement (document `DJANGO_ENV` in `.env.example`).

---

## 4. SECRET_KEY audit

| Question | Finding |
| --- | --- |
| Definition | `SECRET_KEY` in `config/settings.py` |
| Load order | 1) `DJANGO_SECRET_KEY` env → 2) `PROJECT_ROOT/.django_secret_key` file → 3) generate `secrets.token_urlsafe(50)` and write file |
| Hardcoded in settings? | **No** |
| Present at runtime? | **Yes** (length observed only: 50 characters) |
| Source this audit | **ENV** (`SECRET_KEY_SOURCE=ENV`); `.django_secret_key` file **absent** |
| Tracked / committed? | `.env` and `.django_secret_key` are in `.gitignore`. No Git repository present in this workspace copy, so commit exposure could not be verified via `git ls-files`. |
| Silent insecure fallback? | Auto-generation produces a strong random key and persists it; not the Django `django-insecure-…` default. Risk: first-run generation without noticing if env is empty. |
| Multiple loaders? | Settings + `windows_manager` can **generate** a key into `.env` if missing; values never printed by design. |
| Logs | No evidence settings print the key; installer messages say key was generated without echoing it. |

**IMPORTANT:** Actual key material is **not** included in this report.

**Related observation (future / packaging):** `tools/package_release.py` embeds a fixed string used as `DJANGO_SECRET_KEY` for portable release verification only. That is a **known weak key in source** for a packaging path, not the live local `.env` key.

**Classification:** B Security risk (packaging constant — future hardening); E ensure production always uses env-provided persistent key (already the installer path).

**Correction safety now:** Do **not** rotate or rewrite `.env` during Day 4.

---

## 5. ALLOWED_HOSTS audit

| Question | Finding |
| --- | --- |
| Definition | Parsed from `DJANGO_ALLOWED_HOSTS` CSV |
| Default if unset | `localhost,127.0.0.1,[::1]` |
| Runtime observed | `['localhost', '127.0.0.1', '[::1]']` |
| Wildcards | **None** |
| Empty list risk | Empty segments stripped; if env were only commas, list could be empty → Host header rejection (fail closed). |
| Production domains | **Not configured** in this environment (no invented domains). |

**Appropriate for local development:** Yes.  
**Production:** Operator must set real hosts via `DJANGO_ALLOWED_HOSTS` — recommendation only.

Also present (related, not Day-4 category but load-adjacent):  
`CSRF_TRUSTED_ORIGINS` defaults to local `http://127.0.0.1:8000|8001` and `http://localhost:8000|8001`.

**Classification:** E Improvement recommendation for production host inventory.

---

## 6. Database configuration audit

| Question | Finding |
| --- | --- |
| Selection | `DB_ENGINE` env: `sqlite` (default) or `mysql`; else `ImproperlyConfigured` |
| Runtime engine | `django.db.backends.sqlite3` |
| Runtime name/path | `E:\Job POrtal\TalentBridgeAI\database\TalentBridgeAI.sqlite3` |
| File exists | **Yes** |
| Host/user/password | **N/A** for active SQLite path |
| Options | `timeout: 20` |
| `CONN_MAX_AGE` | Not set for SQLite (observed `0` / default); MySQL branch sets `60` |
| MySQL branch | Env: `DB_NAME`, `DB_USER` (default `root`), `DB_PASSWORD` (default empty), `DB_HOST`, `DB_PORT`, charset `utf8mb4` |
| Credentials exposure in settings source | Passwords read from env only; **not** hardcoded |
| Side effect on import | SQLite path **`mkdir` parents** if missing (`SQLITE_DIR.mkdir`) — non-destructive |

**Not performed (per Day 4 rules):** migrations, engine changes, DB resets, record inspection beyond confirming file path existence.

**Classification:** D Missing configuration only if targeting MySQL/production without filling env; current SQLite local setup is coherent.

---

## 7. Email configuration audit

| Setting | Runtime / source |
| --- | --- |
| `EMAIL_BACKEND` | `django.core.mail.backends.console.EmailBackend` |
| Selection logic | Env `DJANGO_EMAIL_BACKEND`, else console if `DEBUG` **or** `EMAIL_HOST` unset; else SMTP |
| Why console now | `EMAIL_HOST` **UNSET** in env → console backend even when audit-shell `DEBUG=False` |
| SMTP block | Only populated when backend is SMTP (`EMAIL_HOST`, `PORT`, `USER`, `PASSWORD`, `USE_TLS`) |
| `DEFAULT_FROM_EMAIL` | Default `TalentBridge AI <noreply@localhost>` (env unset) |
| `SERVER_EMAIL` | Django default `root@localhost` (not customized in settings) |
| Credentials in source | **None** hardcoded |

**App compatibility:** `ACCOUNT_EMAIL_VERIFICATION = "none"` — email verification is not required for signup. Console backend is compatible with local development; production SMTP is optional and commented in `.env.example`.

**No emails were sent during this audit.**

**Classification:** E Improvement — document that verification is off; configure SMTP before enabling email verification (future day).

---

## 8. Media configuration audit

| Setting | Finding |
| --- | --- |
| `MEDIA_ROOT` | `E:\Job POrtal\TalentBridgeAI\private_media` (exists) |
| `MEDIA_URL` | **Not set** in `settings.py`. Django normalizes missing/`''` → observed **`'/'`** |
| Storage | Default `FileSystemStorage` under `STORAGES['default']` |
| Uploads | `Profile.resume` → `resumes/`; `Company.logo` → `company_logos` under `MEDIA_ROOT` |
| Public URL route | **No** `/media/` patterns in URLconf (`MEDIAISH_ROUTES` count **0**) |
| Serving | `@login_required` views `resume_download` / `resume_preview` / `resume_delete` via `FileResponse` |

**Risk:** Unusual `MEDIA_URL='/'` could confuse any code that builds `field.url` as site-root-relative paths. Mitigated today because resumes are not publicly routed and download uses file handles, not public media URLs.

**Classification:** C Configuration inconsistency (`MEDIA_URL` implicit `/`); E explicitly set a non-served private convention or document intentional omission. **Do not** enable public `static(MEDIA_URL, …)` without a privacy review.

**No media files were read or listed for content.**

---

## 9. Static configuration audit

| Setting | Finding |
| --- | --- |
| `STATIC_URL` | `/static/` |
| `STATIC_ROOT` | `backend/legacy-django/staticfiles` |
| `STATICFILES_DIRS` | `frontend/css`, `frontend/js`, `frontend/assets/images`, `legacy-django/static` (all present) |
| `STORAGES['staticfiles']` | `StaticFilesStorage` (default) |
| Whitenoise | **Not** installed/configured |
| Portal CSS/JS serving | Custom `dev_static` on `/css/` and `/js/` (and images routes in URLconf) from frontend dirs — **independent of** `STATIC_URL` collection |
| Duplicates | Root junctions + `STATICFILES_DIRS` historically cause `collectstatic` “another file with destination path” warnings (Day 1/2). Non-blocking for `dev_static` serving. |

**Day 4 did not run `collectstatic` and did not reorganize assets.**

**Classification:** C Configuration inconsistency (dual serving: `/static/` vs `/css|/js`); E acceptable for current hybrid architecture; future cleanup is Day 12-style work, not Day 4.

---

## 10. INSTALLED_APPS inventory

Runtime list (verified import OK for third-party/local packages):

| # | Entry | Type | Module exists / import | Notes |
| --- | ---: | --- | --- | --- |
| 1 | `django.contrib.admin` | Built-in | OK | Admin site |
| 2 | `django.contrib.auth` | Built-in | OK | Users |
| 3 | `django.contrib.contenttypes` | Built-in | OK | |
| 4 | `django.contrib.sessions` | Built-in | OK | DB sessions |
| 5 | `django.contrib.messages` | Built-in | OK | |
| 6 | `django.contrib.staticfiles` | Built-in | OK | |
| 7 | `django.contrib.sites` | Built-in | OK | Required by allauth; `SITE_ID=1` |
| 8 | `allauth` | Third-party | OK (v65.22.1) | |
| 9 | `allauth.account` | Third-party | OK | |
| 10 | `allauth.socialaccount` | Third-party | OK | |
| 11 | `allauth.socialaccount.providers.google` | Third-party | OK | Provider config filled only when both OAuth env vars set |
| 12 | `jobs.apps.JobsConfig` | Local | OK | Domain app; models loaded |

**Duplicates:** None.  
**Missing apps:** None required for current boot.  
**AppConfig:** `jobs.apps.JobsConfig` correctly referenced (patches Google OAuth callback on `ready()`).  
**Migrations:** `jobs` app has migrations 0001–0014 (existence verified earlier; **not** re-applied this day).

---

## 11. Environment variable loading analysis

```text
manage.py / wsgi / asgi
    → DJANGO_SETTINGS_MODULE=config.settings
        → import config.settings
            → resolve PROJECT_ROOT
            → load_dotenv(PROJECT_ROOT / ".env")   # does not override pre-set OS env by default
            → read SECRET / DEBUG / HOSTS / DB / EMAIL / OAuth from os.environ
```

| Loader | Behavior |
| --- | --- |
| `python-dotenv` `load_dotenv` | Loads `.env` into process env for unset keys |
| `windows_manager.launcher_env()` | Copies OS env, merges parsed `.env`, **overrides** `DJANGO_ENV`/`DJANGO_DEBUG` to development/true |
| Bare `manage.py` shell | Uses `.env` + defaults; **no** launcher override → often `DEBUG=False` even if `.env` has `DJANGO_DEBUG=true` without `DJANGO_ENV` |

**Env keys presence (names only, this audit process):**

| Key | Presence |
| --- | --- |
| `DJANGO_SECRET_KEY` | SET |
| `DJANGO_DEBUG` | SET |
| `DJANGO_ENV` | UNSET (in audit process) |
| `DJANGO_ALLOWED_HOSTS` | SET |
| `DB_ENGINE` / `DB_NAME` | SET |
| `EMAIL_HOST` / `DJANGO_EMAIL_BACKEND` / `DEFAULT_FROM_EMAIL` | UNSET |
| `GOOGLE_OAUTH_CLIENT_ID` / `SECRET` | SET (values not shown) |

**Unused imports in settings:** `parse_qs`, `unquote`, `urlparse` imported but unused (hygiene only).

---

## 12. Configuration dependency map

```text
[.env / launcher env]
        │
        ▼
config.settings ──► DATABASES ──► database/TalentBridgeAI.sqlite3
        │
        ├── DEBUG ──► LivePreviewMiddleware + /__dev__/ (managed only)
        ├── SECRET_KEY ──► sessions, CSRF, cookies signing
        ├── ALLOWED_HOSTS / CSRF_TRUSTED_ORIGINS
        ├── INSTALLED_APPS ──► allauth + jobs
        ├── TEMPLATES DIRS ──► frontend/ + frontend/pages + legacy-django/templates
        ├── STATIC* ──► collectstatic /admin static; portal uses /css /js routes
        ├── MEDIA_ROOT ──► private_media + login-gated resume views
        └── EMAIL_* ──► console locally; SMTP when EMAIL_HOST set
```

Startup entrypoints that all resolve to `config.settings`:

- `backend/legacy-django/manage.py`
- `config/wsgi.py` / `config/asgi.py`
- `tools/windows_manager.py` → `manage.py runserver`
- `.vscode/start-talentbridge.ps1` → windows_manager

---

## 13. Confirmed problems and security risks

| ID | Class | Setting / area | Evidence | Impact | Safe to fix now? |
| --- | --- | --- | --- | --- | --- |
| D4-01 | C | DEBUG / `.env.example` | Example sets `DJANGO_DEBUG=true` but omits `DJANGO_ENV`; settings require both | Operators may think DEBUG is on when bare manage.py has DEBUG False | Document only (recommended); do not change live `.env` in Day 4 |
| D4-02 | C | DEBUG dual runtime | Launcher forces development DEBUG; audit/shell defaults production | Different behavior between managed server and CLI | Document; optional future split settings — not applied |
| D4-03 | C | `MEDIA_URL` | Unset → `'/'` | Misleading URL building if `FileField.url` used publicly | Recommend explicit private convention later; **do not** expose media routes now |
| D4-04 | E | No project `LOGGING` | `HAS_LOGGING False` | Weaker operational visibility | Additive later |
| D4-05 | B / E | Production `SECURE_*` | Defaults: no SSL redirect, cookies not Secure | Acceptable locally; weak if same settings used on public HTTPS without change | Do **not** enable Secure cookies locally now |
| D4-06 | E | `ACCOUNT_EMAIL_VERIFICATION=none` | Settings | Email proof not required | Product decision; future day |
| D4-07 | B | Packaging secret constant | `tools/package_release.py` verification key string in repo | Risk if that packaging path were used as real deployment | Future hardening; not rotated this day |
| D4-08 | C | Settings docstring Django 6.1 vs runtime 5.2.19 | File header vs `django.get_version()` | Confusion only | Comment cleanup later |
| D4-09 | E | Unused urllib imports | `settings.py` lines 16 | Noise | Safe cleanup later |

**No confirmed bug** that prevents the project from loading settings or passing `manage.py check`.

---

## 14. Recommended corrections (not applied)

1. Add `DJANGO_ENV=development` to `.env.example` with a short comment explaining the dual gate with `DJANGO_DEBUG`.
2. Document in README that the Windows launcher forces DEBUG on; bare CLI may differ.
3. Explicitly set `MEDIA_URL` to a non-public placeholder **or** document why it remains unset; keep resume serving login-gated.
4. Before any internet-facing deploy: set `DJANGO_ENV=production`, `DJANGO_DEBUG=false`, real `ALLOWED_HOSTS`, HTTPS-related `SECURE_*` / Secure cookies, SMTP, and persistent `DJANGO_SECRET_KEY`.
5. Add structured `LOGGING` configuration.
6. Remove unused imports; fix settings header version comment.
7. Treat `package_release.py` verification secret as non-production only (or generate ephemerally).

**No configuration changes were applied during Day 4.**

---

## 15. Tests / checks executed (actual results)

| Check | Command / method | Result |
| --- | --- | --- |
| Settings import + `django.setup()` | venv Python one-shot | **OK** |
| `manage.py check` (via `call_command('check')`) | Same process | **OK** — `System check identified no issues (0 silenced).` |
| Runtime values dump | Non-secret attributes only | Recorded in §§3–10 |
| App imports | admin, allauth*, jobs | **OK** |
| DB file exists | Path from `DATABASES['default']['NAME']` | **True** |
| Media root exists | `MEDIA_ROOT` | **True** |
| Media URL routes | URL resolver scan | **0** media routes |
| Managed server health | `windows_manager status` + HTTP login | Port **8000** LISTENING; `/login/` **200**; bridge **8001** |
| Migrations / DB writes | — | **Not run** (Day 4 forbid) |
| collectstatic | — | **Not run** |
| Email send | — | **Not run** |

---

## 16. Items requiring future action

- Day 5+ database inventory/backup (out of scope).
- Production hardening checklist (SECURE_*, hosts, SMTP).
- Optional settings package split (base/dev/prod).
- Static dual-path / junction collectstatic noise (organization day).
- Email verification policy if product requires verified addresses.

---

## 17. Final Day 4 completion status

| Requirement | Status |
| --- | --- |
| DEBUG audit | Done |
| SECRET_KEY audit (no value exposure) | Done |
| ALLOWED_HOSTS audit | Done |
| Database configuration audit | Done |
| Email configuration audit | Done |
| Media configuration audit | Done |
| Static configuration audit | Done |
| INSTALLED_APPS inventory | Done |
| Env / dependency map | Done |
| Safe verification checks | Done |
| Report written | This file |
| Config changes applied | **None** |
| Day 5 started | **No** |

### Day 4 status: **COMPLETE**

Existing project remains **safe and runnable** based on `manage.py check` (0 issues) and live HTTP health on `http://127.0.0.1:8000/` (and `:8001` bridge).
