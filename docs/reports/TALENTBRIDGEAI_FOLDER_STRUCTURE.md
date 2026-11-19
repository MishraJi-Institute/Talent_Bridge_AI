# TalentBridgeAI — Folder Structure

Date: 2026-11-18 (resume completion)

```text
TalentBridgeAI/
├── frontend/
│   ├── pages/                 # 65 HTML page sources
│   ├── css/
│   │   ├── base/              # global / foundation
│   │   ├── components/        # shared UI chrome
│   │   ├── layouts/           # reserved
│   │   ├── pages/             # page-specific styles (incl. homepage)
│   │   ├── responsive/        # responsive fixes
│   │   └── dashboard/         # dashboard + jerry-guide CSS
│   ├── js/
│   │   ├── core/
│   │   ├── components/        # reserved
│   │   ├── authentication/
│   │   ├── jobs/
│   │   ├── dashboards/        # reserved (live scripts under dashboard/)
│   │   ├── dashboard/         # existing dashboard scripts
│   │   └── notifications/     # reserved
│   └── assets/
│       ├── images/
│       ├── logos/
│       ├── icons/
│       └── videos/
├── backend/
│   └── legacy-django/         # manage.py, config/, jobs/, templates/, .venv
├── docs/
│   ├── architecture/
│   ├── installation/
│   ├── setup/
│   ├── troubleshooting/
│   ├── reports/
│   └── development/
├── scripts/
│   ├── install/
│   ├── startup/
│   ├── shutdown/
│   ├── maintenance/
│   ├── backup/
│   └── diagnostics/
├── tests/                     # pointers; Django tests stay in jobs/
├── database/                  # SQLite (unchanged)
├── private_media/             # uploads (unchanged)
├── backups/
├── tools/
├── site/                      # generated static preview
├── index.html                 # homepage entry (repo root)
└── root *.bat wrappers        # call into scripts/
```

Compatibility junctions at repo root: `pages`, `css`, `js`, `images`, `logo`, `videos`, `legacy-django`.
