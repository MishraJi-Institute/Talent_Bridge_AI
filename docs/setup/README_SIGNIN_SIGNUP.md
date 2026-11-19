# Sign-in / Sign-up — important

Use the Django site at **http://127.0.0.1:8000/** for real registration and login.

- VS Code **Go Live** opens a static preview (usually port 5500). It cannot create accounts or authenticate users.
- If you submit login or signup in the static preview, it forwards you to the matching Django form on port 8000. Re-enter the details there.
- On Django, use `/login/`, `/pages/jobseeker-signup.html`, and `/pages/company-signup.html`.
- Keep the Django terminal running while testing.
- Google sign-in and signup require your own OAuth Client ID and Secret in the root `.env`. Email/password sign-in does not need Google credentials.

The signup JavaScript no longer blocks valid submissions with the old preview alert. Django validates the fields and password on the server.

## Enable Google sign-in and signup

Follow [GOOGLE_OAUTH_SETUP.md](GOOGLE_OAUTH_SETUP.md) for the complete
Google Cloud Console setup, the verified Django callback URL, local credential
configuration, and troubleshooting. Use the root `.env` only; never commit or
share it.

The current local `.env` does not contain Google OAuth credentials. Therefore
the Google buttons are intentionally disabled until both required values are
configured. Email/password authentication remains available.
