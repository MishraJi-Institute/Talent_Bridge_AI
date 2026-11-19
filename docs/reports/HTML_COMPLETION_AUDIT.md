# TalentBridge AI — HTML and Django Page Coverage

The source package contains the public marketing pages, authentication pages, job-seeker and employer workspaces, account pages, and supporting pages. The Django URL alias map and `page_view` allowlist were checked against the actual files.

## Page groups

- Public site: home, employer, job seeker, pricing, about, careers, blog, customer stories, FAQ, help, contact, privacy, terms, trust center, platform status, and AI audit center.
- Authentication: role selection, job-seeker signup, employer signup, login, social signup, forgot password, password reset, and password reset confirmation/completion.
- Job seeker: job listings/search/detail, application form/success, saved jobs, applied jobs, profile/edit profile, resume management, notifications, and interviews.
- Employer: company profile/details, job posting, manage jobs, manage applications, candidate details, interviews, and pending approval.
- Dashboards: job-seeker dashboard, employer dashboard, dashboard customization, and card organization.
- Administration: Django admin and the staff-only TalentBridge admin dashboard.

## Coverage checks

- 42 friendly Django page aliases map to existing HTML files.
- 44 HTML filenames in the Django page allowlist all exist.
- 53 HTML pages exist in the source `pages/` tree.
- The static preview build completed.
- The local HTML/CSS reference audit found no missing relative assets.

## Functional scope

The Django application includes models and views for profiles, companies, jobs, applications, saved jobs, contact inquiries, notifications, and interviews. Authenticated views handle role-based dashboards, employer approval, resume uploads/downloads, job applications, job management, and application status updates. Informational/legal pages are content pages rather than database workflows.

A source-file and syntax audit cannot prove every interactive workflow works in a real browser. Use the included Windows launcher for local Django checks and run the automated Django tests on the target Windows machine before public release.
