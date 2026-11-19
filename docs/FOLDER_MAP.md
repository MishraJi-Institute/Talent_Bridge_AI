# TalentBridgeAI folder map

Date: 2026-11-18

Plain-language map of the repository after the docs reorganize. **Do not delete root junctions** — the site and tooling still use them.

```text
TalentBridgeAI/
├── README.md                 # Project overview
├── index.html                # Homepage entry (served via Django / static build)
├── .env / .env.example       # Private local settings (never commit secrets)
├── netlify.toml
│
├── frontend/                 # Public UI source
│   ├── pages/                # HTML / Django templates
│   ├── css/
│   ├── js/
│   └── assets/               # images, logos, videos
│
├── backend/
│   └── legacy-django/        # Django project (manage.py, apps, .venv)
│
├── docs/                     # Documentation only (this tree)
│   ├── START_HERE.md         # How to run locally
│   ├── README.md             # Docs index
│   ├── FOLDER_MAP.md         # This file
│   ├── audit/day1…day10/     # Daily audit reports
│   ├── audit/phase1/         # Phase 1 gate / backlog
│   ├── homepage/             # Homepage & matching showcase reports
│   ├── setup/                # Startup, OAuth, ports
│   ├── troubleshooting/      # Fixes & remaining issues
│   ├── reports/              # QA, delivery, PDFs, inventories
│   ├── development/          # Plans & progress
│   ├── architecture/
│   ├── guides/
│   ├── installation/
│   ├── homepage-redesign/
│   └── evidence/
│
├── scripts/                  # install / startup / maintenance / backup / diagnostics
├── tools/                    # Windows manager, packaging helpers
├── database/                 # SQLite (+ helpers)
├── private_media/            # Uploads (local)
├── backups/
├── logs/
├── releases/                 # Portable ZIP artifacts
├── site/                     # Generated static preview (optional port 5500)
├── tests/
│
└── Junctions (compatibility — leave in place)
    ├── css        → frontend/css
    ├── js         → frontend/js
    ├── images     → frontend/assets/images
    ├── pages      → frontend/pages
    └── legacy-django → backend/legacy-django
```

## What belongs where

| Need | Look in |
|------|---------|
| Run the site | `docs/START_HERE.md`, `scripts/startup/` |
| Change homepage UI | `frontend/` (+ root `index.html` as needed) |
| Change Django / auth / DB | `backend/legacy-django/` |
| Read day audits | `docs/audit/dayN/` |
| Homepage design notes | `docs/homepage/` |
| OAuth / ports | `docs/setup/` |

## Intentionally not moved

- Frontend/backend source trees
- Database and private media paths
- Root junctions used by URL space and build tooling
