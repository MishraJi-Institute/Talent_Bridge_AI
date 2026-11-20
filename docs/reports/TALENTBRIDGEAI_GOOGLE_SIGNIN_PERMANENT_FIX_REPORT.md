# Google Sign-In permanent fix — root cause report

Date: 2026-11-20

## Root cause

| Layer | What happens |
|--------|----------------|
| **talentbridge.qd.je** | GitHub Pages serves **static HTML only** (Actions → `site/`). |
| **Google OAuth** | Requires **Django + allauth** on a server with the client **secret**. Pages cannot finish OAuth. |
| **Symptom** | `demo-forms.js` showed a warning because **`TALENTBRIDGE_DJANGO_ORIGIN` was not baked into** the Pages build, so static signup could not redirect to the real backend. |

Architecture (unchanged, now wired correctly):

- **Marketing / browse** → GitHub Pages (`talentbridge.qd.je`)
- **Auth (Google, email, sessions)** → Django HTTPS host (`config/talentbridge_django_origin.txt` / Render)

## Fixes applied (not a warning hide)

1. **`config/talentbridge_django_origin.txt`** — committed production Django HTTPS origin (update to your live Render URL).
2. **`tools/build_static.py`** — resolves origin (env → config file); injects `<meta name="talentbridge-django-origin">` and `window.TALENTBRIDGE_DJANGO_ORIGIN` into every static page.
3. **`.github/workflows/static.yml`** — passes `vars.TALENTBRIDGE_DJANGO_ORIGIN` when set in GitHub repo variables.
4. **`frontend/js/core/demo-forms.js`** — on Pages: redirects Google to `{origin}/auth/social/google/?role=…` (real `social_login_start`); signup/email forms go to `{origin}/signup/job-seeker/` or `/login/`. **No demo session.** Local `:8000`/`:8001` unchanged (server-native OAuth).

## Files changed

- `config/talentbridge_django_origin.txt` (new)
- `tools/build_static.py`
- `.github/workflows/static.yml`
- `frontend/js/core/demo-forms.js`
- `frontend/pages/login.html` (script cache bust)

## Environment variables

| Variable | Where | Purpose |
|----------|--------|---------|
| `GOOGLE_OAUTH_CLIENT_ID` / `SECRET` | Render + local `.env` | Real Google (never in frontend) |
| `GOOGLE_OAUTH_REDIRECT_ORIGIN` | Render (auto from `RENDER_EXTERNAL_URL` if unset) | Callback host |
| `TALENTBRIDGE_DJANGO_ORIGIN` | GitHub Actions **variable** or `config/talentbridge_django_origin.txt` | Static site → Django handoff |
| `DJANGO_*` on Render | `render.yaml` + auto hosts | Production Django |

## Local startup

```text
scripts\startup\START_TALENTBRIDGEAI.bat
→ http://127.0.0.1:8000/login/
→ http://127.0.0.1:8000/signup/job-seeker/
```

Google Console (keep):

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/accounts/google/login/callback/
```

## Production

1. Deploy Django: Render Blueprint `render.yaml` → service `talentbridge-ai`.
2. Set `config/talentbridge_django_origin.txt` to `https://YOUR-SERVICE.onrender.com` (or set GitHub **variable** `TALENTBRIDGE_DJANGO_ORIGIN` — overrides file).
3. Push `main` → Pages rebuild includes origin meta → **warning no longer appears** on signup; button sends user to Django OAuth.
4. Google Console add:

```text
https://YOUR-SERVICE.onrender.com
https://YOUR-SERVICE.onrender.com/accounts/google/login/callback/
```

Optional later: point `api.talentbridge.qd.je` CNAME to Render and use that as origin.

## Tests performed (this session)

| # | Test | Result |
|---|------|--------|
| 1 | Local `/signup/job-seeker/` loads | **200** |
| 2 | Local POST Google start (`job_seeker`) | **Redirects to accounts.google.com** |
| 3 | Static build injects origin meta | **https://talentbridge-ai.onrender.com** (from config file) |
| 4 | Production Pages live OAuth end-to-end | **Blocked until Render deploy + Google Console HTTPS URIs** (service timed out here) |
| 5 | Secrets in `site/` JS | **None** (only public HTTPS origin) |

## Remaining blockers (external)

1. **Render service** must be **Live** at the URL in `talentbridge_django_origin.txt`.
2. **Google Cloud Console** must list production **origin + callback** for that HTTPS host.
3. **GitHub Actions** redeploy after origin is correct (automatic on push to `main`).

## Acceptance

- After Pages deploy with injected origin: the **old localhost warning text will not show** on normal signup; user is sent to real Django OAuth.
- **Local** real Google already works on `:8000`.
- **Production** Google completes only when Django on Render is up and Console URIs match — not a frontend-only fake.