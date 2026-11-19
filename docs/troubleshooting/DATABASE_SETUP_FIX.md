# Database setup

The project now starts with SQLite by default, so a missing MySQL password will
not prevent Django from starting.

## Run locally with SQLite (default)
1. Copy `.env.example` to `.env` in the project root.
2. From `legacy-django`, run:
   `python manage.py migrate`
   `python manage.py runserver`

## Optional MySQL
1. Create the database `talentbridge_db` in your local MySQL server.
2. In the project-root `.env`, set `DB_ENGINE=mysql`.
3. Set `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT` to match
   your own MySQL installation. Do not share your password.
4. Run `python manage.py migrate`, then `python manage.py runserver`.

Do not run the HTML pages through VS Code Live Server when testing Django forms.
Open the Django URL shown by `runserver` (normally http://127.0.0.1:8000/).
