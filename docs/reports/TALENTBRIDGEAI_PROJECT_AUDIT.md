# TalentBridgeAI project audit

Date: 2026-11-12  
Baseline: Step 2 verification accepted. This audit does not reset the database or replace the project.

## Dashboard checkpoint update

The employer dashboard now renders the authenticated account's company details, active non-demo jobs, non-demo applicants and real application-status counts. Its 365-day application/interview history feeds the date-range chart and account-backed CSV. The job-seeker application count excludes demo-job applications. These are still partial dashboards: employer documents and team management are browser-only previews, and existing dashboard customization remains local.

The latest browser check of the protected employer dashboard correctly redirected to sign-in. Dashboard account data and status rendering are covered by `DashboardAccountCountTests`; the final `manage.py test jobs` run passed all 85 tests, and `manage.py check` passed. Google OAuth consent, callback, session, and logout remain unverified. No live database change or server restart was made for this dashboard work.

## Current state

TalentBridgeAI is one Django project in `legacy-django/` and a root frontend in `pages/`, `css/`, `js/`, and `images/`. The `jobs` app owns models, views, auth adapters, and Google OAuth sync. SQLite lives at `database/TalentBridgeAI.sqlite3`. The accepted backup is `backups/audit_20261112_154417/`.

Startup, stop, homepage, login, signup, and admin-login pages were verified. Google settings load and the callback route exists, but real consent and callback/session/logout remain unverified. The latest read-only database check found two users/profiles, no superuser, and no companies, jobs, or applications; this dashboard work did not change live data.

## What already works

- Email/password registration views for job seekers and employers, with employer approval before job publishing.
- Database-backed jobs, applications, saved jobs, notifications, interviews, contact messages, profiles, and one resume file per profile.
- Django admin at `/admin/` and a staff approval page at `/admin-dashboard/`.
- Password reset templates and routes. Email stays on the console backend until SMTP is configured.
- Windows start, stop, status, and restart scripts. One managed server on port 8000.

## What is incomplete

- Job seeker and employer dashboards under `pages/dashboard/` now show selected account-backed company, job, application, and analytics data. Team/document previews and several customization controls remain local-only; the dashboards are not complete server-backed workflows.
- Saved-jobs and several marketing pages still show sample cards beside, or instead of, account data.
- Resume upload stores one file. There is no multi-file library, parser, builder, or profile-card persistence.
- Job search is keyword and location only. There is no match explanation.
- Public company browsing did not exist before this phase. Approved companies can now be listed.
- Admin management beyond Django admin and employer approval is not built.
- Email verification is not implemented.
- No AI provider is configured. Cursor is the coding environment, not the website's runtime AI.

## Duplicates and conflicts

- `site/` is a generated copy of pages. Django serves `pages/`, not `site/`.
- `pages/jobseaker.html` is a misspelled public page and is separate from the seeker dashboard.
- `pages/dashboard/dindex.html` redirects to the employer dashboard and is a legacy layout.
- Two visual systems exist: the large `index.html` homepage and the smaller `portal-pages.css` interior pages.
- `docs/reports/COMPLETE_PROJECT_REPORT.md` still says Google credentials are empty. The accepted verification supersedes that.

## Authentication

Passwords use Django's hasher. Sessions use the database. Google sign-up requires a role form and does not auto-create silent accounts. The live consent flow remains untested. Do not treat an enabled button as a completed login.

## External approval still required

- An interactive superuser password via `CREATE_SUPERUSER.bat`.
- Google Cloud origin `http://127.0.0.1:8000` and redirect `http://127.0.0.1:8000/accounts/google/login/callback/`.
- A chosen AI provider and key before any parsing, resume generation, matching explanations, or assistant calls a paid API.
- SMTP settings before email verification or real password-reset delivery.
- Approval before automatic Windows logon startup.
