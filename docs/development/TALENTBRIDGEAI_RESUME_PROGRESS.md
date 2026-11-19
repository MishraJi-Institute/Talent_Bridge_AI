# TalentBridgeAI resume checkpoint

Updated: 2026-11-17 15:18 IST

## Current state

- The existing project, `.env`, database, users, and uploads were preserved.
- Stage 1 lifecycle/startup work is complete. Stage 2/3 feature work is in
  progress; advanced job search, explainable recommendations, application
  statuses, notifications, interview updates, employer analytics, account-
  backed education, and resume workflow checks have implementation and focused
  test coverage.
- The Django server is responding on `http://127.0.0.1:8000/`. Manager status
  reports managed root PID 17236; the current listener is PID 11272. Additional
  Python runserver processes were observed with ambiguous ownership. None were
  stopped or restarted.
- Live HTTP checks returned 200 for `/`, `/login/`, `/jobs/`, `/admin/login/`,
  and `/__dev__/state/`. The authenticated job-alert route correctly redirects
  anonymous visitors to login; no production credentials were used.
- Migrations `jobs.0011_application_statuses`,
  `jobs.0012_unique_interview_slots`, and `jobs.0013_job_alerts` are applied.
  The manager created and integrity-verified SQLite snapshots before each
  migration run. Read-only checks confirmed existing row counts were retained.
- The full `manage.py test jobs` suite passed all 169 tests (341.382 seconds)
  using an isolated in-memory test database. `manage.py check`,
  `makemigrations --check --dry-run`, and migration-plan checks passed.
- New focused workflow coverage passed 10 tests for saved job alerts,
  notifications/deduplication, employer applicant filters and isolation, and
  account-backed profile completion. Lifecycle-manager parser tests passed 3.
- The latest education/resume/candidate-privacy selection passed 5 tests.
  Education is persisted in the existing per-user `ResumeDraft` JSON field;
  no new migration was created for it.
- A fresh 19-file source-only continuation archive was previously created and CRC-verified:
  `backups/source-only/TalentBridgeAI_CONTINUATION_SOURCE_20261117_123836.zip`.
  It excludes `.env`, databases, media, uploads, and virtual environments.
- A current 375-file portable release was created and verified:
  `releases/TalentBridgeAI_Portable_20261117_151721.zip`. CRC, required-file,
  extracted-copy compilation, and Django system-check tests passed. It excludes
  `.env`, databases, uploads/media, backups, logs, and virtual environments.
- Browser verification of the login redirect and JavaScript syntax passed;
  no browser console errors were observed. Authenticated dashboard/job-alert
  visuals were not tested because no production account was used.

## Previous completed work

- Protected backup:
  `backups/protected/TalentBridgeAI_PROTECTED_BACKUP_20261117_105557.zip`
- Portable release:
  `releases/TalentBridgeAI_Portable_20261117_105557.zip`
- Backup/release integrity, extraction, and temporary-copy checks passed in the
  previous task. The protected backup is unencrypted and must not be shared.
- Existing application work and the previous 149-test `jobs` suite are
  preserved; that suite predates the current lifecycle changes.

## Stage 1 completed in this continuation

- Replaced the VS Code folder-open script's fixed port, stale-login restart,
  and process-kill behavior with a call to `tools/windows_manager.py start`.
- Updated the VS Code task description to document lifecycle-manager behavior.
- Fixed a missing `re` import used in migration SQL impact checks.
- Fixed Windows command-line path normalization so the manager can identify
  only processes rooted in this exact checkout.
- Ensured SQLite migration snapshot connections close before cleanup or
  migration continues.

## Files changed in this continuation

- `tools/windows_manager.py`
- `.vscode/start-talentbridge.ps1`
- `.vscode/tasks.json`
- `TALENTBRIDGEAI_RESUME_PROGRESS.md`

## Verification

- Python 3.12 project interpreter and supported Python 3.11–3.13 selection:
  passed.
- `.env` validation passed without printing values.
- Risky non-SQLite migration confirmation gate and backup-before-migration
  ordering: passed using isolated mocks.
- SQLite snapshot integrity and row preservation: passed using a temporary
  test database; file handles closed and the temporary test directory removed.
- Safe shutdown refused an unmanaged listener without invoking termination.
- Windows path normalization for exact-checkout process identification: passed.
- Occupied-default-port test selected port 8001 without stopping a process.
- `manage.py check`: passed (0 issues).
- Read-only migration plan: 0 pending operations; no migration was applied.
- PowerShell syntax and VS Code task JSON validation: passed.
- Manager status: port 8000 and homepage/login/admin/signup/static health checks
  all returned HTTP 200.
- Browser homepage: expected TalentBridge AI title; no console errors or failed
  requests.
- `logs/server.log`: no traceback/error markers in the inspected tail; a
  Broken pipe appeared during a successful request sequence.

## Current feature-sprint checkpoint

- Job listings support server-side title/company/location/skills/experience,
  job type and work-mode filters, sorting, relevance ordering, and pagination.
  Recommendations use profile/job signals and selected preferences with
  explanatory match reasons; no AI score is fabricated.
- Application statuses cover Applied, Under Review, Shortlisted, Interview
  Scheduled, Selected, and Rejected. Older `pending` and `reviewed` values are
  retained for compatibility. Duplicate status updates do not send repeated
  notifications.
- New applications notify the employer; application and interview status
  changes notify the candidate. Interview scheduling is idempotent and uses a
  transaction lock. The database uniqueness constraint from migration `0012`
  is applied. Employer ownership is checked on status changes.
- Employer dashboard now shows active/closed jobs, total and pending
  applications, shortlisted candidates, scheduled interviews, and the recent
  application list. Existing CSS already provides four desktop columns and two
  mobile columns. Counts come from account-owned, non-demo database records.
- Education entered through profile/dashboard forms is saved in each user's
  existing resume draft, loaded back into the profile, resume builder, and job
  seeker dashboard, and shown to an employer only for an application owned by
  that employer. This avoids adding a profile column/migration.
- Resume workflow tests cover upload replacement, rejection of mismatched PDF
  contents, deletion, owner downloads, applicant-employer downloads, and
  denial of unrelated users. Uploaded files are served through authenticated
  endpoints, not a public media route.
- Candidate-details messaging now distinguishes an authorized live application
  from the fictional samples; employer ownership remains enforced by the view.
- `jobs.0011_application_statuses` changes the application status field
  choices/default using a state-only migration. `jobs.0012_unique_interview_slots`
  adds a real unique constraint, and `jobs.0013_job_alerts` creates the saved-
  alert models. All three are applied after integrity-checked SQLite snapshots.
- Migration `0012`'s SQLite interview-table copy was reviewed and executed
  after a verified backup. No duplicate slots were found beforehand. Migration
  `0013` SQL adds tables/indexes only and did not rebuild existing tables. The
  verified snapshots are `backups/TalentBridgeAI_20261117_150025.sqlite3`
  (before `0011`/`0012`) and
  `backups/TalentBridgeAI_20261117_150958.sqlite3` (before `0013`).
- Focused test command:
  `manage.py test jobs.tests.ConnectedDatabaseFeatureTests jobs.tests.DashboardAccountCountTests jobs.tests.JobWorkflowTests`
  passed 30 tests. The latest full `manage.py test jobs --verbosity 1`
  run passed all 169 tests (341.382 seconds), including the new feature tests.
  An earlier run passed 155 tests before the
  education/resume additions. After the applicant-status pill/template and
  repeated-interview-status assertion edits,
  `manage.py test jobs.tests.ConnectedDatabaseFeatureTests jobs.tests.DashboardAccountCountTests --verbosity 1`
  passed all 11 tests (56.346 seconds).
- After the education/resume additions, the focused selection
  `ResumeWorkflowTests`, candidate-education authorization, profile editing,
  and dashboard profile saving passed all 5 tests (17.727 seconds).
- After adding the interview uniqueness constraint and making `0011`
  state-only, the focused status/interview tests passed (2 tests), migration
  consistency reported no model changes, and `sqlmigrate` showed `0011` as a
  no-op and `0012` as the expected table-copy constraint operation.
- The prior complete `jobs` suite passed 159 tests before migrations `0012`
  and `0013`; the latest 169-test result above supersedes it.
- Django check passed; migration check reported no model changes and no
  pending migration operations.
- Live HTTP probes returned 200 for `/`, `/login/`, `/jobs/`, `/admin/login/`,
  and `/__dev__/state/`. The warmed health endpoint returned 119–133 ms.
- `_check_links.py` checked 65 HTML and 39 CSS files without missing local
  references.
- The integrated browser fetched `jdashboard.js` with HTTP 200 and parsed it
  successfully with the browser JavaScript engine. The authenticated dashboard
  was not visually tested; no production account credentials were used.
- `node --check` was attempted but Node.js is unavailable in this environment;
  browser-engine parsing provided a syntax check instead.

Files changed by the feature sprint:

- `legacy-django/jobs/views.py`
- `legacy-django/jobs/models.py`
- `legacy-django/jobs/forms.py`
- `legacy-django/jobs/admin.py`
- `legacy-django/jobs/migrations/0011_application_statuses.py`
- `legacy-django/jobs/migrations/0012_unique_interview_slots.py`
- `legacy-django/jobs/migrations/0013_job_alerts.py`
- `legacy-django/config/urls.py`
- `legacy-django/jobs/tests.py`
- `legacy-django/jobs/test_new_quality_features.py`
- `legacy-django/jobs/templates/jobs/home.html`
- `pages/job-alerts.html`
- `pages/recommended-jobs.html`
- `pages/manage-applications.html`
- `pages/interviews.html`
- `pages/dashboard/cdashboard.html`
- `pages/dashboard/jdashboard.html`
- `js/dashboard/jdashboard.js`
- `pages/profile.html`
- `pages/edit-profile.html`
- `pages/candidate-details.html`
- `tools/test_windows_manager.py`

The source-only pre-sprint archive is
`backups/source-only/TalentBridgeAI_FEATURE_SPRINT_SOURCE_20261117_115356.zip`.
The newest current-code package is
`releases/TalentBridgeAI_Portable_20261117_151721.zip`; it contains no `.env`,
database, or private media. Existing protected backups are documented above.
The project database received the reviewed migrations listed above; existing
user/company/profile row counts were preserved.

## Latest QA and feature update

- Fixed a lifecycle-manager bug: Django's current `migrate --plan` output lists
  `app.migration` names, while the manager only searched for `[ ]` markers.
  The false negative skipped pending migrations. The manager now parses both
  formats; 3 focused parser tests pass.
- Added saved job-alert preferences for title, location, skills, type, work
  mode, and experience. Enabled preferences match active, approved, non-demo
  database jobs; alerts and in-app notifications are deduplicated per user/job.
  Users can pause/re-enable alerts and see matching-field explanations.
- Employer application management now supports candidate/skill search, status
  filtering, newest/oldest sorting, 25-item pagination, profile headline/skills/
  experience display, own-company isolation, and exclusion of demo jobs.
- Profile completion now uses account-backed name, email, headline, bio, skills,
  education, experience, location, and uploaded-resume fields. Incomplete
  checks link to the relevant form field or account page; browser-only fields
  no longer inflate the percentage.
- New alert models are available in Django Admin. The new job-alert workflow,
  access control, applicant filters, and profile completion are covered by 10
  focused tests within the 169-test full suite.
- Live Django manager status is healthy on port 8000. Five `/__dev__/state/`
  requests returned 200; after warm-up, responses were 119–133 ms. The
  browser confirmed anonymous job-alert requests redirect to login and parsed
  the updated dashboard JavaScript with no syntax error or console error.
- Portability: the new release ZIP passed CRC, extraction, Python compilation,
  and extracted-copy Django system checks. It excludes secrets/database/media.

## Errors and cautions

- `logs/setup.log` contains historical server-exit records, including
  2026-11-17 11:40:58. The corresponding inspected server-log tail had no
  traceback and the site remains healthy. Cause of that earlier process exit
  is unconfirmed.
- A later server-log scan found three `SyntaxError` traceback markers, with
  traceback metadata pointing to `views.py` line 1815 during reload/edit
  activity. The current source passes Django checks and the full test suite,
  and live routes are healthy; the historical exception text is not retained
  here, so treat the transient reload cause as unconfirmed.
- Multiple runserver processes exist; ownership of all listeners is not
  established. Do not stop or restart them until ownership is verified.
- Two early isolated backup-test attempts failed due to test-harness issues
  (fixture connections not explicitly closed and a mocked backup helper not
  restored). The corrected harness passed; no production data was affected.
- No real VS Code folder-open or Windows-restart test was run.

## Remaining work / exact next step

1. Continue the broad remaining audit: registration/OAuth/email settings,
   authenticated Admin flows, and responsive authenticated pages. First-time
   Google signup, production SMTP/TLS, and superuser login were not tested.
2. Verify Windows restart and VS Code reopen behavior only when owner-
   authorized. The current portable ZIP extraction test passed; no actual
   Windows restart or folder-open test was run.
3. Keep the existing Django server running. Multiple runserver processes have
   ambiguous ownership; do not stop or restart any process until ownership is
   established. Do not modify credentials, `.env`, existing user data, or
   uploaded files.
