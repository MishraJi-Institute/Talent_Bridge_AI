# TalentBridgeAI page directory

Date: 2026-11-13

Status means the route exists and what it does today. PARTIAL pages are not finished product screens.

## Public

| Page | Route | Status |
| --- | --- | --- |
| Home | `/` | PARTIAL. Large existing homepage. |
| About | `/about/` | PARTIAL. Static content. Companies link added. |
| Contact | `/contact/` | COMPLETE for storing a contact message. |
| Pricing | `/pricing/` | PARTIAL. Illustrative pricing and plan concepts only; payments, subscriptions, paid entitlements, and AI plan features are not implemented. Employer signup and Contact links are live. |
| Browse jobs | `/jobs/` | PARTIAL. Database query, plus debug-only samples when empty. |
| Startup jobs | `/startup-jobs/` | PARTIAL. Filters approved company/job records for startup indicators; clearly labelled development samples appear only when no matching live records exist. |
| Remote jobs | `/remote-jobs/` | PARTIAL. Filters approved active jobs to Remote mode; labelled development samples are filter-matched and not persisted. |
| Remote Work Guide | `/remote-work-guide/` | COMPLETE as a practical guide with working links to remote roles and related resources. |
| Job details | `/jobs/<id>/` | PARTIAL. Real job records only. |
| Browse companies | `/companies/` | COMPLETE for approved employers. Empty until one is approved. |
| Company details | `/companies/<id>/` | COMPLETE for approved employers and their active jobs. |
| Categories | `/categories/` | PARTIAL. Category cards filter the Django job search by keyword; there is no dedicated category taxonomy. |
| Career resources | `/careers/`, `/blog/` | PARTIAL. Informational articles, not a resource-management or company recruiting portal. |
| Salary calculator | `/salary-calculator/` | COMPLETE for validated gross-pay conversions across pay periods and hourly estimates; tax and currency conversion are explicitly excluded. |
| FAQ | `/faq/` | PARTIAL. Static. |
| Privacy | `/privacy/` | PARTIAL. Operational summary of local Django data flows and external requests; not a full production legal notice. |
| Terms | `/terms/` | PARTIAL. Development-site usage summary; legal review and production-specific terms remain outstanding. |
| Help | `/help/` | PARTIAL. Describes working account-backed workflows and limitations; not an AI assistant. |
| Trust, cookies, status, stories | matching slugs | PARTIAL. Trust/status pages explain current capability limits; customer stories are clearly labeled illustrations, not testimonials. Cookie preferences are informational only. |

## Authentication

| Page | Route | Status |
| --- | --- | --- |
| Sign in | `/login/` | PARTIAL. Form works in code; actual page and Django navigation links were verified. A new registration was not submitted in verification. |
| Choose account type | `/signup/` | COMPLETE as a router to the two forms; actual Django destinations were verified. |
| Job seeker registration | `/signup/job-seeker/` | PARTIAL. Backend exists. Live submit not verified. |
| Employer registration | `/signup/employer/` | PARTIAL. Creates an unapproved company. |
| Google sign-in and sign-up | `/auth/social/google/` | PARTIAL. Two live sign-ins/callbacks, Job Seeker dashboard redirects, logout, and login after logout verified. First-time signup and direct Cloud Console review remain untested. |
| Forgot and reset password | `/forgot-password/`, `/password-reset/...` | PARTIAL. Signed-link flow is tested end-to-end, including password update and unknown-email response; development emails go to the server console, with no SMTP delivery configured. |
| Logout | `POST /logout/` | COMPLETE in tests. |
| Email verification | — | NOT IMPLEMENTED. |
| Access denied | `/access-denied/` | COMPLETE. A real HTTP 403 page offers sign-in, home, and support recovery links; configured as Django's 403 handler. |
| Employer pending | `/employer/pending/` | COMPLETE. |

## Job seeker

| Page | Route | Status |
| --- | --- | --- |
| Dashboard | `/dashboard/` then `/pages/dashboard/jdashboard.html` | PARTIAL. Account name, headline, location, skills, experience, summary, application count, and saved-job count are database-backed. A prominent Upload Resume action opens the secure Resume Library. Demo applications are separate and labelled; extended profile/customization remains browser-local. Dashboard styling now follows the reference palette and Inter/Manrope typography. |
| Profile and edit | `/profile/`, `/edit-profile/` | PARTIAL. Database profile form. |
| Privacy settings | `/privacy-settings/` | COMPLETE. Authenticated job seekers can enable or disable discovery; existing profiles default to private. |
| Get Discovered | `/get-discovered/` | COMPLETE. Uses the same explicit discovery preference and safe-field policy as Privacy Settings. |
| Resume library | `/resume-management/` | COMPLETE for private PDF/DOC/DOCX upload (5 MB cap), download, replacement, and deletion; PDF browser preview; DOC/DOCX must be previewed in a compatible local app. |
| Resume builder | `/resume-builder/` | PARTIAL. Authenticated account-backed manual draft, live preview, escaped output, and browser Print/Save as PDF; AI writing generation is unavailable until a provider is configured. |
| Smart profile card | inside the seeker dashboard | PARTIAL. Card content starts from account-backed profile fields; visual design/customization is saved in this browser. |
| Saved jobs | `/saved-jobs/` | PARTIAL. Account-saved live jobs are database-backed; fictional samples appear only when the account list is empty, and demo jobs cannot be saved as account records. |
| Applied jobs | `/applied-jobs/` | PARTIAL. Database list. |
| Recommended jobs | `/recommended-jobs/` | PARTIAL. Ranks approved, active, non-demo jobs by profile skills and location; excludes submitted applications. Development samples are clearly labelled and not saved. |
| Notifications | `/notifications/` | PARTIAL. Database list. |
| Account and security settings | `/account-security/` | PARTIAL. Authenticated password change validates the current password and preserves the session; email verification and additional sign-in factors are not implemented. |

## Employer

| Page | Route | Status |
| --- | --- | --- |
| Dashboard | `/pages/dashboard/cdashboard.html` | PARTIAL. Company details, active non-demo jobs, applicants/status counts, application/interview chart, and CSV are account-backed. Team/documents and some customization controls remain browser-only previews. Dashboard styling now follows the reference palette and Inter/Manrope typography. |
| Company profile | `/company-details/` | PARTIAL. Database form. No logo upload. |
| Post a job | `/posting-job/` and `POST /jobs/create/` | PARTIAL. Approved employers only. |
| Manage jobs | `/manage-jobs/` | PARTIAL. Owner-scoped pause, reactivate, and edit workflows with validation. |
| Applicants and candidate details | `/manage-applications/`, `/candidate-details/` | PARTIAL. Status is pending, reviewed, or rejected. |
| Candidate Search | `/candidate-search/` | PARTIAL. Searches the employer's own non-demo applicants and separately lists profiles explicitly opted in by job seekers. Discovery results omit email, phone, and resume. |
| Resume viewer | `/resume/download/` | PARTIAL. Owner or hiring employer only. |
| Interviews | `/interviews/` | PARTIAL. Schedule and notify. |
| Hiring pipeline and analytics | Inside the employer dashboard | PARTIAL. Real application-status counts and date-range application/interview chart; no shortlist workflow. |

## Admin

| Page | Route | Status |
| --- | --- | --- |
| Django admin login | `/admin/login/` | PARTIAL. Page renders. No superuser exists. |
| Staff overview | `/admin-dashboard/` | PARTIAL. Staff-only live counts, pending employer approvals, recent contacts, and permission-gated Django admin links; company review requires view permission and approval requires change permission. Analytics, content, settings, and audit tools remain incomplete. |
| User, profile, company, job, application, saved-job, notification, interview, and contact management | Django admin model lists | PARTIAL. The staff dashboard links to searchable, permission-checked Django admin pages. Advanced content management, audit tools, and app-specific settings remain incomplete. |

## Route availability snapshot

Updated after privacy, discovery, saved-jobs, access-denied, admin-management, and account-recovery/navigation verification: the project documents 53 page/workflow entries—12 complete, 39 partial, 0 blocked, and 2 not implemented (51 active, 2 inactive). The PAGES map contains 50 friendly aliases and 60 physical HTML page templates; Remote Jobs and Startup Jobs are two additional named filtered routes. All 133 Django tests and `_check_links.py` pass. Route availability is not equivalent to full product completeness; pages still marked PARTIAL or NOT IMPLEMENTED remain unfinished.
