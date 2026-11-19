# Interruption recovery

## Latest resume point — deployment security baseline

- All 133 Django tests pass and the ordinary system check is clean.
- `manage.py check --deploy` using production settings reports four
  deployment-hardening gaps: no HSTS, HTTPS redirect, secure session cookie,
  or secure CSRF cookie.
- The actual local website is served over HTTP and uses the Windows
  development launcher. Production domain and TLS/reverse-proxy details are
  unknown, so no HTTPS/HSTS flags were changed. Do not claim production
  security approval from local tests.
- Owner confirmed local-only use for now. Actual Django browser checks of 22
  public and five authentication/recovery routes at the configured mobile
  width found no horizontal overflow.
- Continue feasible local security/responsive checks. Before configuring
  production TLS behavior, obtain the intended deployment topology; SMTP,
  first-time Google signup, owner-operated Super Admin setup, AI provider,
  final PDF, and clean ZIP also remain pending.

## Latest resume point — password recovery pages

- The existing Django forgot-password route already issues signed reset links,
  and the confirm route updates the account password; this implementation was
  preserved.
- Corrected password-recovery page navigation to friendly Django routes and
  added a visible disclosure that local development reset emails appear in the
  server console rather than an inbox.
- Fixed stale relative links across Login, account-type selection, and both
  registration forms. The actual Django login, signup router, and job-seeker
  signup pages rendered with their corrected destinations.
- Both focused `PasswordResetWorkflowTests` passed, including full link
  follow-through and successful password change, plus same-response handling
  for unknown email. All 10 authentication/recovery tests passed.
  `manage.py check` passed; `_check_links.py` reported no missing references
  across 64 HTML and 37 CSS files.
- The complete Django suite passed all 133 tests in 215.6 seconds after
  updating a stale dashboard-link test assertion to match the existing
  “Resume Library” label.
- At the configured mobile viewport, Login, signup selection, both signup
  forms, and Forgot Password showed no horizontal overflow in the actual
  Django browser.
- The actual `/forgot-password/` page was inspected on the Django site. Tests
  used a temporary database; no live account records or schema were changed.
- Next: continue the remaining public/account workflow audit. SMTP delivery,
  first-time Google signup, owner-operated Super Admin setup, full
  security/responsive testing, final PDF, and clean ZIP remain incomplete.

## Latest resume point — privacy and cookie information

- Privacy now describes local Django account/profile/application/contact data,
  private resume storage, Google OAuth/Fonts, the local email backend,
  browser-only preferences, and the unavailable AI provider. It explicitly
  disclaims being a complete production legal notice.
- Cookie Preferences now explains session/CSRF cookies, browser storage, the
  lack of a consent manager, and that deleting browser data does not delete
  server-side records.
- Focused regression tests passed; the actual Django browser showed both
  pages with no horizontal overflow at the configured 390px viewport
  (effective width 300px). `_check_links.py` checked 64 HTML and 37 CSS files.
- No live records or schema changed. Continue feasible account-page work.
  Google first-time signup, owner-operated Super Admin setup, AI provider
  connection, full security/responsive testing, final PDF, and clean ZIP remain
  outstanding.

## Latest resume point — Categories, Pricing, and public pages

- Category cards now open the actual Django job search with keyword filters;
  test coverage verifies that filtering against live test-database roles.
- Pricing is explicitly illustrative. The application has no billing or
  subscriptions, the AI features are unavailable, employer signup does not
  select a paid plan, and plan inquiries go to the local Contact workflow.
  Monthly/yearly display switching was exercised in the actual browser with
  no script errors.
- About, Help, FAQ, Trust Center, Platform Status, AI Audit Center, Terms,
  Categories, Careers, Blog, and Customer Stories were corrected for backend
  reality and friendly routes. Demo content remains labeled; no live data or
  schema was changed.
- `manage.py` system check and all 12 `PageRoutingTests` passed;
  `_check_links.py` checked 64 HTML and 37 CSS files with no missing local
  references. Pricing and Categories showed no horizontal overflow at the
  configured 390px viewport (browser effective width 300px).
- Continue the remaining public/account workflow audit. OAuth first-time
  signup, owner-operated Super Admin setup, AI provider integration, full
  security/responsive testing, final PDF, and clean ZIP remain incomplete.

## Latest resume point — public information pages

- Continued from the verified Resume Builder checkpoint; the required design
  image remains visually inspected and the existing Django database/migration
  state was preserved.
- About, Help, FAQ, Trust Center, Platform Status, AI Audit Center, and Terms
  were corrected to distinguish actual account-backed Django workflows from
  labeled demo content, local development email, the absence of a public
  uptime feed, and unavailable AI generation. The About logo now links to `/`,
  the real Django homepage, not `/index.html`.
- Verification: Django system check and focused page regression tests passed;
  `_check_links.py` checked 64 HTML and 37 CSS files with no missing local
  references. The actual Django browser rendered the revised About, Help, FAQ,
  Trust Center, Platform Status, and AI Audit Center. FAQ had no horizontal
  overflow at the configured 390px width (effective browser width 300px).
- No live records or schema were changed. Continue reviewing remaining public
  and account workflows; do not claim the full project or final delivery is
  complete.

## Latest resume point — manual Resume Builder verified

- The required design board `design-references/TalentBridgeAI Premium Design
  System Board (1).png` was located and visually inspected. It depicts the
  premium recruitment homepage, analytics dashboard, and resume editor/live
  preview; the palette is `#155EEF`, `#101828`, and `#F8FAFC` with Inter and
  Manrope.
- Resumed the interrupted Builder work. The authenticated manual editor,
  account-private `ResumeDraft`, live preview, browser Print/Save as PDF, and
  AI-unavailable disclosure already existed, so no app code was overwritten.
- Confirmed `jobs.0009_resumedraft` is already applied in the existing
  database. No schema change or live record modification was made. A recent
  backup exists, but whether it predates the migration is unknown.
- Verification: `manage.py check` passed; all 12 focused Builder and
  Resume Upload/Library tests passed; `_check_links.py` found no missing local
  references across 64 HTML and 37 CSS files. The actual Django Builder route
  redirects an unauthenticated browser to login and retains its `next` path.
- Tests cover owner-scoped draft persistence/reload, escaped preview content,
  invalid-form handling, and resume upload/library workflows. A signed-in
  browser session was unavailable; do not claim a live authenticated screenshot.
- AI writing remains unavailable until a provider is configured. The next
  phase is the remaining public/account workflow audit; Google first-time
  signup, owner-operated Super Admin setup/verification, full responsive and
  security testing, final PDF, and clean ZIP remain pending.

## Latest resume point — account workflows and page activation

- Implemented `/privacy-settings/` and `/get-discovered/` for authenticated job seekers, linked from the seeker dashboard. Profiles default to private; only approved employers can search opted-in profiles, and discovery cards show no email, phone, or resume.
- Candidate Search includes applicants to the signed-in employer's own non-demo jobs and a separate, paginated opt-in profile directory.
- Saved Jobs now shows account-backed roles separately from fictional preview cards; the preview hides when real saved jobs exist, and demo/unapproved jobs cannot be saved as account records.
- Added `/access-denied/` with HTTP 403 recovery links and configured Django's 403 handler. Staff dashboard links now include user, profile, company, job, application, saved-job, notification, interview, and support-message management.
- Applied `jobs.0008_profile_is_discoverable` as an additive migration. Live aggregate counts before and after are users=2, profiles=2, companies=0, jobs=0, applications=0; both existing profiles are private and SQLite integrity is `ok`. No account records or backups were deleted or reset.
- Verification: all 119 Django tests passed; `manage.py check`, `makemigrations --check --dry-run`, and `_check_links.py` passed (62 HTML, 35 CSS). The new page routes, privacy boundaries, saved-job separation, and admin links have focused tests.
- Current inventory: 53 workflow/page entries (12 complete, 39 partial, 0 blocked, 2 not implemented); 51 active, 2 inactive; 50 friendly aliases and 60 physical HTML templates. Progress estimate: overall 59%, implementation 85%, testing 63%, verification 72%.
- Live-server recheck after the latest code changes: exactly one listener on port 8000; `/`, `/login/`, and `/__dev__/state/` returned HTTP 200; health reports server/frontend `ok` and zero errors. Privacy settings, Get Discovered, and Candidate Search returned expected anonymous HTTP 302 redirects; Access Denied returned HTTP 403. Port 5500 is separate (`/` 200, `/__dev__/state/` 404). No server was started or duplicated.
- Next: continue remaining incomplete workflows, then create the final report, genuine screenshots, and clean ZIP only when implementation is finished. AI generation remains blocked until a provider is configured; first-time Google signup and direct Cloud Console review remain unverified.

## Historical resumed checkpoint — 13 November 2026, before privacy and admin work

- Urgent Django-preview diagnosis: the original backend stayed healthy; a failed health poll could leave a stale warning, and `js/dev-preview.js` now clears it after recovery. Current verification is stronger: the shared browser is open to `http://127.0.0.1:8000/`, its screenshot has no red warning, and a visible-text check after polling found zero “Development server unavailable” messages.
- Current process/task status: no background agent is running and all shell tasks are completed. The Django autoreloader parent/worker are PIDs 3696/9548, one server tree and one listener on port 8000. Recent `server.log` requests to `/`, `/login/`, and `/__dev__/state/` returned 200 with no current traceback. `RUN_DJANGO_WINDOWS.bat` delegates to `START_TALENTBRIDGEAI.bat`; it was not run because the existing server is healthy, avoiding a duplicate.
- Port distinction: 8000 is Django (`/`, `/login/`, `/__dev__/state/` => 200). Port 5500 is a separate VS Code static preview (root => 200, `/login/` and `/__dev__/state/` => 404). The red unavailable warning is expected on 5500 because that static server has no Django health endpoint; it is not evidence that Django is down.
- A later full-suite run exposed a real `/__dev__/state/` failure: `_template_errors()` scanned allauth's installed templates outside the workspace. One external template referenced an unregistered `humanize` library, and the scanner then raised `ValueError` while formatting the external path relative to `PROJECT_ROOT`. Fixed the root scope so only project-contained app template directories are scanned; added a regression test for an external app template. The live state endpoint now returns HTTP 200 with server/frontend `ok` and zero errors.
- Current OAuth config was checked without reading or printing either value: both Django settings are present, the provider is configured, one SocialApp is linked to the active site and matches the loaded client, and the callback path resolves correctly. Two private sign-ins/consents completed, including a second login after logout: both callbacks returned 302, both protected dashboard redirects reached the Job Seeker page (200), and logout returned 302 after each. A later dashboard request redirected to login.
- New employer search is limited to applications for the owning approved company’s non-demo jobs. Remote Jobs and Startup Jobs use real filtered records and clearly labelled development-only samples when no matching live records exist. The Salary Calculator now validates gross-pay inputs and calculates pay-period estimates; the previously misleading homepage footer link now opens it.
- The read-only live SQLite check returned integrity `ok`, with 2 users, 2 profiles, and no companies, jobs, or applications. The full test suite used its temporary test database.
- Full current verification: `manage.py check` passed and `manage.py test jobs` passed all 115 tests. The four preview tests include the external-template regression; candidate search, startup/remote filters, resume workflows, salary calculations, and route tests pass. `_check_links.py` checked 59 HTML and 35 CSS files; no missing local references were found. The current PAGES map has 46 friendly aliases and 57 physical page templates; Startup Jobs and Remote Jobs are separate named routes.
- The seeker dashboard has a prominent Upload Resume link to the secure Resume Library. `/recommended-jobs/` ranks approved active non-demo roles by profile skills/location, excludes applied roles, and uses labelled non-persistent samples only in development when no live roles exist. The offline Jerry guide links to this page.
- The last private provider check found no configured AI key; the user selected OpenAI for private setup. No key was requested or displayed and no AI request was made. Two Google OAuth login/session/role redirect/logout cycles are verified; first-time signup and direct Cloud Console review remain untested.
- The resume library now supports authenticated private upload, download, replacement, and deletion for PDF, DOC, and DOCX (maximum 5 MB), plus an in-browser PDF preview. Office-format files are not sent to an external preview service; the page directs users to download them for local preview.
- Fixed a storage cleanup bug in resume replacement by preserving the old storage name before Django mutates the model field.
- The job-seeker dashboard now reads and saves account-backed name, headline, location, skills, experience, and summary fields. The Smart Card starts from those fields. Browser-only extended details and design settings are disclosed. Demo applications now appear in their own labelled tracker instead of being hidden by real account application rows.
- Employer job editing is now owner-scoped, validates input, and is linked from Manage Jobs; tests reject cross-company and demo-job edits.
- `/account-security/` provides authenticated password changes using Django's current-password validation and preserves the signed-in session. Both dashboards link to it. Email verification and MFA remain unfinished.
- The staff-only Admin dashboard now uses live metrics, separates demo job totals, and exposes permission-gated Django admin links, the employer approval queue, and recent contact messages. Non-staff access remains blocked.
- Verified: all 109 Django tests passed; resume, profile-save, dashboard-separation, recommendation, job-edit, security, Admin, and auth tests passed; `manage.py check` passed; the login page rendered in the actual browser and the dashboard redirected to login as expected; 57 HTML and 35 CSS files passed `_check_links.py`; all 44 named page aliases and 55 physical page templates passed route tests.
- Live preview remains on port 8000 and returned HTTP 200. One listener is present; do not start a second server. The read-only live database integrity/count check passed; automated tests use Django's temporary test database.
- Progress estimate: 56% overall, 82% implementation, 60% testing, 69% verification. These estimates remain coarse; 50 entries include 8 complete, 38 partial, 0 blocked, and 4 not implemented (46 active, 4 inactive).
- Exact next task: continue auditing remaining workflows. First-time Google signup and direct Cloud Console review are untested; connected AI features remain blocked until OpenAI is configured privately; Jerry remains an offline guide.
- Still blocked or incomplete: first-time Google signup and direct Cloud Console review. There is no verified external AI provider. DOC/DOCX browser rendering is not supported; download is provided. Final visual PDF, genuine saved screenshots, and clean secret-free ZIP are not created.
- A milestone notification was invoked: WAV playback, speech, and balloon request reported success; actual speaker audibility and visible delivery were not user-confirmed. No Windows audio or power settings were changed.
- Preserve the live database, private media, backups, `.env`, and existing server. No direct development edits were made to account records; OAuth sign-in was user-initiated.

## Historical checkpoint — 2026-11-13

The resume library page now clearly exposes the real authenticated upload/download workflow, supported formats and size limit, and account-specific current/empty states. Resume acceptance tests cover access control, valid PDF upload/download, invalid formats, and oversized uploads. Direct physical paths for account pages use the same permission-checked views as friendly routes. `manage.py check` passed; `manage.py test jobs` passed all 89 tests. Existing smoke tests cover all named routes and physical page templates. `_check_links.py` found no missing local references across 55 static HTML files and 35 CSS files.

At this older checkpoint, no live database data had been changed and Google consent/callback/session/logout were unverified. JavaScript syntax validation was not run because Node.js is unavailable. The broader inactive-page and full-project review remains in progress. Do not claim final project, PDF, or ZIP completion. Continue from `DEVELOPMENT_PROGRESS.md`, and preserve the existing database and private OAuth configuration.

Updated: 2026-11-12 22:50 local. Project completion is 42% across 24 required areas. 4 are complete, 20 remain. Google OAuth is not verified. Dashboard account rows and Categories, Help, FAQ, and Pricing links were saved. The live database was not modified. The Django server was left running.

## Exact resume point

The updated `.env` credentials loaded. Google accepted the client and showed its sign-in page. Consent, callback, session, and logout are not done because this browser was not signed in to Google. Leave the open Google page for the user. Do not mark Google Login complete.

Dashboard overview counts now come from account records. Sample job rows and charts remain. `DashboardAccountCountTests` passed on the temporary test database. The live database was not modified.

## Exact resume point

Google OAuth Client ID and Client Secret are pending manual configuration in the local `.env`. Development is fully stopped. The Django server was not restarted.

On the next instruction to resume:

1. Confirm both `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` load, without printing them.
2. The client ID must end with `.apps.googleusercontent.com`.
3. Restart Django only if you ask, using `RESTART_TALENTBRIDGEAI.bat`, and only if a restart is required to load the new values.
4. Test Google consent. Do not mark Google Login complete until Google accepts the client and the callback, session, and logout succeed.
5. Then continue with Privacy, Terms, and About navigation.

Do not restart from Phase 1. Do not discard pending review changes. Do not reset the database.

## Current status

Status: BLOCKED on Google Login. No feature implementation is running after this note. The project database was not changed by the OAuth diagnosis.

Resume from `DEVELOPMENT_PROGRESS.md`. Do not restart from Phase 1.

## Sleep versus screen off

Checked on 12 November 2026. The active plan is Balanced. No power setting was changed.

| Condition | Plugged in | On battery |
| --- | --- | --- |
| Turn off the screen | 10 minutes | 5 minutes |
| Sleep the computer | 30 minutes | 15 minutes |
| Hibernate | 3 hours | 3 hours |

The screen turning off does not stop the computer. Sleep does. Sleep after 30 minutes on power can interrupt a long Django session. Hybrid sleep is off.

To keep the PC awake only while plugged in, after you approve it, this is the setting and the restore value:

```text
powercfg /change standby-timeout-ac 0
```

Restore the previous plugged-in sleep time with:

```text
powercfg /change standby-timeout-ac 30
```

Leave `standby-timeout-dc` at 15 so battery use still sleeps. This was not run. Automatic sleep prevention is not active.

## If work stops

1. Read `ACTIVITY_NOW.md`. If the timestamp is old and the state is NOT WORKING, the turn ended or the PC slept.
2. Read `DEVELOPMENT_PROGRESS.md` for the exact next task.
3. Start the site again with `START_TALENTBRIDGEAI.bat` only if port 8000 is not already listening.
4. Do not create a second server.
