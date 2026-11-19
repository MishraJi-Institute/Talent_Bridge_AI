# Live preview progress

Updated: 2026-11-12 19:05 local. Preview: http://127.0.0.1:8000/

## Homepage directory link

- Page: Home, `http://127.0.0.1:8000/`
- Before: the page directory had no Browse companies link, then the link was added in `js/site-experience.js` but a cached script hid it. A later reload showed the link. Clicking it was covered by the hero heading.
- Change: confirmed the link address is `http://127.0.0.1:8000/companies/`.
- After: the directory link is present. The top navigation now also has Companies.
- Result: PASS for the link being present. The direct click was blocked by the hero, so the destination was opened from the link address.

## Company directory

- Page: Browse Companies, `http://127.0.0.1:8000/companies/`
- Before: Django 404. The running URL list had no `companies/` route. The views had been dropped from `jobs/views.py` even though the templates and tests remained.
- Change: restored `company_directory` and `public_company_detail`, and registered both routes.
- After: HTTP 200. Heading “Companies hiring on TalentBridge AI”. Empty state “No approved companies yet”. Navigation, sign-in, and register links are present.
- Result: PASS. `ApprovedCompanyDirectoryTests`: 2 tests OK. The test database was created and removed. The project database was not modified.
- Remaining: no approved companies exist, so a populated company card was not shown. Desktop screenshot captured. Mobile layout was not checked in this pass.

## Browse Jobs

- Page: Find Jobs, `http://127.0.0.1:8000/jobs/?keyword=designer`
- Before: the search form submitted to the homepage, so a search left the jobs page.
- Change: the form and the clear-filters link now use the jobs route. Companies and Browse Jobs were added to that page navigation.
- After: the preview kept `designer` in the search box. The page showed two labeled sample roles, UI/UX Designer and Product Designer, because DEBUG is on and there are no database jobs.
- Result: PASS for the search staying on the jobs page. One route test passed. Mobile layout was not checked.

