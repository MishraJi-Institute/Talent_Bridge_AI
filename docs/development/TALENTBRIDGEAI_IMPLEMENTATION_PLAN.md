# TalentBridgeAI implementation plan

Date: 2026-11-12

The accepted Step 2 baseline stays. Each later phase gets a backup before any schema change. No paid API, SMTP service, or Windows logon task will be added without approval.

## Phase 1 — Audit and plan

Done in this checkpoint: `TALENTBRIDGEAI_PROJECT_AUDIT.md`, `TALENTBRIDGEAI_PAGE_DIRECTORY.md`, and this plan.

## Phase 2 — Pages and visual system

Started. The first delivered screen is the approved-company directory.

Done now:

- `/companies/` lists only approved companies and shows an empty state when there are none.
- `/companies/<id>/` shows that employer and its active, non-demo jobs. Unapproved companies return 404.
- `css/tb-foundation.css` is the first shared visual layer for these new pages.
- About links to the directory.

Still in this phase:

- Apply one navigation, footer, and card system across the existing public pages without removing working forms.
- Replace sample-only blocks where a database view already exists, such as saved jobs.
- Add access-denied and authentication-error pages when those states have real views.
- Do not invent email verification until SMTP is approved.

## Phase 3 — Models for the missing workflow

Needs a dated SQLite backup first. Planned models, only when that phase starts:

- Multiple resumes per user, with one approved default.
- Application withdrawal and an explicit shortlist status.
- Profile fields the user chooses to show on a public card.

No schema change was made for the company directory. It uses the existing `Company` and `Job` models.

## Phase 4 — Authentication completion

- Keep the current Google and password code.
- Ask you to run `CREATE_SUPERUSER.bat` and then test that login.
- Test Google only after you confirm the Cloud origin and redirect URI.
- Email verification waits for SMTP approval.

## Phase 5 — Resumes

- Extend the current 5 MB PDF, DOC, and DOCX checks to a real library.
- Parsing and generation go through a provider interface.
- If no provider is configured, the builder stores only text you typed. It will not pretend to call a model and it will not invent jobs, degrees, or skills.

## Phase 6 — Profile card and matching

- Save the card on the profile, with a private-contact switch.
- Rank jobs by overlapping confirmed skills and show matched and missing skills.
- Do not rank by age, gender, religion, or other sensitive attributes.

## Phase 7 — Employer workflow

- Connect the employer dashboard to the database pages that already manage jobs and applicants.
- Add job editing, shortlist, and a simple status pipeline.

## Phase 8 — Help and notifications

- Keep the existing in-app notifications.
- Add a page-help panel that explains the current screen from local content and is labeled as guide text until an AI provider is approved.

## Phase 9 — Security and startup

- Keep the current start, stop, and single-port lock.
- Review upload and private-file rules again after the resume library exists.
- Do not enable automatic Windows startup unless you ask.

## Phase 10 — Integration and delivery

- Run the relevant tests after each phase.
- Build a ZIP only after the project works, excluding `.env`, the virtual environment, logs, and private uploads.

## Approval required before proceeding past the company directory

1. Confirm the Google Cloud origin and redirect, then perform one live sign-in.
2. Create the superuser yourself in `CREATE_SUPERUSER.bat`.
3. Choose whether resume parsing and the help assistant may call an external AI API, and provide that key outside the chat if you want it.
4. Approve SMTP only if verification email must leave this computer.
5. Approve the next schema migration before Phase 3 changes tables.
