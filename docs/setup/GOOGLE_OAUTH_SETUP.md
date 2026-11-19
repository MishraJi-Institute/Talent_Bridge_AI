# Google OAuth setup for TalentBridgeAI

## Live verification update — 13 November 2026

The local Django process reports both OAuth settings loaded without displaying
their values. The Google provider is configured; one Google `SocialApp` is
linked to the active site and matches the loaded client. Django resolves the
callback to `/accounts/google/login/callback/`.

Two user-authorized Google sign-ins and consent flows completed. Sanitized
server-log checks show two successful callback redirects; after each,
`/dashboard/` redirected to `/pages/dashboard/jdashboard.html` (200). A
`POST /logout/` returned 302 after each session, and a later dashboard request
redirected to `/login/`, confirming logout and subsequent login. The current
browser is logged out. Read-only checks found the user count remained two and
two Google SocialAccounts are linked to two Job Seeker profiles; no identities
or credential values were displayed. Existing-account authentication and role
routing are verified; first-time Google signup was not exercised. Google Cloud
Console origin/test-user settings were not directly inspected. The older
12 November `invalid_client` diagnosis below is historical and superseded.

## Diagnosis on 12 November 2026 — BLOCKED

Google returned `Error 401: invalid_client` and “The OAuth client was not found.” The local configuration was checked without printing credential values.

- One client ID value is loaded. The launcher value and the Django value match. There is one Google SocialApp and it matches that value. It is linked to site `127.0.0.1:8000`.
- The loaded client ID is 36 characters, contains no dot, and does not end with `.apps.googleusercontent.com`. That is not a Google OAuth client ID, so Google cannot find a client for it.
- The secret is present, is 35 characters, and has the normal Google secret prefix. The two values do not appear to be swapped.
- The required redirect remains `http://127.0.0.1:8000/accounts/google/login/callback/`.
- Google Login is not complete. Consent was not accepted because Google rejected the client.

Replace `GOOGLE_OAUTH_CLIENT_ID` in the private `.env` with the Web client ID from Google Cloud Console. It must end with `.apps.googleusercontent.com`. Keep the existing secret if it belongs to that same client. Then run `RESTART_TALENTBRIDGEAI.bat`. Do not paste the values into chat.

## Current status

The Django application already has a server-side Google OpenID Connect flow
implemented with django-allauth. OAuth credentials are private local
configuration and must not be copied into source, reports, or chat. Use
`CONNECT_GOOGLE_OAUTH.bat` to verify that Django can load them without printing
their values.

The real callback route was resolved from the running Django URL configuration:

```text
http://127.0.0.1:8000/accounts/google/login/callback/
```

The local OAuth start route is `/auth/social/google/`. Use the Django website at
`http://127.0.0.1:8000/`, not the static VS Code Go Live preview (usually port
5500). OAuth start is a CSRF-protected POST; allauth manages the authorization
state, callback, token exchange, and identity validation.

## Google Cloud Console configuration

1. Sign in to [Google Cloud Console](https://console.cloud.google.com/) and
   create or select the project that will own the OAuth client.
2. Configure the OAuth consent/branding screen. Choose **Internal** only if
   access should be limited to users in your Google Workspace organization;
   otherwise choose **External**. If the external app is in **Testing**, add
   each account you will use under the test-user/audience settings.
3. Use the scopes this project requests: `openid`, `email`, and `profile`.
   They provide identity, email, and basic profile information. This code does
   not request Drive, Calendar, or other Google API data; no separate Google
   API needs to be enabled just for this login flow.
4. Create an OAuth client with application type **Web application**.
5. Add the authorized JavaScript origin:

   ```text
   http://127.0.0.1:8000
   ```

   If you also open the site as `http://localhost:8000`, add that origin too.
   The current application uses a server-side authorization-code flow rather
   than a Google JavaScript SDK; the origin must still match the local browser
   origin if listed in the web client.
6. Add the exact authorized redirect URI:

   ```text
   http://127.0.0.1:8000/accounts/google/login/callback/
   ```

   If using `localhost`, add its exact matching URI as well:

   ```text
   http://localhost:8000/accounts/google/login/callback/
   ```

   Google requires an exact match, including scheme, host, port, path, and
   trailing slash. Do not register the port-5500 static-preview URL.
7. Copy the Web Client ID and Client Secret. Do not put either value in source
   code, documentation, chat, or a ZIP file.

Google's official references:

- [OAuth 2.0 for Web Server Applications](https://developers.google.com/identity/protocols/oauth2/web-server)
- [OpenID Connect](https://developers.google.com/identity/openid-connect/openid-connect)

## Store credentials locally

From the project root, run the interactive launcher:

```powershell
.\CONNECT_GOOGLE_OAUTH.bat
```

The script locates the project root from its own path, prompts for the Client
ID, and accepts the Client Secret through hidden input. It updates only the two
Google OAuth entries in the private root `.env`, verifies both settings through
the Django application, synchronizes the django-allauth Google app, and runs
Django's system checks. It then restarts the managed Django server and waits
for the HTTP health check before startup is reported successful. The `.env`
file is ignored by Git and must stay private. To configure without restarting,
run `.\CONNECT_GOOGLE_OAUTH.ps1 -NoServer`, then run
`STOP_TALENTBRIDGEAI.bat` and `START_TALENTBRIDGEAI.bat`.

The reusable Django configuration check is:

```powershell
legacy-django\.venv\Scripts\python.exe legacy-django\manage.py check_google_oauth
```

It reports only whether Django loaded each value, never their contents. Django
loads settings when a process starts, so refreshing a browser tab does not
apply `.env` changes to an already-running server. Never set only one
variable, commit `.env`, or share its contents.

The health check confirms that both values are present in Django settings; it
does not validate that the OAuth client is active or correctly configured in
Google Cloud. A real Google authorization and callback test is still required
to verify those settings.

Start or restart the local Django server after configuring credentials:

```text
START_TALENTBRIDGEAI.bat
```

Then open `http://127.0.0.1:8000/login/`. The Google button becomes available
only when both credentials are loaded. The missing-configuration notice is
intentional and should not be hidden as a substitute for setup.

## Test the configured flow

Use an account permitted by the consent-screen audience/test-user settings.

1. On `/login/`, select **Continue with Google**, choose an account, and approve
   the requested basic identity scopes.
2. Confirm Google returns to the callback URL above. A first-time user is sent
   to TalentBridgeAI's account-completion form to choose a role. Employer
   accounts require a company name and remain pending approval.
3. Sign out with the site's logout control, then test an existing account.
   A verified Google email that matches an existing local email can authenticate
   that account and be connected; allauth rejects unverified provider email for
   email-based account matching.
4. Test **Cancel** at Google's account/consent screen and confirm the user is
   returned to a handled cancellation page without being logged in.
5. Repeat from `/pages/jobseeker-signup.html` and
   `/pages/company-signup.html` to verify the signup role is retained.

Do not treat the automated tests with placeholder credentials as a successful
Google login. A real login requires the user's valid Cloud client, an allowed
Google test account, and an interactive browser session.

## Production setup

For production, register the production site's exact HTTPS origin and callback
with Google. The callback pattern is:

```text
https://<your-production-domain>/accounts/google/login/callback/
```

Replace the placeholder only with the actual deployment domain. Configure
`GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` through the hosting
platform's secret/environment settings, not a committed `.env`. Ensure
`DJANGO_ALLOWED_HOSTS`, HTTPS/proxy settings, and any required CSRF trusted
origins match the deployed site. Never enable Django DEBUG or development
autoreload in production.

## Common failures

- **Google button remains disabled:** both credentials were not loaded by the
  running Django process. Check the root `.env` locally without sharing it, then
  restart Django.
- **`redirect_uri_mismatch`:** compare the callback shown above character for
  character with the Web Client's authorized redirect URI.
- **Access blocked / app not verified:** check consent-screen audience and add
  the account as a test user while the app is in Testing. Complete Google's
  verification process if required for a public production audience.
- **Cancelled or invalid callback:** allauth handles cancellation and
  authentication errors. Check the Django server log for the detailed
  application-side error; do not copy credentials or tokens into reports.
- **Email/password login still works:** Google credentials are independent of
  the existing local password flow.
