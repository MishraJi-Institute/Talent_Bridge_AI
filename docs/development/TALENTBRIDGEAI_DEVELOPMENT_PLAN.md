# TalentBridgeAI development plan

Date: 2026-11-12  
Status: active reference plan. Work is in progress; user-controlled authentication and external-service steps remain gated.

## Latest verified progress

- Employer dashboard company, active non-demo job, applicant/status, application-history, and interview-history data now comes from Django. The chart and CSV use those account records.
- Job-seeker application counts exclude demo jobs.
- Focused dashboard tests and Django system checks passed. The final full `manage.py test jobs` run passed all 85 tests.
- Google OAuth still needs a real user consent/callback/session/logout verification. The final PDF and ZIP are not ready.

Next unblocked feature: continue the resume-library implementation. Keep OAuth verification user-assisted and do not claim overall project completion.

The project stays in place. Later work edits the existing Django app and root frontend. It does not replace the project, reset the database, or upgrade dependencies unless a missing package is explicitly approved.

## Recommended order

1. Restart Django only after approval, so the running process loads the current `.env`. Confirm the Google button state changes only if both OAuth values load. Do not print those values.
2. Fix the duplicate empty `DJANGO_SECRET_KEY` line without rotating the populated key, so existing session cookies keep validating.
3. Set the Django site domain to `127.0.0.1:8000` and sync one Google social app. This still cannot pass a live Google login until the Cloud redirect URI is confirmed.
4. Add a superuser only when you provide the username and password, or run `createsuperuser` yourself. Do not invent or reset an account.
5. Correct admin login CSS and the stale docs that say OAuth is empty and that the launcher seeds demo data.
6. Point the job seeker dashboard at the signed-in `Profile`, real jobs, and real applications. Keep `localStorage` only for theme and layout preferences. (Account counts and application rows are connected; the broader dashboard remains partial.)
7. Point the employer dashboard at the owner's company, jobs, and applicants. Remove the hard-coded TechSphere demo from the signed-in view. (Company details, active non-demo jobs, applicants/status counts, and application/interview analytics are connected; team/documents remain previews.)
8. Make Resume Library a real list of that user's files, and stop presenting the sample resume card as a stored document.
9. Add job match scoring only after the profile and job records are connected. Start with skill overlap already stored on `Profile.skills` and `Job.skills`. Do not add an AI vendor in that pass.
10. Add AI resume parsing and an AI resume builder only after you choose a provider and supply a key. Until then, leave those features marked not implemented.

## Cross-cutting development notifications

For each major work phase, keep the existing live preview, progress tracking, checkpointing, and interruption recovery active. `ACTIVITY_NOW.md` is the live status, `logs/activity.log` is the event history, and `tools/activity_pulse.ps1` provides the existing visual heartbeat. Use `tools/activity_notify.ps1` for milestone notifications; do not notify on every edit or start another background service.

Mark these events only when they are true: task start, feature completion, test-suite completion, verified bug fix, OAuth success or failure, saved checkpoint, safe pause, resume, whole-project completion, and verified final PDF/ZIP readiness. Milestone notices request both a visible Windows balloon and a synchronous Windows sound, plus a short generic SAPI announcement when installed. Never announce success before verification or speak/log OAuth secrets.

On audio failure, record the error and keep the visual notification/status update. If all progress notification channels fail, mark the activity blocked, save a safe checkpoint, and pause rather than silently proceeding. Do not change Windows volume, audio-device selection, or system configuration. A successful playback API call is not proof that anyone heard it; record that limitation and request a listening test when actual audibility matters. Setup, invocation, and the latest machine-level checks are documented in `NOTIFICATION_SETUP.md`.

## Files for those steps

| Step | Files |
| --- | --- |
| Restart and secret-key hygiene | `tools/windows_manager.py`, private `.env` (edit in place, never print) |
| Site and Google app | `legacy-django/jobs/google_oauth.py`, site row in the database via a data migration or `sync_google_oauth` |
| Admin | `legacy-django/templates/admin/login.html` |
| Docs | `docs/troubleshooting/REMAINING_ISSUES.md`, `README_RUN_DJANGO.md` |
| Seeker dashboard | `pages/dashboard/jdashboard.html`, `js/dashboard/jdashboard.js`, `legacy-django/jobs/views.py` |
| Employer dashboard | `pages/dashboard/cdashboard.html`, `js/dashboard/cdashboard.js`, `legacy-django/jobs/views.py` |
| Resume library | `legacy-django/jobs/models.py`, a new migration, `pages/resume-management.html`, `legacy-django/jobs/views.py` |
| Skill match | `legacy-django/jobs/views.py`, `pages/job-listings.html` or `legacy-django/jobs/templates/jobs/home.html` |
| AI parsing and builder | new service module under `legacy-django/jobs/`, plus `requirements.txt` only when a provider is chosen |

## Testing required before any feature is called done

Run these against the real local server on port 8000, not `file://` and not the generated `site/` folder.

| Feature | Required checks |
| --- | --- |
| Server lifecycle | Stop, start, and restart through the Windows scripts. Homepage returns HTTP 200 after each start. Confirm a reboot or a closed console leaves port 8000 closed until the script is run again. |
| Seeker registration and login | Create a new seeker, sign out, sign in, and confirm `/dashboard/` opens the seeker dashboard. Restart Django and confirm the same browser is still signed in. |
| Employer registration and login | Create an employer, confirm publishing is blocked, approve the company as staff, then confirm a job can be posted. |
| Admin | Sign in at `/admin/login/` with the account you created. Open `/admin-dashboard/` and approve one pending company. |
| Google | With the server restarted, confirm the button is enabled only when both values load. Complete one sign-up and one sign-in in the browser, including cancel. Record failure if Google Cloud rejects the redirect. |
| Jobs | Post a job as an approved employer. Search by keyword and location. Open the detail page. Confirm sample roles are labeled and do not create applications. |
| Applications | Apply once, confirm a second apply does not duplicate, and confirm the employer can move status among pending, reviewed, and rejected. |
| Resume upload | Upload a valid PDF under 5 MB, reject a renamed non-PDF, download as the owner, and download as the hiring employer. Confirm a second user cannot download it. |
| Resume library | Upload two files and confirm both remain listed for that user only. |
| Smart profile card | Save card fields, reload, restart the browser, and confirm the saved fields come from the database rather than only `localStorage`. |
| Recruitment | Employer sees only their applicants, can open candidate details, and can schedule an interview that creates a notification. |
| Skill match | A seeker with overlapping skills sees those jobs ranked above unrelated jobs. Empty skills do not raise an error. |
| AI builder and parser | Not testable until a provider is configured. Do not mark them passed. |
| Frontend | At desktop and a narrow viewport, use the main nav, login, both dashboards, job detail, and resume page. Confirm buttons that claim to save do save. |
| Database | `manage.py check` and `showmigrations` after any migration. Confirm existing rows are still present. |

Also run `python manage.py test jobs` after code changes. A pass must be from that run, not from the earlier checkpoint.

## Notification verification required for release

For the notification system, verify at least one milestone notification during development and another at completion of this notification task or final project delivery. Record the selected WAV, synchronous playback method, audio-service/default-output checks, SAPI availability, visual notification request, and test result in `logs/activity.log` and `NOTIFICATION_SETUP.md`. Do not describe the final project or PDF/ZIP as ready until those deliverables themselves are complete and checked. If the user cannot confirm hearing the sound, explicitly keep audibility marked unconfirmed and provide the safe manual listening test.

## Needs your permission or credentials

- Approval to restart the local Django process.
- Approval before creating the first superuser, plus the username and password you want.
- Confirmation of the Google Cloud origin and redirect URI. The secret itself must stay in `.env`.
- A decision on whether sample dashboard companies and sample jobs should remain visible for demos.
- A provider choice and API key before any AI parsing or resume generation.
- SMTP host, if password reset must send real email. Local console email is enough for development.

## Out of scope until you ask

- Rebuilding the project.
- Dependency upgrades.
- Production hosting, HTTPS, or a public domain.
- Password resets of existing accounts. There are currently no accounts.
- Destructive database commands.
