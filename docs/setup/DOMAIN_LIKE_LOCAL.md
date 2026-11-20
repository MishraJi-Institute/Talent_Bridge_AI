# Domain pe local jaisa kaam (database + login + jobs)

GitHub Pages (`talentbridge.qd.je`) **database nahi chala sakta**. Local jaisa kaam domain par tabhi hota hai jab **Django + cloud database** chale.

## Architecture (recommended)

| URL | Kya hai |
|-----|---------|
| `https://talentbridge.qd.je` | GitHub Pages — marketing / static preview |
| `https://app.talentbridge.qd.je` | **Live Django** — login, Google, jobs, **Postgres DB** |

Local PC par: SQLite `database/TalentBridgeAI.sqlite3`  
Live server par: **alag** Postgres (Render) — same tables (migrations), alag file path.

## Ek baar setup (managed by project)

1. Run `scripts\deploy\SETUP_DOMAIN_LIKE_LOCAL.bat` (opens Render Blueprint + checklist).
2. Render: Blueprint from `render.yaml` → service `talentbridge-ai` + database `talentbridge-db`.
3. DNS at your domain provider:

   ```text
   app.talentbridge.qd.je  CNAME  talentbridge-ai.onrender.com
   ```

4. Render → service → Custom Domains → add `app.talentbridge.qd.je`.
5. Google Cloud: add origins/callback for `https://app.talentbridge.qd.je`.
6. Push `main` → GitHub Pages rebuild; static Google button → `app.talentbridge.qd.je`.

## Local data live par copy (optional)

Default: live DB khali + migrations (fresh start).  
Local rows copy karne ke liye (one-time):

```text
cd backend\legacy-django
..\.venv\Scripts\python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > ..\..\backups\local_seed.json
```

Then on live (Render shell): `loaddata` from uploaded file — only when you understand the risk.

Daily routine: local = `START_TALENTBRIDGEAI.bat`; live data = Postgres on Render (automatic migrate on deploy).