# Reference Image Implementation Inventory

Source inspected: `design-references/TalentBridgeAI Premium Design System Board (1).png` and the image assets in `images/`, `logo/`, and `legacy-django/static/`.

The design board is used as a visual specification only. It is not embedded as a substitute for functional website pages.

| Original filename | Destination / served path | Page or component | Implementation |
|---|---|---|---|
| `images/Airy Futuristic Office with City Views(1).png` | `/images/Airy%20Futuristic%20Office%20with%20City%20Views(1).png` | Homepage hero visual layer; Login visual panel; Employer dashboard banner | Added to real homepage/login templates and employer banner CSS. |
| `images/avatar_rahul.svg` | `/images/avatar_rahul.svg` | Homepage illustrative candidate profile card | Replaced the inline candidate drawing with the supplied local SVG avatar (initials RM). |
| `images/Manhattan Skyline at Dusk.png` | `/images/Manhattan%20Skyline%20at%20Dusk.png` | About page story section | Added as a responsive editorial image, not as a page screenshot. |
| `images/talentbridge-mark.svg` | `/images/talentbridge-mark.svg` | Existing brand mark / favicon | Retained existing use. |
| `images/jerry-mascot.png` | `/images/jerry-mascot.png` | Existing Job Seeker dashboard guide | Retained existing use in the dashboard. |
| `images/avatar_priya.svg` | `/images/avatar_priya.svg` | Available illustrative avatar asset | Not inserted into a real-user dashboard to avoid implying a real candidate identity. |
| `images/avatar_amit.svg` | `/images/avatar_amit.svg` | Available illustrative avatar asset | Not inserted into a real-user dashboard to avoid implying a real candidate identity. |
| `images/loginpageimage.jpg` | `/images/loginpageimage.jpg` | Existing decorative image asset | Not used; collage is not a good fit for the current login panel and would compete with the supplied office image. |
| `images/Loginpage.jpg` | `/images/Loginpage.jpg` | Existing abstract green visual | Not used; its visual style conflicts with the blue reference palette. |
| `images/talentbridge_nyc_skyline.png` | `/images/talentbridge_nyc_skyline.png` | Existing static homepage preview screenshot | Not used as a website hero because it is a screenshot of a different page, not an independent content image. |
| `images/logo_flipkart.svg`, `images/logo_microsoft.svg`, `images/logo_zoho.svg`, `images/logo_tcs.svg` | `/images/<filename>` | Existing company/logo assets | Retained as supplied; no new third-party logo placements were invented. |
| `logo/TalentBridgeAI.png` | `logo/TalentBridgeAI.png` | Existing brand artwork | Retained; existing logo references were not replaced. |
| `legacy-django/static/admin/...` image files | Django admin static paths | Existing admin login/background styling | Retained in place; no originals removed. |
| `design-references/TalentBridgeAI Premium Design System Board (1).png` | Design reference only | Homepage, employer dashboard, resume editor, design system blueprint | Inspected as the primary layout/color/component specification; not rendered as a website screenshot. |

## Template and stylesheet changes

- `index.html`: added local office backdrop and replaced the inline candidate portrait with `avatar_rahul.svg`.
- `pages/login.html`: added the supplied office image as a decorative layer behind the existing Django login panel; form action remains `/login/` with CSRF protection.
- `pages/about.html`: added the Manhattan skyline editorial section.
- `pages/dashboard/cdashboard.html`: loads the shared reference-image integration stylesheet.
- `pages/dashboard/jdashboard.html`: loads the shared reference-image integration stylesheet; existing Jerry mascot remains.
- `pages/resume-builder.html` and `pages/resume-management.html`: load shared integration stylesheet for consistent image/layout behavior.
- `css/dashboard/dashboard-polish.css`: replaced the external Unsplash employer banner with the local supplied office image.
- `css/reference-image-integration.css`: adds responsive image layout and overlay rules.

## Automated verification added

`legacy-django/jobs/tests.py` now includes regression tests that assert the homepage, login page, About page and three image URLs are present/served by Django's URL configuration.

## Verification status

Verification performed against a temporary QA copy of the uploaded SQLite database: Django system check passed; the real Django server returned HTTP 200 for `/`, `/login/`, `/pages/login.html`, both signup routes, the three integrated image assets and the shared CSS file. The image endpoints returned their expected SVG/PNG content types and non-empty bodies. Browser screenshot automation was attempted but Chromium navigation was blocked by the execution environment policy (`ERR_BLOCKED_BY_ADMINISTRATOR`), so browser-visible visual rendering is not claimed. The Windows VS Code folder-open task must still be confirmed on the user's PC.
