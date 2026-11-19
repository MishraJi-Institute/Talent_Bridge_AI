# TalentBridgeAI development progress

## Deployment security baseline — 2026-11-13

- Full Django suite: 133 tests passed; the standard system check is clean.
- `manage.py check --deploy` in production-settings context reports four
  hardening gaps: HSTS, HTTPS redirect, secure session cookies, and secure
  CSRF cookies.
- The actual local site uses HTTP and is started with development environment
  variables. No production security flags were guessed or enabled; HSTS and
  redirect settings require the target domain and TLS/reverse-proxy details.
- Owner confirmed local-only use for now. Actual-browser mobile checks of 22
  public Django routes and five authentication/recovery routes all returned
  successfully with no horizontal overflow at the configured 390px width
  (effective viewport 312px, document width 300px).
- Production security sign-off remains outstanding. Do not equate the passing
  development test suite with production deployment security.

## Password recovery — 2026-11-13

- Preserved the existing Django password-reset implementation and verified
  the full signed-link flow through password change on a temporary test DB.
- Added a regression proving unknown email addresses receive the same success
  redirect without mail, reducing account enumeration risk.
- Updated recovery navigation to real Django routes and disclosed that local
  development writes reset mail to the server console rather than sending it.
- Fixed stale relative links across Login, signup-type selection, and seeker
  and employer registration forms. They now use the real Django routes for
  account navigation, legal pages, and password recovery.
- All 10 focused authentication/recovery tests, `manage.py check`, and
  `_check_links.py` (64 HTML, 37 CSS) passed. Inspected the recovery, signup
  router, job-seeker signup, and login pages on the actual Django site. No
  live records or schema changed; registration forms were not submitted.
- The complete Django suite subsequently passed all 133 tests in 215.6
  seconds; the final local HTML/CSS link check also passed.
- Actual-browser mobile checks of Login, signup selection, both signup forms,
  and Forgot Password reported no horizontal overflow at the configured 390px
  width (effective browser viewport 312px, document width 300px).
- SMTP delivery, first-time Google registration/consent, owner-operated
  Super Admin setup, broader account review, full security/responsive testing,
  and final PDF/ZIP remain outstanding.

## Privacy and Cookie Preferences — 2026-11-13

- Replaced inaccurate static-preview statements with the current local Django
  data flows: account/profile/application/contact records, private resume
  storage, OAuth, external Google Fonts, local email backend, and no connected
  AI provider.
- Clarified essential session/CSRF cookies, browser-only preferences, absent
  consent controls, and that clearing browser storage does not delete
  server-side user data.
- Focused privacy/cookie regression test passed; `_check_links.py` checked 64
  HTML and 37 CSS files. The actual Django browser showed both pages without
  horizontal overflow at the configured 390px viewport (effective width
  300px).
- No database records/schema were changed. Remaining public/account pages and
  owner-assisted authentication verification remain unfinished.

## Categories and Pricing — 2026-11-13

- Category cards now route to the Django job search with their keyword filter;
  a focused test verifies real job-query filtering.
- Pricing now clearly discloses that prices, limits, and plan features are
  illustrative, with no active payments/subscriptions or AI hiring features.
  Purchase-implying links now open Contact, the employer CTA opens registration,
  and the obsolete third-party mailto was removed.
- Corrected navigation on Categories, Careers, Blog, and Customer Stories to
  use friendly Django routes. Kept example stories explicitly non-testimonial.
- Fixed a stale pricing JavaScript callback; actual-browser monthly/yearly
  toggles now work without script errors. Pricing and Categories showed no
  horizontal overflow at the configured 390px viewport (effective width 300px).
- All 12 public `PageRoutingTests` passed; Django system check and the local
  link checker (64 HTML, 37 CSS) passed. No live data or schema was changed.

## Public information pages — 2026-11-13

- Corrected About, Help, FAQ, Trust Center, Platform Status, AI Audit Center,
  and Terms to describe the actual Django deployment accurately. Live
  account-backed workflows, labeled demo data, local-only email handling,
  missing public uptime reporting, and unavailable AI generation are now
  distinguished.
- Fixed About's brand navigation to use the real Django root `/`.
- `manage.py check` and focused page regression tests passed;
  `_check_links.py` found no missing local references across 64 HTML and 37 CSS
  files. Inspected the actual pages on `127.0.0.1:8000`; FAQ showed no
  horizontal overflow at the configured 390px width (browser effective width
  300px).
- No application records or schema changed. Remaining public/account pages
  remain in progress.

## Resume Builder continuation — 2026-11-13

- Recovered the interrupted work and visually inspected the required design
  board at `design-references/TalentBridgeAI Premium Design System Board (1).png`.
- The existing authenticated, account-backed manual Resume Builder already
  saves a private draft, displays a live preview, and offers browser
  Print/Save as PDF. Its template clearly discloses that AI writing is
  unavailable; no provider was configured or simulated.
- Confirmed `jobs.0009_resumedraft` is applied in the existing Django
  database. No migration or live data was changed in this continuation.
- `manage.py check` passed; 12 focused Builder and Resume Upload/Library tests
  passed using the temporary Django test database. `_check_links.py` passed
  across 64 HTML and 37 CSS files.
- The actual Django Builder URL redirects signed-out visitors to login with
  the return path intact. Automated tests cover authenticated save/reload,
  preview escaping, invalid submission, upload, download, replacement, and
  deletion. A signed-in live-browser verification was not possible in the
  available browser session.
- Continue with the remaining public/account pages. Google first-time signup,
  owner-operated Super Admin verification, any provider-backed AI features,
  full responsive/security testing, and final PDF/ZIP remain outstanding.

## Latest resumed increment — Resume Upload/Library verification

- Re-ran `jobs.test_acceptance_flows.ResumeUploadAcceptanceTests`: all 8 tests
  passed against Django's temporary test database.
- Live Django requests to `/resume-management/` and
  `/pages/resume-management.html` correctly redirected an anonymous browser to
  login with the destination preserved. No resume data was accessed or changed.
- No application files or live database records changed in this verification.
- Next: inspect and implement the absent authenticated Resume Builder with a
  real saved draft, live preview, and export. AI generation remains unavailable
  until an AI provider is configured.

## Latest resumed increment — actual Django homepage

- The required design reference `TalentBridgeAI Premium Design System Board (1).png` was opened and visually inspected. Its three designs are a premium recruitment homepage, analytics dashboard, and resume editor/live preview.
- The actual Django root `/` remains HTTP 200; `/site/index.html` now redirects there. `/index.html` serves raw template markers, so the Job Search brand points to `/`.
- Strengthened the root hero's blue right-side gradient and reverified desktop/mobile layout. Candidate art remains explicitly illustrative; all counts are live Django data and demo match/role cards clearly disclose that AI matching is not connected.
- Reverified phases 1–3 (dashboards): 23 focused Django tests passed; actual anonymous browser requests redirect to login; signed-in templates and Admin permission behavior are covered by Django tests.
- Phase 4 (Job Search / Company): fixed the root brand link, anonymous Dashboard CTA, job title link styling, and company brand marks. Search filters correctly on the live Django route. The company directory currently has no approved records; test database cases verify approved detail access and exclusion of unapproved companies.
- Verification: homepage 5 tests, dashboard/Admin 23 tests, Job Search/Company 7 tests, `manage.py check`, and `_check_links.py` (63 HTML / 36 CSS) passed. Desktop/mobile Django browser checks showed no horizontal overflow. Existing database records were not changed.
- Existing five-file homepage work was preserved. Resume Upload/Resume Library has since been reverified; continue with the AI Resume Builder. No AI provider is configured.

## Resumed dashboard and Admin checkpoint

Updated: 2026-11-13

- The reference image at `design-references/TalentBridgeAI Premium Design System Board (1).png` was opened and visually inspected. Job Seeker, Employer, and staff dashboards now use its blue/navy/soft-background direction and Inter/Manrope typography.
- Employer approval visibility now respects company view/change permissions, and only staff with company-change permission can approve. A focused regression test covers the denied path.
- Verification in this increment: Django system check passed; 4 focused dashboard/Admin tests passed; `_check_links.py` checked 63 HTML and 36 CSS files without broken local references. The live Django homepage and health endpoint returned 200 with one listener on port 8000.
- Node.js is unavailable, so JavaScript syntax validation was not run. The signed-in dashboards were server-rendered in tests; no authenticated browser screenshot was available.
- Next: continue the remaining workflow audit, beginning with a backend-backed Resume Builder/live preview/export. No AI provider is configured, so generated AI content remains unavailable. Preserve the existing migration/backup safeguards.

## Latest live-preview and server reliability verification

Updated: 2026-11-13

- Root cause of the recurring browser warning and slow health checks: the Django health endpoint recursively sorted and enumerated the whole Django project, including `.venv` and `staticfiles`, before filtering file names. With the monitor polling every 1.2 seconds on every Django HTML page, open tabs repeated the expensive scan and re-announced the same failed poll. Before the fix, `/__dev__/state/` took 12,079 ms; after pruning ignored directories before traversal, five consecutive checks completed in 113–287 ms.
- Client fix: the monitor now polls every five seconds, aborts a stalled health request after eight seconds, backs off to 15 seconds during continued failures, announces an outage once per transition, and clears that notice on the first successful recovery poll. Repeated identical status/error text is not rewritten into live regions.
- Browser fault-injection verified the behavior: an intentionally aborted health request showed one notice; after repeated failures the notice remained a single unchanged element; restoring the route let the successful poll clear it. The injected aborts intentionally generated browser `ERR_FAILED` events and a Django broken-pipe log entry. A normal Django reload then recorded no browser console errors, uncaught errors, failed requests, or outage notice.
- Static preview distinction: VS Code Live Server on port 5500 serves generated `site/`, not the root source tree. Its assets had been stale because `build_static.py` could not render newer `account-security` and `candidate-search` routes or the `static`, `with`, and `empty` template tags. Those generator gaps are fixed, `site/` was rebuilt, and the static directory link now opens a clearly labelled Django-backed company-directory page. Static pages do not poll `/__dev__/state/`; its 404 on port 5500 is expected.
- Static browser verification after the rebuild: port 5500 `/` and `/pages/companies.html` returned 200, the static notice appeared once and clearly lists Django-only sign-in, OAuth, resume uploads, dashboards, and database actions, all requested local assets loaded without failed requests, and no Django health requests were made. Its `/login/` and `/__dev__/state/` paths correctly remain unavailable.
- Django verification: port 8000 `/`, `/login/`, `/companies/`, and `/__dev__/state/` returned HTTP 200. The health payload reported server/frontend `ok` with zero errors; repeated checks stayed below 500 ms. Anonymous `/dashboard/` redirected to login. Browser checks showed no static-preview notice on Django pages. The startup manager reported the existing server healthy and reused it; exactly one listener remained on port 8000.
- Tests and checks: all 120 Django `jobs` tests passed (242.480 seconds); `manage.py check` reported no issues; `makemigrations --check --dry-run` found no changes; `build_static.py` completed; `_check_links.py` checked 63 static HTML files and 35 CSS files without missing local references; Python compilation checks passed.
- Read-only database integrity is `ok`; the current counts are users=3, profiles=3, companies=1, jobs=0, applications=0. No database rows were changed by this pass; the test runner used and destroyed its temporary database. These current counts supersede older checkpoint counts.
- Admin/OAuth status: there are currently zero active superusers. `CREATE_SUPERUSER.bat` calls an idempotent interactive command and will not reset existing accounts; creating a usable permanent admin requires the owner to enter the chosen credentials locally. Google OAuth settings and one provider app are present (no values were printed); prior saved checkpoints document two successful login/callback/logout cycles. First-time Google signup and direct Google Cloud Console review remain unverified.
- This pass resolves the recurring health notification and static preview/build issues; it does not complete the entire platform. Remaining workflow audit, any required admin account setup, first-time OAuth signup verification, final screenshots/PDF/ZIP, and other incomplete product areas are still outstanding.

## Server recovery and resumed checkpoint

Updated: 2026-11-13

- Latest server recheck: Django is running with exactly one listener on port 8000; no second server was started. `/`, `/login/`, and `/__dev__/state/` return HTTP 200; health is server/frontend `ok` with zero errors. Privacy settings, Get Discovered, and Candidate Search correctly redirect anonymous users; Access Denied returns HTTP 403. Port 5500 is a separate static preview (`/` 200, `/__dev__/state/` 404). The actual Django homepage rendered in the browser without the stale warning.
- Follow-up root cause and fix: the development health endpoint's template checker also scanned installed allauth templates outside the project. An allauth template referenced an unregistered `humanize` tag library; formatting that external path with `relative_to(PROJECT_ROOT)` then raised `ValueError`, causing `/__dev__/state/` to return 500 in the full test. The checker now scans app template roots only when they are inside the project. A regression test covers external app templates.
- Google OAuth configuration check (values withheld): both private settings load; the provider and active-site SocialApp match; the callback resolves correctly. Two user-authorized sign-ins/consents completed; each callback returned 302 and `/dashboard/` routed to the Job Seeker dashboard (200). Logout returned 302 after each, and a later dashboard request redirected to login. First-time signup and direct Google Cloud Console review remain untested.
- Root cause distinction: the previous stale-warning behavior in `js/dev-preview.js` is fixed. The separate static preview on port 5500 returns HTTP 404 for `/__dev__/state/` and `/login/`; its unavailable warning is expected and does not indicate Django failure. Port 5500 belongs to VS Code; port 8000 belongs to the single Django process. `RUN_DJANGO_WINDOWS.bat` delegates to `START_TALENTBRIDGEAI.bat`; it was not run because the existing Django server is already healthy, avoiding a duplicate.
- Root cause: a transient failed health-poll during autoreload made the client show “Development server unavailable”, but `js/dev-preview.js` did not clear that network-error banner after a later successful poll. The success path now hides the banner only after recovery.
- Actual-browser regression check: deliberately aborted one `/__dev__/state/` fetch on the Django login page, confirmed the warning appeared, then confirmed it disappeared after the next successful health poll. `/dashboard/` and `/account-security/` safely redirect unauthenticated visitors to `/login/`; authenticated dashboard visuals still require an authorized session.
- Server verification: homepage and login returned HTTP 200; `/__dev__/state/` returned HTTP 200 with server/frontend status `ok` and zero errors. Exactly one listener remained on port 8000. Port 5500 serves a distinct static preview. The full Django suite and the eight focused Resume Upload acceptance tests used temporary databases/media.
- Read-only live database check: SQLite integrity is `ok`; users=2, profiles=2, companies=0, jobs=0, applications=0. The Django suite used its temporary test database.
- The seeker dashboard now has a prominent **Upload Resume** CTA to the authenticated library. Added `/recommended-jobs/`, which ranks approved, active, non-demo jobs by profile skills/location, excludes submitted applications, and only displays labelled non-persistent sample roles in development when no live jobs exist. Jerry's local guide links to this page and discloses that matching is not a connected AI provider.
- The last private provider check found no configured AI key. The user selected OpenAI for private setup; no key was requested, displayed, or used. Two Google OAuth login/session/role redirect/logout cycles are verified, including a login after logout; first-time signup and direct Cloud Console review remain untested.

- Resume management now supports authenticated PDF/DOC/DOCX uploads (maximum 5 MB), private download, in-browser PDF preview, replacement, and deletion. DOC/DOCX remain downloadable and are clearly marked as requiring a compatible local app for preview; resumes are not sent to an external viewer.
- Fixed a replacement bug: Django mutates the bound `FieldFile` during save, so the former comparison left the replaced file on disk. The previous storage name is now preserved and removed after the replacement saves.
- The job-seeker dashboard now bootstraps name, headline, location, skills, experience, and summary from the account profile and saves those fields through an authenticated, CSRF-protected endpoint. Smart Card content updates from those account fields. Extended dashboard details and appearance settings remain browser-local and are disclosed as such.
- Fixed a dashboard behavior bug: demo Apply actions updated browser storage, while the Applications page displayed account rows instead. Account applications and the clearly labelled browser-only sample tracker now have separate lists and controls.
- Employer job editing now has an owner-scoped route, form validation, and an Edit action in Manage Jobs. Tests cover successful edits, invalid input, attempts to edit another employer's jobs, and demo-job exclusion.
- Added `/candidate-search/`, scoped to the signed-in approved employer's own non-demo job applications. It searches candidate name, email, profile skills/headline/location, and role, paginates results, and deliberately does not expose all user profiles without explicit opt-in. The application page now accurately distinguishes its sample table from account-backed applications.
- Added authenticated `/privacy-settings/` and `/get-discovered/` preferences. Profiles default to private; approved employers see only opted-in names and profile fields, never discovery results' email, phone, or resume. Applied the additive `0008_profile_is_discoverable` migration; aggregate counts remained users=2, profiles=2, companies=0, jobs=0, applications=0, both existing profiles are private, and SQLite integrity is `ok`.
- Fixed `/saved-jobs/` mixing fictional preview rows with real account-saved jobs and showing obsolete “not connected” copy. The demo preview now appears only when the account list is empty; saved jobs are shown inside the workspace with success feedback, live Django navigation, and demo/unapproved jobs excluded from account records.
- Added `/access-denied/` as a genuine HTTP 403 page with recovery links and configured it as Django's 403 handler. Expanded the staff dashboard and Django admin indexes for searchable profile, saved-job, notification, and interview management.
- Added `/remote-jobs/` and `/startup-jobs/` filters using approved job and company data. Development fallback roles stay labelled and are limited to the requested filter; job search/clear-filter links preserve the selected route.
- Added a server-validated Salary Calculator for annual, monthly, semi-monthly, biweekly, weekly, daily, and hourly gross pay. Corrected the homepage Salary Calculator footer link; the calculator is linked from Career Resources and clearly disclaims tax and currency conversion.
- Added `/account-security/` with an authenticated password change, current-password validation, session preservation, success/error feedback, and entry links from both dashboards. Email verification and MFA remain unimplemented.
- Replaced the staff dashboard's fictional summary and queue with live account/job/application counts, pending employer approvals, recent contact messages, and permission-gated Django admin links. Demo jobs are counted separately from live jobs; non-staff are redirected.
- Verification: `manage.py check` and `makemigrations --check --dry-run` passed; the complete suite passed 119 tests after the latest access-denied and admin updates. `_check_links.py` checked 62 static HTML files and 35 CSS files with no missing local references. The 8 focused Resume Upload acceptance tests also passed previously, and are included in the full suite.
- Overall completion estimate: 59%; implementation 85%; testing 63%; verification 72%. These are coarse estimates, not claims that every page or requested integration is finished.
- Page counts: 53 documented workflow/page entries—12 complete, 39 partial, 0 blocked, and 2 not implemented. Thus 51 are active and 2 are inactive. The PAGES map has 50 friendly aliases and there are 60 physical page templates; Remote Jobs and Startup Jobs are additional named routes.
- OAuth: two callbacks, session establishment, Job Seeker role redirect, logout, and login after logout are verified. The browser is logged out as expected. First-time signup and direct Cloud Console review remain untested. No Git metadata or Git executable is available to inspect an editor Review queue; existing project files were preserved and edits were surgical.
- No direct edits to live account records were made. One additive schema migration added a default-private preference; aggregate user/application counts are unchanged and database integrity passed. OAuth sign-ins were user-initiated. No final PDF, saved screenshots, or ZIP has been created. Milestone sound playback and speech succeeded and a balloon was requested; actual audibility/display was not user-confirmed.
- Next: continue the Admin and remaining workflow audit. AI Resume Builder/generative assistant integration is blocked until a provider is configured; do not treat profile-based job ranking or offline Jerry guidance as AI generation. Keep all demonstration content separate from user records.

## Historical checkpoint — resume library

Updated: 2026-11-13

- The resume library now clearly presents the authenticated account upload workflow, supported formats, the 5 MB cap, current-file download, empty state, and replacement behavior. The prior fictional document was removed from the live resume state.
- Upload handling remains private and server-validated. Acceptance tests cover authentication, valid PDF upload/download, invalid extension/content, and oversized files.
- Direct physical page paths for saved jobs, notifications, interviews, candidate details, and the admin dashboard now call the same permission-checked, account-backed views as their friendly URL aliases.
- Verification: `manage.py check` passed; the complete `manage.py test jobs` suite passed all 89 tests. All physical page templates and named page routes passed the existing route smoke tests. `_check_links.py` checked 55 static HTML files and 35 CSS files without missing local references.
- At this earlier checkpoint, no live database data had been changed; OAuth callback/session/logout were not yet verified. The broader inactive-page and full-project review requested on 2026-11-13 is not complete; do not claim final project, PDF, or ZIP completion.
- Next: continue auditing and activating incomplete page interactions against their existing Django routes and clearly labelled demonstration data. JavaScript syntax validation remains unrun because Node.js is unavailable in this environment. Keep OAuth verification user-assisted and do not inspect or reveal private credentials.
- Older notes below are historical. The later audit found two users/profiles and a client ID with the expected Web-client suffix; older zero-user and invalid-client-shape statements are superseded. At the time those notes were written, the Google consent/callback flow had not been completed.
- Older notes below are historical. The later audit found two users/profiles and a client ID with the expected Web-client suffix; older zero-user and invalid-client-shape statements are superseded. At the time those notes were written, the Google consent/callback flow had not been completed.

Updated: 2026-11-12 23:17 local. Notification restoration is complete; product development remains paused pending the Google OAuth/user checkpoint.

## Notification restoration checkpoint

- Repaired the existing `tools/activity_notify.ps1` milestone path and kept `ACTIVITY_NOW.md`, heartbeat/status files, and `logs/activity.log` as the existing progress system.
- The pulse process was not running when checked. `tools/activity_pulse.ps1` remains the visual heartbeat and no longer plays repetitive timed sounds.
- The development test (23:14) and final safe-pause notification (23:17) used `C:\Windows\Media\Windows Notify.wav` with synchronous `SoundPlayer.PlaySync()`. Both returned successful audio playback, SAPI speech, and balloon-request results. `Audiosrv`, `AudioEndpointBuilder`, and the default wave output probe were OK; the Realtek speakers/headphones endpoint was listed.
- Actual speaker/headphone output was not independently confirmed. Do not claim it was heard. Run the listening test in `NOTIFICATION_SETUP.md` if audibility must be confirmed.
- Script execution required a child PowerShell process with a process-only execution-policy override; persistent policy was not changed. No Windows volume/device settings were changed.
- At the time of this notification checkpoint, Google OAuth callback/session/logout remained unverified; the broader project remains incomplete.

Interim report written while paused: `docs/reports/TalentBridgeAI_Interim_Progress_Report.pdf`. No website feature was added for that report. Before-and-after screenshots were not saved in the project, so the PDF does not embed any.

## Pause checkpoint

- Last completed task: seeker application rows and employer job and applicant rows read account records. `DashboardAccountCountTests` passed once on Django’s temporary test database. Categories, Help, FAQ, and Pricing link to `/jobs/` and `/companies/` and each returned HTTP 200.
- Current unfinished task: Google sign-in. The browser was still on Google’s account sign-in page. Callback, Django session, and logout were not verified. The employer hiring chart and sample company name are still browser sample data.
- Exact next action when resumed: finish the open Google sign-in, then verify the callback, session, and logout. After that, replace the remaining employer chart and sample company name with account records. Do not generate the final PDF until the project work is finished.
- Live database, user data, media, backups, `.env`, and Google OAuth settings were not changed for this pause. Pending Review files were not discarded. The Django server was left as it was.

## Completion, from 24 required areas

An area counts as complete only when the behavior is implemented and tested. File creation alone does not raise the percentage. Each area is one equal share of 100%.

- Total project completion: 42%.
- Work remaining: 58%.
- Development implementation: 58%. Code exists for the public board, accounts, applications, one resume upload, and admin counts. Resume library, resume builder, and a real AI provider do not.
- Testing: 25%. Targeted tests passed. The full suite was not run.
- Final verification: 20%. Several public pages were opened or checked over HTTP. Google callback, a live signed-in session, mobile layout, and the final PDF were not verified.
- Completed tasks: 4/24. Homepage navigation, company directory, job search, and contact storage.
- Remaining tasks: 20/24. Fourteen are partial. Six are not started or are prototypes only: resume library and builder, AI smart profile, AI assistant, mobile verification, final visual PDF, and the secret-free ZIP.

At an earlier browser check, Google showed its account sign-in page, but no callback reached Django. A later read-only database check found two users/profiles and no superuser, companies, jobs, or applications. This dashboard work did not change live data.

## Current phase and task

Phase: authentication verification, then dashboard account counts.

Google credentials from the updated `.env` were loaded. Both names are present and non-empty. The client ID has the Web client suffix. Django settings match the file. One SocialApp matches that ID. The site domain is `127.0.0.1:8000`. One Django listener is running after `RESTART_TALENTBRIDGEAI.bat`. No credential values were printed or overwritten.

Google Login is not complete. Continue with Google opened the real Google sign-in page for Talent Bridge AI and asked for an email or phone. This browser had no signed-in Google account, so consent, callback, session, and logout were not reached. The sign-in page was left open and unlocked.

Dashboard account rows, status counts, and the employer chart/CSV are now backed by real account records. `DashboardAccountCountTests` and the complete 85-test jobs suite passed on temporary test databases. Employer team and document controls remain explicitly browser-only previews.

## Exact next action

1. On the open Google page, sign in with the Google account that should use TalentBridgeAI.
2. Confirm the callback returns to this site, a session exists, and logout works. Mark Google Login complete only after that.
3. Continue the next unblocked product task: the resume library. Obtain user participation before claiming Google OAuth callback/session/logout verified.

## Google check after the saved credentials

Historical diagnosis, superseded by the later audit: an earlier loaded client ID had an invalid shape and produced an `invalid_client` error. A later check found the configured ID has the expected Web-client suffix. No credential values are recorded here. Consent, callback, session, and logout still need a real user-assisted test.

Required correction: replace `GOOGLE_OAUTH_CLIENT_ID` with the Web client ID from Google Cloud Console that ends with `.apps.googleusercontent.com`. Keep the secret only if it belongs to that same client. Then ask for a resume. Do not paste the values into chat.

## Latest verified page work

Privacy, Terms, and About now link to `/jobs/` and `/companies/`. All three returned HTTP 200 with those links. The About page was opened in the preview and the navigation showed Browse Jobs and Companies. Privacy and Terms were not given a separate visual screenshot. Mobile layout was NOT TESTED.

Next product task: continue the resume-library work. Dashboard integration is complete; do not restart from Phase 1.

## Exact resume point

Google OAuth consent and callback/session/logout verification are pending your participation. Product development can continue on unrelated, unblocked features; do not inspect or repeat credentials.

The earlier `invalid_client` diagnosis was superseded by a later client-ID shape check. Do not claim Google OAuth success until a real sign-in reaches the callback, establishes a session, and logs out successfully.

When you resume, the first task is to recheck that Django loaded both values, without printing them, then test the Google consent page. The client ID must end with `.apps.googleusercontent.com`. The redirect remains `http://127.0.0.1:8000/accounts/google/login/callback/`.

After Google is unblocked, the next product task is still Privacy, Terms, and About navigation, then the dashboards. Do not restart from Phase 1.

## Preserved

All current code edits remain. The database, uploads, and `backups/audit_20261112_154417/` were not changed. Pending review changes were not discarded.

## Google Login blocker

Google OAuth verification remains incomplete: consent, callback, Django session, and logout have not been tested end-to-end. A later check found the configured client ID has the expected Web-client suffix. Do not enter credentials into chat or mark OAuth complete before the real flow succeeds.

Exact next Google action, by you: in Google Cloud Console, open the Web application client and copy the Client ID that ends with `.apps.googleusercontent.com` into `GOOGLE_OAUTH_CLIENT_ID` in the private `.env`. Keep the matching secret. Restart with `RESTART_TALENTBRIDGEAI.bat`. Do not paste either value into chat.

Independent work saved: `NOTIFICATION_SETUP.md` and `INTERRUPTION_RECOVERY.md`. Sleep settings were read and not changed. Plugged-in sleep is 30 minutes. Screen off is 10 minutes on power and is not the same as sleep.

## Exact stopping point before this diagnosis

## Exact stopping point

Phase 2, public pages. No task is running. The project is not complete.

Last completed work:

- Job detail page includes Companies in the navigation. The page source no longer names Google. The sample UI/UX Designer page was opened in the preview and showed the illustrative-listing notice.
- Contact form posts to `/contact/submit/` and a valid message is stored. The page states that email is not sent. `ContactWorkflowTests`: 2 tests OK. No new inquiry was written to the live database.
- Earlier in the same development run: `/companies/` restored, homepage Companies link verified, Browse Jobs search stays on `/jobs/`.

Exact next task when work is resumed later:

1. Add the same working navigation to Privacy, Terms, and About.
2. Then connect the job-seeker and employer dashboards to the database.
3. Do not restart from Phase 1. Do not repeat the company directory, Browse Jobs search, job detail, or contact-form fixes unless a regression is found.

## Files changed and left in place

Do not use Undo All or discard these.

- `pages/job-detail.html`
- `js/job-preview.js`
- `pages/contact.html`
- `legacy-django/jobs/templates/jobs/home.html`
- `legacy-django/jobs/views.py`
- `legacy-django/jobs/tests.py`
- `legacy-django/config/urls.py`
- `index.html`
- `js/site-experience.js`
- `tools/activity_notify.ps1`
- `tools/activity_pulse.ps1`
- `LIVE_PREVIEW_README.md`
- `LIVE_PREVIEW_PROGRESS.md`
- `DEVELOPMENT_PROGRESS.md`
- `ACTIVITY_NOW.md`

Pending review: leave every editor change in place. Nothing was discarded.

## Preserved

The project database, uploaded files, and `backups/audit_20261112_154417/` were not reset or deleted. No new live contact inquiry was created during the contact test. The test database was temporary and was removed by Django.

Live status file: `ACTIVITY_NOW.md`. History: `logs/activity.log`. A Windows balloon repeats about every 2 minutes while `logs/agent_heartbeat.txt` is less than 12 minutes old. A short system sound is limited to about every 5 minutes, and only while the state is WORKING. Chat cannot send a new message while a tool is still running.

Homepage check on 2026-11-12: `http://127.0.0.1:8000/js/site-experience.js` contains Browse companies, but the open homepage directory did not show that link. Verification is not finished. One Django listener was on port 8000, PID 14888. One activity pulse was left running, PID 18496.

## Earlier pause record

No further implementation is in progress. Do not restart from Phase 1. Resume from the exact next action below.

## Current phase and exact task

Phase 2 of the Final Master prompt: live preview and page-by-page navigation.

The exact task in progress was adding the approved company directory to the homepage page directory, then confirming that link in the browser.

That code change is saved. The browser confirmation was not finished. The Final Master prompt is not complete. The PDF report, ZIP, and remaining portal features were not started in this pause window.

## Completed work

Preserved from earlier accepted work. Do not repeat it unless a regression is found.

- Step 2 startup and authentication foundation: launcher environment reload, single-server lock, stop marker, local site domain `127.0.0.1:8000`, Google SocialApp sync command, interactive superuser command, admin login CSS fix.
- Database-backed public company directory at `/companies/` and `/companies/<id>/`. Only approved companies are public. Empty state was verified earlier with HTTP 200.
- About page links to `/companies/`.
- `css/tb-foundation.css` styles the company pages.
- Company directory tests were added at the end of `legacy-django/jobs/tests.py`. Last recorded run: `ApprovedCompanyDirectoryTests` plus one public page-route test, 3 tests OK.
- Earlier recorded auth run: 46 tests OK. That run was not repeated in this pause window.
- Audit documents already on disk: `TALENTBRIDGEAI_PROJECT_AUDIT.md`, `TALENTBRIDGEAI_PAGE_DIRECTORY.md`, `TALENTBRIDGEAI_IMPLEMENTATION_PLAN.md`, `TALENTBRIDGEAI_PROGRESS.md`, Step 2 reports.

This session, before the pause:

- Confirmed one listener on port 8000. Did not start a second server.
- Opened `http://127.0.0.1:8000/` in the Cursor browser. Homepage returned the existing TalentBridge AI page, including the intro and the sample profile content.
- Added one page-directory entry in `js/site-experience.js`: Browse companies → `/companies/`.
- Requested `http://127.0.0.1:8000/js/site-experience.js` and confirmed the served file contains `Browse companies`.
- The browser accessibility tree after a normal reload still listed the old directory and did not show Browse companies. A cache-bypass reload was not run. Treat the visible link as NOT VERIFIED.
- Unlocked the browser preview before pausing.

## Files created or modified

Created by this pause:

- `DEVELOPMENT_PROGRESS.md`

Modified in the interrupted session and saved on disk:

- `js/site-experience.js` — Explore group now includes `["Browse companies", "/companies/"]` immediately after Browse jobs.

Earlier files that must stay. They were not edited in this pause:

- `tools/windows_manager.py`
- `legacy-django/jobs/management/commands/prepare_local_auth.py`
- `legacy-django/jobs/management/commands/ensure_superuser.py`
- `legacy-django/jobs/views.py`
- `legacy-django/jobs/tests.py`
- `legacy-django/config/urls.py`
- `legacy-django/jobs/templates/companies/list.html`
- `legacy-django/jobs/templates/companies/detail.html`
- `legacy-django/templates/admin/login.html`
- `css/tb-foundation.css`
- `pages/about.html`
- `RESTART_TALENTBRIDGEAI.bat`
- `CREATE_SUPERUSER.bat`
- `README_RUN_DJANGO.md`
- `STARTUP_README.md`
- `docs/troubleshooting/REMAINING_ISSUES.md`
- Step 2 and audit markdown reports listed above

Not created yet, despite the Final Master prompt asking for them:

- `LIVE_PREVIEW_README.md`
- `LIVE_PREVIEW_PROGRESS.md`
- `TalentBridgeAI_Final_Development_Report.pdf`
- `FINAL_CHANGELOG.md`
- `FINAL_TEST_REPORT.md`
- `SETUP_AND_USAGE_GUIDE.md`
- `KNOWN_ISSUES.md`
- Final delivery ZIP

## Pending review changes

Leave every existing editor change in place. Do not use Undo All, discard, or bulk-accept.

The newest unreviewed edit is `js/site-experience.js`. The Step 2 and company-directory files listed above are also still part of the saved project and should remain in review until the user accepts them.

## Current server and live preview status

- Address: `http://127.0.0.1:8000/`
- At the last check before the pause, port 8000 had one listener, PID 15436.
- `logs/setup.log` last success line: `DEVELOPMENT SERVER READY` at 2026-11-12 16:34:03, parent PID 16148, HTTP 200, autoreload enabled.
- This pause did not stop, restart, or replace that server.
- Cursor browser tab `37e106` was left on the homepage and then unlocked.
- Live preview documents were not written.
- Desktop and mobile layout checks for this session were not completed. The homepage screenshot showed the existing header and hero, with sample profiles still on the page.

## Remaining tasks and the exact next action

Exact next action when work resumes:

1. Hard-reload `http://127.0.0.1:8000/` so the browser does not use a cached `site-experience.js`.
2. Open the page directory and confirm Browse companies is visible and opens `/companies/`.
3. Record that before/after check in `LIVE_PREVIEW_PROGRESS.md`.
4. Continue Phase 2 page by page from the existing page directory. Do not rebuild completed Step 2 or company-directory code.

Still required by the Final Master prompt, and not done:

- Shared navigation and replacement of sample-only blocks on the remaining public pages.
- Job seeker, employer, and admin workflows that are still prototypes or incomplete.
- Resume library, resume builder, and configurable AI help. No AI provider is connected. Do not pretend one is.
- Google consent login: NOT TESTED.
- Admin password login: NOT TESTED. No superuser exists. Do not create one unless the user runs `CREATE_SUPERUSER.bat` and enters a password.
- Full test pass, PDF report, and secret-free ZIP.

## Errors or blockers

- Browser cache left the new directory link unverified. The file on disk and the HTTP response are updated. This is not a server crash.
- No superuser. Google consent has not been completed. No AI or SMTP credentials are configured for product features.
- Do not invent those results.
- Database was not modified in this pause. User count was last recorded as 0. Backup `backups/audit_20261112_154417/` was not touched.
- Do not enable Windows auto-startup, add a paid API, send mail, or run a schema migration without approval.

## Safe state

File edits are saved. The database was not reset. The existing server was left running. No new task was started after the pause request.


## 14 November 2026 — Critical preview, authentication route and reference-image repair
- Confirmed the supplied design board and inspected all image assets in `images/`, `logo/`, and `legacy-django/static/`.
- Root cause of VS Code preview mismatch: `.vscode/tasks.json` called `.vscode/start-django.ps1`, which contained a hardcoded old Windows workspace path and looked for the virtual environment in the wrong directory. Updated the folder-open task to call the project-managed `START_TALENTBRIDGEAI.bat` / `tools/windows_manager.py` lifecycle instead. Replaced the PowerShell file with a portable wrapper.
- Login page itself already uses Django `login_view`, CSRF token, POST `/login/`, email/password authentication and session login. Existing automated tests cover valid email/password login, invalid credentials, session creation, logout and `/pages/login.html`. The observed Firefox error is a server-not-listening condition, not proof of a broken password form.
- Integrated the supplied office image into homepage, login visual and employer banner; supplied avatar SVG into homepage candidate card; supplied Manhattan skyline into About page.
- Added `docs/homepage/REFERENCE_IMAGE_IMPLEMENTATION.md` and Django regression tests for image URLs.
- Runtime/browser test status: not run in this environment (Django package unavailable; no dependency installation/network). Do not treat local template/source checks as proof that the user's Windows server is running.

## 14 November 2026 — Reference images, login route and Django-first startup
- Replaced the stale `.vscode/start-django.ps1` task target with the project-managed `START_TALENTBRIDGEAI.bat` lifecycle. The old hardcoded workspace path was the confirmed VS Code folder-open startup defect.
- The login view is already a real Django email/password POST flow with CSRF, session login and logout. Existing auth tests verify valid login/session, invalid credentials and logout; no real user/admin password was changed.
- Added supplied office image to homepage/login/employer banner, supplied avatar SVG to the homepage candidate preview and supplied skyline image to About page. Full inventory: `docs/homepage/REFERENCE_IMAGE_IMPLEMENTATION.md`.
- Added regression tests for image markup and Django-served asset endpoints.
- Fixed `build_static.py` mapping for `resume-builder`; fixed visible field-level Resume Builder validation; fixed About canonical home link.
- Django system check: PASS. Django test suite: 138/138 PASS. Static build: PASS. Python compileall: PASS.
- QA Django server on port 8000 returned HTTP 200 for homepage, login, legacy login URL, both signup URLs, supplied image URLs and shared integration CSS. Tests used a temporary QA copy of SQLite and that copy was removed afterward.
- Browser screenshot automation was blocked by Chromium policy; actual visual browser rendering is not claimed. Windows VS Code automatic task still needs first-run confirmation on the user's PC.
- Package DB preserves user/profile/social identity rows while clearing OAuth secrets and session rows. Private `.env`, signing key, private media, backups, logs, venvs and caches are excluded.
