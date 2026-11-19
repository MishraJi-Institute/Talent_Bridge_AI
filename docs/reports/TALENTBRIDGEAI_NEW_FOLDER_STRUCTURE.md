# TalentBridgeAI — New Folder Structure (Step 1)

Date: 2026-11-18

## Adopted layout

```text
TalentBridgeAI/
├── frontend/
│   ├── pages/                 # HTML sources (Django templates)
│   ├── css/
│   ├── js/
│   ├── assets/
│   │   ├── images/
│   │   ├── logos/
│   │   ├── icons/             # reserved
│   │   └── videos/
│   └── README.md
├── backend/
│   ├── legacy-django/         # manage.py, config/, jobs/, templates/, .venv
│   └── README.md
├── docs/
│   ├── architecture/
│   ├── setup/
│   ├── troubleshooting/
│   ├── reports/
│   └── development/
├── scripts/
│   ├── install/
│   ├── startup/
│   ├── maintenance/
│   ├── backup/
│   ├── diagnostics/
│   └── README.md
├── tests/
│   ├── frontend/              # reserved (no duplicate Django tests)
│   ├── backend/               # reserved pointer only
│   ├── integration/
│   └── README.md              # points to jobs/ tests
├── assets/                    # reserved shared packaging slot (no duplicate media)
├── database/                  # SQLite + SQL helpers (unchanged location)
├── private_media/             # uploads (unchanged)
├── backups/
├── tools/
├── site/                      # generated static preview
├── index.html                 # homepage entry (unchanged location)
├── 404.html
├── .env / .env.example
└── root *.bat wrappers        # call into scripts/
```

## Design decisions (safety)

1. **Django tests stay in `backend/legacy-django/jobs/`** — moving them would break `manage.py test jobs`.
2. **URL space unchanged** — browsers still request `/css/`, `/js/`, `/images/`, `/pages/`.
3. **Junctions** preserve old relative tooling paths and `build_static.py` publish layout.
4. **Repo-root detection** in `settings.py` / `urls.py` supports `backend/legacy-django` after `Path.resolve()`.
5. **Homepage not redesigned** during organization.

## What was intentionally not flattened

- CSS/JS were not split into many subfolders (base/layout/components/…) in this pass — that would require mass HTML link edits and risk homepage regressions. Physical files live under `frontend/css` and `frontend/js` with existing names.
- Empty `assets/` and `frontend/assets/icons/` reserved for future use without duplicating images.
