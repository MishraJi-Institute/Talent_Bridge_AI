# TalentBridgeAI test report

**Date:** 2026-11-12 (historical snapshot)  
**Test result:** Automated test results in this snapshot are superseded by the
13 November continuation status below.

## Current continuation result — 13 November 2026

The older result above is a dated snapshot. `manage.py check` and
`makemigrations --check --dry-run` passed, and the full `manage.py test jobs`
suite passed **119 tests** after adding opt-in profile discovery, privacy
settings, saved-job/demo separation, access-denied handling, and admin links.
`_check_links.py` checked 62 HTML files and 35 CSS files with no
missing local references. These tests use Django's temporary database. Two user-authorized
Google sign-in/consent flows completed: both callbacks returned 302, both
protected dashboard routes reached the Job Seeker dashboard (200), and logout
returned 302 after each. A dashboard request after logout redirected to login.
First-time signup and direct Cloud Console configuration review remain
unverified. The live database received only the additive
`0008_profile_is_discoverable` migration; aggregate counts remained unchanged
(2 users, 2 profiles, 0 companies, 0 jobs, 0 applications), both existing
profiles default to private, and SQLite integrity reports `ok`.

The dated ZIP row in the historical table below describes an earlier archive,
not the requested final delivery for this continuation. The final PDF,
current screenshots, and clean ZIP remain outstanding until development is
complete.

## Passed checks

| Check | Result |
|---|---|
| `python manage.py check` | Passed; no issues identified |
| `python manage.py test jobs.tests.SocialAuthenticationTests` | Passed; 24 tests |
| `python manage.py test jobs` | Passed; 78 tests |
| Google callback URL resolution | Passed; route name is `google_callback` |
| Salary Calculator | Passed; calculations, input bounds, friendly and physical routes, and live browser submission verified |
| Local browser `/login/` | HTTP 200; expected missing-credentials notice and disabled Google button |
| Local browser `/admin/login/` | HTTP 200; Admin login form rendered |
| Email/password login | Automated test confirms authentication and session creation |
| Job-seeker registration | Automated test confirms user creation with valid CSRF |
| Employer registration | Automated test confirms profile/company creation and pending approval |
| Google OAuth start | Automated tests confirm CSRF-protected start and redirect to Google using placeholder test credentials |
| Existing Google-email account matching | Automated test confirms verified Google email matches the local account and unverified Google email does not |
| Callback cancellation and invalid state | Automated test confirms cancellation is handled and an uninitiated state is rejected without authenticating a user |
| Logout | Automated test confirms GET is rejected, POST logs out, and the session is cleared |
| Resume upload/download | Existing acceptance test verifies a PDF upload and byte-identical download |
| Smart Profile Card | Existing acceptance test verifies the dashboard card elements and script |
| Project structure audit | Passed; zero missing required entries, Python syntax errors, broken imports, or missing local asset paths |
| Final source ZIP | CRC passed; 256 files; all requested reports included; secrets, databases, runtime data, and generated output excluded |

The full test runner emitted a `Not Found: /jobs/2/apply/` log line from an
expected negative-path test; the suite completed with all 78 tests passing.

## Test iteration note

The first version of the new callback-cancellation test expected an HTTP 200
directly from the callback. Runtime evidence showed that django-allauth
redirects cancellations to its dedicated cancellation page (HTTP 302); that
page then returns HTTP 200. The test was corrected to assert that behavior.
Invalid state returns HTTP 401. The final focused and full test suites pass.
This was a test expectation correction, not an application failure.

## Not performed / blocked

- First-time Google account creation and signup.
- Direct Cloud Console review of consent-screen status, origins, redirect URIs,
  or test-user configuration.

The local `.env` values were confirmed present without displaying them. Cloud
Console access was not provided. Placeholder credentials in automated tests do
not count as a first-time Google signup.

## Validation environment

- Django 5.2.19.
- django-allauth 65.22.0.
- Windows local development environment.
- Tests use Django's temporary test database; no persistent project database or
  existing user record was modified.
