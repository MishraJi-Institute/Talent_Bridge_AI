# Deploy Django on Render for real Google OAuth

GitHub Pages stays optional for static browsing. **Real Google login runs only on Django.**

## 1) Deploy

1. Open [Render Dashboard](https://dashboard.render.com/) and sign in with GitHub.
2. **New** → **Blueprint** → select `MishraJi-Institute/Talent_Bridge_AI`.
3. Apply `render.yaml`.
4. In the service **Environment** tab set (use your real values; never commit them):

```text
DJANGO_ALLOWED_HOSTS=talentbridge-ai.onrender.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://talentbridge-ai.onrender.com
GOOGLE_OAUTH_CLIENT_ID=<from Google Cloud Console>
GOOGLE_OAUTH_CLIENT_SECRET=<from Google Cloud Console>
GOOGLE_OAUTH_REDIRECT_ORIGIN=https://talentbridge-ai.onrender.com
```

Replace `talentbridge-ai.onrender.com` with the hostname Render shows after the first deploy.

5. Deploy / wait until the service is **Live**.
6. Open `https://YOUR-APP.onrender.com/login/` and use **Continue with Google**.

## 2) Google Cloud Console

For the Web OAuth client, add:

```text
Authorized JavaScript origin:
  https://YOUR-APP.onrender.com

Authorized redirect URI:
  https://YOUR-APP.onrender.com/accounts/google/login/callback/
```

Keep the local entries too if you still develop on this folder:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/accounts/google/login/callback/
```

## 3) Optional: put talentbridge.qd.je on Django

To make the public domain serve real OAuth (instead of static Pages):

1. In Render → Custom Domains → add `talentbridge.qd.je`.
2. At DigitalPlat DNS, point `@` / `www` as Render instructs (usually CNAME/ALIAS to the Render host).
3. Update env:

```text
DJANGO_ALLOWED_HOSTS=talentbridge.qd.je,www.talentbridge.qd.je,YOUR-APP.onrender.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://talentbridge.qd.je,https://www.talentbridge.qd.je,https://YOUR-APP.onrender.com
GOOGLE_OAUTH_REDIRECT_ORIGIN=https://talentbridge.qd.je
```

4. Add the same HTTPS origin + callback in Google Cloud Console.
5. Redeploy, then run (Render shell or release command already calls it):

```text
python manage.py prepare_deploy_auth
```

## 4) Local folder (unchanged)

Real Google on this machine remains:

```text
http://127.0.0.1:8000/login/
```

## Notes

- Free Render disks are ephemeral; SQLite data can reset on redeploy. For lasting users, add Render Postgres later.
- Do not put Google secrets in the repo or in frontend JavaScript.
