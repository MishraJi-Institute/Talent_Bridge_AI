# Tests layout

- Backend Django tests remain inside `backend/legacy-django/jobs/` (Django discovery). Do not duplicate them here.
- `tests/frontend/`: future UI/link checks.
- `tests/integration/`: future cross-layer checks.
- Root `_check_links.py` remains a repo-level link checker.
