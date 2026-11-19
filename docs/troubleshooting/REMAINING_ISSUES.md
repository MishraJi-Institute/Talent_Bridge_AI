# TalentBridgeAI remaining issues and external requirements

Updated: 2026-11-12, after the foundation repair.

## Current OAuth checkpoint — 13 November 2026

The current Django process loads both private OAuth values; the provider is
configured and its single SocialApp is linked to the active site and matches
the configured client. Two private Google sign-ins completed, with the second
after logout: both callbacks returned 302 and both protected dashboard routes
reached the Job Seeker dashboard. Each POST logout returned 302, and a later
dashboard request redirected to `/login/`. No credential values or account
identities are recorded here. First-time Google signup and direct Google Cloud
Console configuration review remain unverified.

## Google OAuth

The Django route, adapter, and local provider sync are in place. Both
`GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` are present in the
private `.env`. Their values are not recorded here.

A running server keeps the environment it was started with. After any `.env`
change, use `RESTART_TALENTBRIDGEAI.bat` and leave that window open. Do not
treat an enabled Google button as proof that sign-in works.

## What to verify in Google Cloud Console

Open the OAuth client used by this project and confirm all of the following:

1. Application type is **Web application**.
2. Authorized JavaScript origin is `http://127.0.0.1:8000`.
3. Authorized redirect URI is exactly
   `http://127.0.0.1:8000/accounts/google/login/callback/`.
4. If the consent screen is in testing, the Google account you use is listed
   as a test user.
5. The consent screen is allowed to request the openid, email, and profile
   scopes.

Then, in a browser, complete one new-account sign-up and one existing-account
sign-in, including Cancel. Those live consent steps have not been completed
in this repair.

## Administrator account

The local database had no superuser when this repair started. No account was
created and no password was reset. Run `CREATE_SUPERUSER.bat` in a terminal
and enter the username and password there.

## Still out of scope

- AI resume parsing and AI resume generation are not implemented.
- Job seeker and employer dashboards are still partly browser-local demos.
- Startup does not insert demo data.
- Automatic Windows logon startup was not enabled.
- Production hostname, HTTPS, and SMTP are not configured. Password reset uses
  the console email backend until SMTP is set.

## Evidence limits

This folder is not a Git repository. Do not describe a Google consent flow or
an admin password login as passed until those actions are performed.
