# Automatic Render setup (minimal manual steps)

Most settings are now automatic in code:

- `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` auto-include Render hostname + `talentbridge.qd.je`
- `GOOGLE_OAUTH_REDIRECT_ORIGIN` auto-uses `RENDER_EXTERNAL_URL` when unset
- Start script runs migrate + `prepare_deploy_auth` + gunicorn

## One-time human steps (cannot be skipped by code)

1. **Render account** → Blueprint → connect `Talent_Bridge_AI` (uses `render.yaml`).
2. Create a **Render API Key** (Account Settings → API Keys).
3. In PowerShell from the project folder:

```powershell
$env:RENDER_API_KEY = 'rnd_...'   # paste your key once in this terminal
powershell -ExecutionPolicy Bypass -File scripts\deploy\SYNC_GOOGLE_SECRETS_TO_RENDER.ps1
```

This copies Google ID/secret from local `.env` into Render and redeploys.

4. **Google Cloud Console** (one time) add the Render callback:

```text
https://YOUR-APP.onrender.com
https://YOUR-APP.onrender.com/accounts/google/login/callback/
```

After that, real Google works at `https://YOUR-APP.onrender.com/login/`.

Local folder real Google remains: `http://127.0.0.1:8000/login/`.
