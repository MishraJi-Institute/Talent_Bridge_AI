# TalentBridgeAI project changelog

## History and evidence limits

The workspace has no Git repository and Git history could not be inspected.
Before this OAuth documentation task, the source was compared with the
available `TalentBridgeAI_FINAL_20261112.zip`; no packaged source differences
were found at that point. The database backup is not a source-code history.
Older changes that cannot be established from the checkpoint or archive are
not attributed to a person or date here.

## Current continuation — 13 November 2026

- Fixed the DEBUG-only health checker so it scans app templates only inside
  the project; added a regression test for external package templates.
- Added an approved-employer Candidate Search page limited to the employer's
  own non-demo applications, with query filtering, pagination, and ownership
  tests.
- Added database-backed Remote Jobs and Startup Jobs filters. Development
  samples remain clearly labelled and non-persistent.
- Corrected a Manage Applications notice that incorrectly implied no real
  applications were loaded even when account-backed applications appeared.
- Added a server-validated Salary Calculator and corrected the homepage footer
  link; Career Resources now links to the calculator.
- Two live Google sign-ins, callback redirects, Job Seeker role routing, logout,
  and login after logout are verified. No credential values are recorded.
- Verification: 115 Django tests passed; the local asset checker found no
  missing references in 59 HTML and 35 CSS files.

The earlier persistent checkpoint records the following completed work. This
is a reconstruction from that checkpoint, not a claim that Git commits exist.

## Previously recorded development work

- Added DEBUG-only live-preview dashboard and refresh handling:
  - `legacy-django/jobs/dev_preview.py`
  - `legacy-django/jobs/dev_preview_views.py`
  - `legacy-django/templates/dev_preview.html`
  - `legacy-django/jobs/test_dev_preview.py`
  - `css/dev-preview.css`
  - `js/dev-preview.js`
- Gated development preview middleware/routes behind Django DEBUG and configured
  local startup to use Django's autoreloader:
  - `legacy-django/config/settings.py`
  - `legacy-django/config/urls.py`
  - `tools/windows_manager.py`
  - `START_TALENTBRIDGEAI.bat`
  - `CONNECT_GOOGLE_OAUTH.ps1`
- Added resume upload/download and Smart Profile Card acceptance coverage:
  - `legacy-django/jobs/test_acceptance_flows.py`
- Added the non-destructive structure audit and layout/preview documentation:
  - `tools/project_structure_audit.py`
  - `PROJECT_LAYOUT.md`
  - `PROJECT_STRUCTURE_REPORT.md`
  - `LIVE_PREVIEW_SETUP.md`
  - `README.md`
  - `README_RUN_DJANGO.md`
- Added/maintained `TALENTBRIDGEAI_PROGRESS.md` as the persistent development
  checkpoint.
- No project-wide folder move or source-file deletion was recorded. The layout
  remains Django under `legacy-django/`, frontend page/CSS/JS sources at the
  project root, and generated preview output under `site/`.

## Google OAuth audit and current task

The Google sign-in implementation existed before this task. Inspection
confirmed that Django settings load the two required environment variables;
django-allauth provides the Google authorization-code/OpenID Connect flow; the
callback resolves to
`/accounts/google/login/callback/`; the custom signup form collects role and
employer company information; and the account adapter routes users through the
dashboard/pending-employer flow. The login warning is accurate because the
local `.env` values are empty.

Files changed for this task:

- `legacy-django/jobs/tests.py` — added tests for verified Google-email matching,
  callback cancellation/invalid state, and POST-only logout/session clearing.
- `README_SIGNIN_SIGNUP.md` — directs users to the full Google OAuth setup guide
  and documents the current missing-credential status.
- `docs/setup/GOOGLE_OAUTH_SETUP.md` — exact local callback, Cloud setup, private
  credential instructions, local testing, production, and troubleshooting.
- `docs/reports/PROJECT_CHANGELOG.md` — this evidence-based change history.
- `docs/reports/COMPLETE_PROJECT_REPORT.md` — full project/change report.
- `docs/reports/TEST_REPORT.md` — final validation results and limitations.
- `docs/troubleshooting/REMAINING_ISSUES.md` — external setup and verification items.
- `PROJECT_STRUCTURE_REPORT.md` — regenerated after adding the OAuth reports.
- `TALENTBRIDGEAI_COMPLETE_CHANGE_REPORT.txt` and
  `TALENTBRIDGEAI_COMPLETE_CHANGE_REPORT.pdf` — matching user-facing reports.
- `TALENTBRIDGEAI_PROGRESS.md` — updated persistent checkpoint.

No OAuth implementation code, database schema, Django migration, dependency
manifest, database content, user account, or admin credential was changed.
No existing source file was deleted.

## Current Google OAuth status

- Automated code tests cover the local OAuth start, signup handling, safe
  redirects, verified-email matching, cancellation, and invalid state.
- The local Google Client ID and Client Secret are empty. No real Google
  account selection or successful callback has been performed.
- The current warning and disabled button remain until the user configures
  valid credentials in the private `.env` and Google Cloud Console.
