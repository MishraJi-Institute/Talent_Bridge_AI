# Real Google OAuth (no demo login)

GitHub Pages is **static**. It cannot store the Google client secret or complete the OAuth code exchange. Real Google sign-in always runs on **Django**.

## Local (this folder) — works now

1. Start Django: `scripts/startup/START_TALENTBRIDGEAI.bat` (or your usual launcher).
2. Open **http://127.0.0.1:8000/login/**
3. Click **Continue with Google** — this is the real allauth flow.
4. Google Cloud Console must allow:

```text
Origin:   http://127.0.0.1:8000
Callback: http://127.0.0.1:8000/accounts/google/login/callback/
```

Keep `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` in the private root `.env` only.

## Live site (talentbridge.qd.je) — needs a Django host

To use real Google on the public domain:

1. Deploy Django (Render blueprint: `render.yaml` in the repo root).
2. Set env on the host: `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, Google secrets, and  
   `GOOGLE_OAUTH_REDIRECT_ORIGIN=https://YOUR-DJANGO-HOST`.
3. In Google Cloud Console add:

```text
Origin:   https://YOUR-DJANGO-HOST
Callback: https://YOUR-DJANGO-HOST/accounts/google/login/callback/
```

4. Optional: point `talentbridge.qd.je` DNS at that Django host (instead of GitHub Pages), **or** keep Pages and set  
   `TALENTBRIDGE_DJANGO_ORIGIN=https://YOUR-DJANGO-HOST` when building Pages so the static Google button sends users to real Django OAuth.

There is **no demo Google login** anymore. Static Pages alone will not invent a signed-in user.
