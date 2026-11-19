# TalentBridgeAI — File Inventory

Date: 2026-11-18 (resume completion)

## Prior work resumed

Yesterday’s Step 1 move into `frontend/`, `backend/`, `docs/`, `scripts/` with root junctions was preserved. This resume completed CSS/JS subfolder organization, homepage elevation, remaining script/doc folders, and verification.

## Counts (canonical sources)

| Area | Count | Location |
| --- | ---: | --- |
| HTML pages | 65 | `frontend/pages/` (+ root `index.html`, `404.html`) |
| CSS files | 42+ | `frontend/css/` (`base` 6, `components` 10, `pages` 16 incl. elevate, `responsive` 2, `dashboard` 7+) |
| JS files | 26+ | `frontend/js/` (`core` 10 incl. hero network, `authentication` 4, `jobs` 5, `dashboard` 7+) |
| Images | 19 | `frontend/assets/images/` |
| Django app files | ~94 under `jobs/` | `backend/legacy-django/` |
| Docs | 93 | `docs/` |
| Scripts | 34 | `scripts/` |

## Compatibility junctions (not duplicates)

`pages`, `css`, `js`, `images`, `logo`, `videos`, `legacy-django` → canonical trees under `frontend/` / `backend/`.

## Preserved (never reset)

- `.env` (not opened for reports)
- `database/`
- `private_media/`
- migration history `0001`–`0014`
- `.venv` under `backend/legacy-django/`

## Git

`git` was not available on PATH in this environment; no git status captured.
