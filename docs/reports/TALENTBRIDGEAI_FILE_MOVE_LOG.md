# TalentBridgeAI — File Move Log

Date: 2026-11-18

## Session A (yesterday — preserved)

- Frontend trees → `frontend/{pages,css,js,assets}`
- Django → `backend/legacy-django` + root junction
- Docs → `docs/{architecture,setup,troubleshooting,reports,development}`
- Scripts → `scripts/{install,startup,maintenance,backup,diagnostics}` + root wrappers
- Backup: `backups/structure_20261118_002618/`

## Session B (resume — this run)

### Docs / scripts gaps
- Added `docs/installation/` (moved install guides from `docs/setup/`)
- Added `scripts/shutdown/` (STOP + DISABLE_* bats); refreshed root wrappers

### CSS organization → `frontend/css/`
| Subfolder | Examples |
| --- | --- |
| `base/` | style, tb-foundation, tb-premium-system, portal-pages, redesign, pro-upgrade |
| `components/` | site-header, site-experience, motion, dark-mode, landing-intro, auth-*, reference-image-integration, admin, dev-preview |
| `pages/` | login*, signup*, job-listings, homepage*, pricing, resume-builder, … |
| `responsive/` | responsive-all, responsive-fixes |
| `layouts/` | reserved |
| `dashboard/` | unchanged nested tree |

### JS organization → `frontend/js/`
| Subfolder | Examples |
| --- | --- |
| `core/` | script, site-experience, motion, dark-mode, landing-intro, demo-forms, tb-hero-network (new) |
| `authentication/` | google-oauth, login-10sec, company-signup, dashboard-guard |
| `jobs/` | job-listings, job-preview, posting-job, jobseaker, resume-builder |
| `dashboard/` | existing dashboard scripts |
| `components/`, `dashboards/`, `notifications/` | reserved |

### Reference updates
- HTML/CSS/JS links rewritten to nested paths
- Django tests + `views.py` premium CSS + `dev_preview.py` script path updated
- Homepage linked `tb-homepage-elevate.css` + `tb-hero-network.js`

### Homepage additions (not moves)
- `frontend/css/pages/tb-homepage-elevate.css`
- `frontend/js/core/tb-hero-network.js`
- `index.html` canvas + stylesheet/script tags

No deletes of source trees. `.env` / DB / media untouched.
