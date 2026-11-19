# TalentBridgeAI — File Move Log (Finish Pass)

Date: 2026-11-18T08:18:03
Backup: `backups/structure_finish_20261118_081801/`

## Moves

| Original | New | Reason |
| --- | --- | --- |
| `START_HERE.md` | `docs/START_HERE.md` | Documentation belongs under docs/ |
| `TALENTBRIDGEAI_PROJECT_PROGRESS.md` | `docs/reports/TALENTBRIDGEAI_PROJECT_PROGRESS.md` | Docs report (merged into docs/reports) |
| `bootstrap_env.py` | `tools/bootstrap_env.py` | Env bootstrap helper belongs in tools/ |
| `build_static.py` | `tools/build_static.py` | Static site builder belongs in tools/ |
| `_check_links.py` | `tools/_check_links.py` | Link checker belongs in tools/ |
| `index.html` | `frontend/index.html` | Homepage HTML with other frontend sources |
| `404.html` | `frontend/pages/404.html` | Error page with other frontend HTML pages |
| `design-references` | `docs/design-references` | Design reference assets under docs/ |
| `assets/README.md` | `frontend/assets/ROOT_ASSETS_README.md` | Preserve assets README under frontend/assets |
| `START_TALENTBRIDGEAI.bat` | `scripts/startup/START_TALENTBRIDGEAI.ROOT_WRAPPER.bat` | Archive root BAT wrapper under scripts/; use scripts/startup|shutdown |
| `STOP_TALENTBRIDGEAI.bat` | `scripts/shutdown/STOP_TALENTBRIDGEAI.ROOT_WRAPPER.bat` | Archive root BAT wrapper under scripts/; use scripts/startup|shutdown |
| `RESTART_TALENTBRIDGEAI.bat` | `scripts/startup/RESTART_TALENTBRIDGEAI.ROOT_WRAPPER.bat` | Archive root BAT wrapper under scripts/; use scripts/startup|shutdown |

## Notes

- collision backup: E:\Job POrtal\TalentBridgeAI\frontend\pages\404.html -> E:\Job POrtal\TalentBridgeAI\backups\structure_finish_20261118_081801\collisions\frontend\pages\404.html
- removed empty root assets/ stub (content lives in frontend/assets)
- wrote docs/setup/HOW_TO_START.md
- updated settings.py TEMPLATE_DIRS + STATICFILES_DIRS
- updated urls.py index.html document_root -> FRONTEND_ROOT
- updated views.page_file pages_root -> FRONTEND_ROOT/pages
- updated jobs/tests.py pages_root
- updated tools/build_static.py for frontend/ layout
- updated netlify.toml build command
- script files patched: 10
- removed junction: css
- removed junction: js
- removed junction: pages
- removed junction: images
- removed junction: logo
- removed junction: videos
- removed junction: legacy-django

## Counts (approx., excluding venv/staticfiles/backups/releases)

- HTML (frontend + Django templates): **78**
- CSS (frontend/css): **43**
- JavaScript (frontend/js): **26**
- Documentation (docs + root README): **86**
- Scripts/tools: **52**
- Files still in root: **8** → `.env, .env.example, .gitattributes, .gitignore, .talentbridge_django.port, README.md, TalentBridgeAI.code-workspace, netlify.toml`

## Root directories after pass

`.github, .vscode, backend, backups, database, docs, frontend, logs, private_media, releases, scripts, site, tests, tools`

## Intentionally kept in root

| File | Why |
| --- | --- |
| `.env` / `.env.example` | Secrets / env template must stay at repo root for Django loader |
| `.gitignore` / `.gitattributes` | Git configuration |
| `README.md` | Standard project entry documentation |
| `netlify.toml` | Netlify expects repo-root config |
| `TalentBridgeAI.code-workspace` | VS Code multi-root workspace file |
| `.talentbridge_django.pid` / `.port` | Runtime locks written by startup manager |

## References updated

- `backend/legacy-django/config/settings.py` (TEMPLATE_DIRS, STATICFILES_DIRS)
- `backend/legacy-django/config/urls.py` (index.html from FRONTEND_ROOT)
- `backend/legacy-django/jobs/views.py` (page_file pages root)
- `backend/legacy-django/jobs/tests.py`
- `tools/build_static.py`, `netlify.toml`
- `scripts/**` paths → `backend\legacy-django`
- `.vscode/launch.json`

## Verification

See companion section filled by the verification runner.

## Verification (2026-11-18 continue)

- Django system check: OK
- Server restarted at http://127.0.0.1:8001/
- Fixed page_view to resolve templates from FRONTEND_ROOT/pages (was 404 after junction removal)
- Restored compatibility junctions: pages, css, js, images, legacy-django
- Named routes verified 200: /, /login/, /jobs/, /pricing/, /employer/, /jobseaker/, /about/
- PageRoutingTests (named pages + public info): OK
- Homepage CSS restored (hero13): premium-system no longer overrides hero h1; layout lock softened
- Broken CSS image paths fixed to /images/...
- Homepage asset links switched to absolute /css /js /images

Root files kept: .env, .env.example, .gitignore, .gitattributes, README.md, netlify.toml, TalentBridgeAI.code-workspace, runtime .port/.pid
