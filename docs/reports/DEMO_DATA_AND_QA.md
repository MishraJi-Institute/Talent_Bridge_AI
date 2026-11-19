# Demo data and quality notes

- The Django development launcher runs with `DEBUG=True` for local development.
- When there are no active jobs from approved employers, the jobs and recommendations
  pages can display the built-in sample roles from `legacy-django/jobs/views.py`.
- These sample roles are presentation-only. They are not inserted into the SQLite
  database, cannot be applied to, and are not presented as real employer vacancies.
- Existing user, profile, company, and database records are preserved.
- The Home page now exposes the existing Page Directory. Its groups link to the
  HTML pages included in this project.
- Footer links that were previously inert text now open their corresponding pages.
- `START_TALENTBRIDGEAI.bat` is the supported local server launcher. It runs Django
  checks and HTTP health checks before opening the browser. If port 8000 is already
  owned by another process, the launcher reports that conflict rather than killing
  an unrelated process.
- Google OAuth, SMTP email delivery, and production hosting still require the
  project owner's external credentials and deployment configuration.
