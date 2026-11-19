# TalentBridgeAI complete project and change report

**Report date:** 2026-11-13  
**Project root:** `E:\Job Portal\TalentBridgeAI`  
**Status:** Local test suite passes; two live Google sign-ins, including a
login after logout, are verified.

## Current status addendum — 13 November 2026

The 12 November statements below about empty OAuth settings are a historical
snapshot and are superseded. The current Django process reports both private
settings present; the Google provider is configured, its single SocialApp is
linked to the active site and matches the configured client, and the callback
resolves correctly. Two user-authorized flows completed: both callbacks
redirected successfully and the protected route reached the Job Seeker
dashboard; logout cleared each session, and a later dashboard request
redirected to login. First-time Google signup and Google Cloud Console
configuration have not been inspected.

The Salary Calculator is now a server-validated page for gross pay conversions
from annual to common pay periods and hourly estimates. Privacy Settings and
Get Discovered now provide a default-private opt-in for approved employers;
discovery excludes contact details and resumes. Saved Jobs keeps fictional
preview rows separate from live account data. Access Denied returns HTTP 403,
and the staff dashboard links to searchable profile, saved-job, notification,
and interview admin lists. The additive migration
preserved aggregate account counts and passed SQLite integrity validation. The
latest full Django suite passed 119 tests, and the local link checker passed
for 62 HTML and 35 CSS files.

## Current executive summary

TalentBridgeAI is a Django application with frontend page, CSS, JavaScript, and
image sources at the project root. Django configuration and the `jobs` app are
under `legacy-django/`. The current checkpoint has 119 passing Django tests,
passing system and migration checks, and no broken local HTML/CSS references
across 62 HTML and 35 CSS files. Django on port 8000 has one listener; the
homepage, login, and health route return HTTP 200, and the health state is
`ok`. Port 5500 remains a separate static preview.

Existing-account Google sign-in, callback/session creation, dashboard redirect,
logout, and subsequent login were verified twice; first-time signup and direct
Google Cloud Console review remain unverified. Resume upload and library
workflows support PDF/DOC/DOCX up to 5 MB. AI resume generation remains
unavailable until an AI provider is privately configured. The page inventory
currently has 53 workflows: 12 complete, 39 partial, and 2 not implemented.

## Project overview and organization

| Area | Current location / responsibility |
|---|---|
| Django project and settings | `legacy-django/config/` |
| Django application, views, models, tests, migrations | `legacy-django/jobs/` |
| Django-only templates | `legacy-django/templates/` |
| Django-routed source pages | `pages/` |
| Frontend styles, scripts, and images | `css/`, `js/`, `images/` |
| Local database and SQL setup | `database/` |
| Documentation | `docs/` |
| Windows lifecycle and maintenance tools | `tools/` and root `.bat` files |
| Generated static preview | `site/` (not the editable source tree) |

No folder reorganization or existing file deletion was made in this task.
The previously generated layout and structure-audit documentation remain
available in `PROJECT_LAYOUT.md` and `PROJECT_STRUCTURE_REPORT.md`.

## Historical OAuth setup snapshot — 12 November 2026

The login page displays a warning that Google sign-in is unavailable. Runtime
inspection of the private `.env` checked only whether values were present and
did not display their contents:

```text
GOOGLE_OAUTH_CLIENT_ID=empty
GOOGLE_OAUTH_CLIENT_SECRET=empty
```

The Django settings require both values and configure the Google provider only
when both exist. The login page disables the Google button while configuration
is missing. This is the intended safe behavior; it is not appropriate to hide
the warning or supply invented credentials.

The authorized redirect route was verified against Django's resolver:

```text
http://127.0.0.1:8000/accounts/google/login/callback/
```

## Google OAuth implementation inspected

- Uses django-allauth 65.22.0 with the Google OAuth 2.0 / OpenID Connect
  provider; no bespoke token-validation implementation was added.
- Requests `openid`, `email`, and `profile`.
- Uses `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` from the
  private root `.env`; a one-sided configuration raises a Django configuration
  error rather than silently proceeding.
- Starts from the app's CSRF-protected POST route `/auth/social/google/`.
- Uses allauth's session-bound OAuth state, authorization-code callback,
  token exchange, Google identity-token validation, and callback error
  handling.
- Uses the verified Google email for existing-account matching and auto-link
  behavior configured for the trusted Google provider. Allauth only permits
  email authentication when the provider's email is verified.
- Disables automatic account creation so first-time users complete the
  TalentBridgeAI signup form. The selected role is retained in the session;
  employers also provide a company name and remain pending approval.
- Uses the account adapter to route users to the dashboard or the employer
  pending-approval page, and safely validates any requested local destination.
- Keeps email/password login and POST-only logout available independently.
- `CONNECT_GOOGLE_OAUTH.ps1` provides hidden Client Secret input, saves the
  values locally, synchronizes the django-allauth app, and runs Django checks.

At the time of this historical snapshot, no live Google authorization,
account selection, authorization-code exchange, Google identity-token
validation, or Cloud Console setting had been tested. The 13 November status
addendum above supersedes this for the two existing-account login flows; first-
time signup and direct Cloud Console review are still unverified.

## Historical changes from the initial OAuth audit

### Backend and automated tests

`legacy-django/jobs/tests.py` now includes regression coverage for:

- Matching an existing local account only when Google reports a verified email.
- Handling a user-cancelled OAuth callback without creating an authenticated
  session.
- Rejecting callback state that was not initiated by the local session.
- Requiring POST for logout and clearing the authenticated session.

The tests use placeholder values and do not communicate with Google. No
authentication production code was changed because inspection did not identify
a code defect to fix; the missing external credentials are the actual blocker.

### Frontend and setup documentation

`README_SIGNIN_SIGNUP.md` now points to the dedicated setup guide. New
documentation explains exact callback configuration, consent screen/testing
users, local secrets handling, the current status, production setup, and
troubleshooting.

### Database and dependencies

- No application database schema or migration changed.
- No local user, admin credential, database, or existing record was altered.
- No dependency or requirements file changed.
- Django's test runner created and removed its temporary test database.

## Other project functionality verified from source and tests

### Resume upload

The existing resume flow stores PDF, DOC, or DOCX files up to 5 MB. It checks
file signatures (and DOCX archive contents) before storing a file. Download
access requires authentication and is scoped to the user's own resume or to an
employer's applicant on a job owned by that employer. Acceptance tests verify a
PDF upload and download retain the uploaded bytes.

### AI resume parsing

No AI resume-parsing service or external AI provider integration was found in
the inspected Django or frontend source. The existing upload feature stores and
serves resumes; this report does not describe that as AI parsing.

### Smart Profile Card

The job seeker dashboard includes the Smart Card panel and its `jdashboard.js`
behavior. An acceptance test verifies the dashboard renders its card elements
and script. No Smart Card implementation was changed during this OAuth task.

### Development workflow

Previously recorded work adds a DEBUG-only live-preview dashboard and browser
refresh handling, enables Django's autoreloader through the Windows startup
workflow, and requires a development/local environment before enabling DEBUG.
Production mode does not turn on the preview routes or development middleware.
See `LIVE_PREVIEW_SETUP.md` and the persistent checkpoint for the earlier
browser/autoreload checks.

## Complete known file-change history

Git history is unavailable in this workspace. The following earlier changes
are recorded by `TALENTBRIDGEAI_PROGRESS.md`; they are not represented as Git
commits.

**Earlier recorded live-development and structure work:**

- `legacy-django/jobs/dev_preview.py`
- `legacy-django/jobs/dev_preview_views.py`
- `legacy-django/templates/dev_preview.html`
- `legacy-django/jobs/test_dev_preview.py`
- `legacy-django/jobs/test_acceptance_flows.py`
- `legacy-django/config/settings.py`
- `legacy-django/config/urls.py`
- `css/dev-preview.css`
- `js/dev-preview.js`
- `tools/windows_manager.py`
- `START_TALENTBRIDGEAI.bat`
- `CONNECT_GOOGLE_OAUTH.ps1`
- `tools/project_structure_audit.py`
- `PROJECT_LAYOUT.md`
- `README_RUN_DJANGO.md`
- `README.md`
- `LIVE_PREVIEW_SETUP.md`
- `PROJECT_STRUCTURE_REPORT.md`
- `TALENTBRIDGEAI_PROGRESS.md`

**Files changed or generated for this OAuth/reporting task:**

- `legacy-django/jobs/tests.py`
- `README_SIGNIN_SIGNUP.md`
- `docs/setup/GOOGLE_OAUTH_SETUP.md`
- `docs/reports/PROJECT_CHANGELOG.md`
- `docs/reports/COMPLETE_PROJECT_REPORT.md`
- `docs/reports/TEST_REPORT.md`
- `docs/troubleshooting/REMAINING_ISSUES.md`
- `PROJECT_STRUCTURE_REPORT.md`
- `TALENTBRIDGEAI_COMPLETE_CHANGE_REPORT.txt`
- `TALENTBRIDGEAI_COMPLETE_CHANGE_REPORT.pdf`
- `TALENTBRIDGEAI_PROGRESS.md`
- `TalentBridgeAI_GOOGLE_OAUTH_COMPLETE_20261112.zip` (generated outside the
  source root after validation)

No files were deleted. No historical changes older than the available
checkpoint/archive comparison are asserted.

## Validation results

- `manage.py check` — passed with no issues.
- Focused `jobs.tests.SocialAuthenticationTests` — 24 tests passed.
- Full `manage.py test jobs` — 78 tests passed.
- OAuth callback route resolution — passed; resolves as `google_callback`.
- Local browser `/login/` — returned the sign-in page; Google button was
  disabled and the missing-configuration notice was visible, as expected.
- Local browser `/admin/login/` — returned the Admin login page.
- `tools/project_structure_audit.py --check` — passed; zero missing required
  entries, Python syntax errors, broken imports, or missing local asset paths.
- `TalentBridgeAI_GOOGLE_OAUTH_COMPLETE_20261112.zip` — CRC verified; 256 files
  included, all requested reports present, and no secret/runtime exclusions
  detected inside the archive.
- Resume upload/download and Smart Profile Card acceptance tests — included in
  the passing full suite.
- Real external Google sign-in — not performed; credentials and Cloud
  configuration are missing.

See `docs/reports/TEST_REPORT.md` for test scope and distinctions between passed,
failed, and blocked checks.

## Installation and local run

1. Keep the source tree intact and use `START_TALENTBRIDGEAI.bat` from the
   project root for the local development workflow. The project startup scripts
   install declared dependencies as needed, check the database, and start
   Django with development autoreload.
2. Open `http://127.0.0.1:8000/`. Do not use the static Go Live preview for
   account creation/authentication.
3. Email/password login and signup work without Google credentials.
4. To configure Google, follow `docs/setup/GOOGLE_OAUTH_SETUP.md` and use the
   credentials only in the private root `.env`.

## Google OAuth setup instructions

1. Create/select a Google Cloud project and configure the OAuth consent screen.
   Use External for public users; while the app is in Testing, add the Google
   accounts that will test it.
2. Create an OAuth client of type **Web application** and request only the
   existing `openid`, `email`, and `profile` scopes. No separate Google API is
   required by the current login-only integration.
3. For local testing, add the origin `http://127.0.0.1:8000` and this exact
   authorized redirect URI:

   ```text
   http://127.0.0.1:8000/accounts/google/login/callback/
   ```

4. Run `.\CONNECT_GOOGLE_OAUTH.ps1 -NoServer` from the project root and enter
   the real Client ID and Secret through the local prompts. This stores them in
   the ignored `.env`, synchronizes the allauth app, and runs Django checks.
5. Start with `START_TALENTBRIDGEAI.bat`, visit
   `http://127.0.0.1:8000/login/`, and test with an allowed Google test account.
   A production deployment must register its own exact HTTPS origin/callback
   and store credentials in the hosting platform's secret settings.

## Remaining requirements

Google sign-in is not declared fully working until the user supplies a valid
OAuth Web Client ID and Secret, configures the consent screen and exact redirect
URI in Google Cloud, and successfully completes a real browser login. The
remaining items are listed in `docs/troubleshooting/REMAINING_ISSUES.md`.
