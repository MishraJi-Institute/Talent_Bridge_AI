# Google OAuth on GitHub Pages only (no Render)

Live domain uses **Google Identity Services** with your **public Client ID** baked in at build time. The **client secret never** goes to GitHub Pages.

## One-time setup

1. Google Cloud → same OAuth client as local.
2. **Authorized JavaScript origins:**
   - `https://talentbridge.qd.je`
   - `https://www.talentbridge.qd.je`
   - `http://127.0.0.1:8000` (local Django)
3. GitHub repo → **Settings → Secrets and variables → Actions → Variables**:
   - `GOOGLE_OAUTH_CLIENT_ID` = your client ID (not the secret)
4. Push `main` → Actions rebuilds Pages.

## Local vs live

| | Local `127.0.0.1:8000` | Live `talentbridge.qd.je` |
|--|------------------------|---------------------------|
| Engine | Django + SQLite | Static HTML |
| Google | Full allauth + secret in `.env` | Browser sign-in (GIS) |
| Jobs / DB save | Yes | Preview only on Pages* |

\* For employer/job database workflows on the public site, users still need the Django app locally, or you would need a server later (you chose not to use Render).

## Sync workflow

Edit code → commit → `GITHUB_DOMAIN_SYNC.bat` or push → domain updates in a few minutes.