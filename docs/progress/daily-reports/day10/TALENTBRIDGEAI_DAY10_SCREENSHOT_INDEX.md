# TalentBridgeAI — Day 10 Screenshot / Evidence Index

**Date:** 2026-11-18  
**Evidence directory:** `docs/audit/day10/evidence/`  
**Source copies:** Preserved originals remain under `docs/reports/day2_screenshots/` and `docs/reports/day8_screenshots/`.

No passwords, tokens, resume contents, or private candidate data are included.

| Evidence ID | Filename | Page / component | Viewport | Demonstrates | Related finding | Baseline / problem |
| --- | --- | --- | --- | --- | --- | --- |
| E-D2-01 | `login.png` | Login | Desktop (Day 2) | Sign-in UI baseline | Day 2 website baseline | Baseline |
| E-D2-02 | `page-2026-11-18T03-09-31-686Z.png` | Public page (Day 2 capture) | Desktop | Early baseline capture | Day 2 | Baseline |
| E-D2-03 | `page-2026-11-18T03-12-02-437Z.png` | Public page (Day 2 capture) | Desktop | Early baseline capture | Day 2 | Baseline |
| E-D2-04 | `page-2026-11-18T04-45-33-491Z.png` | Public page (Day 2 capture) | Desktop | Early baseline capture | Day 2 | Baseline |
| E-D8-01 | `day8_homepage_desktop.png` | Homepage `/` | Desktop | Brand hero; live stats show **0** | D8-S01 / D8-U01 | Problem (empty live counts) |
| E-D8-02 | `day8_homepage_mobile_390.png` | Homepage `/` | 390×844 | Mobile nav hamburger; no overflow | Day 8 responsive | Baseline |
| E-D8-03 | `day8_jobs_mobile_390.png` | Jobs `/jobs/` | 390×844 | Stacked search fields on mobile | Day 8 responsive | Baseline |
| E-D8-04 | `day8_contact_desktop.png` | Contact `/contact/` | Desktop | Contact form baseline | Day 8 forms | Baseline |
| E-D8-05 | `day8_contact_relative_link_404.png` | Literal `/contact/about.html` | Desktop | DEBUG 404 / URLconf disclosure | D8 residual + D9-D01 | Problem |

## Limitations
- Day 4–7 / Day 9 did not produce additional browser screenshots (settings/DB/URL/ERD/security were source + CLI verified).
- Authenticated dashboards, resume contents, and admin private data were **not** screenshot-captured (by design).
- Day 2 generic `page-*.png` filenames lack descriptive labels in original capture metadata.
