# Naukri parity — session summary (21 Nov 2026)

## Compared to Naukri.com (honest)

| Naukri | TalentBridge AI today |
|--------|------------------------|
| Search + filters | **Live** on `/jobs/` (DB + labelled DEBUG samples) |
| Login / register | **Live** on Django `:8000` |
| Resume upload (1 CV) | **Live** on `/resume-management/` after sign-in |
| Quick apply | **Live** on `/jobs/<id>/apply/` |
| Application tracking | **Live** on `/applied-jobs/` |
| Employer post + applicants | **Live** (approval required) |
| Paid Resdex / subscriptions | **Not built** (pricing page illustrative) |
| Multi-resume library | **Not built** (one file per profile) |
| Mobile app | **Not built** |

## Fixed in this session

1. **Seeker dashboard** — when employers post real jobs, dashboard **Find jobs** uses database listings; **Apply** goes to real apply URL (not browser-only demo).
2. **Broken links** — `applied-jobs`, `notifications`, `interviews`, `employee` → canonical `/resume-management/`, `/applied-jobs/`, `/jobs/`.
3. **Resume page** — explains Django `:8000` + login required (static live cannot upload).
4. **Employer posting** — demo form message points to real `/posting-job/`.
5. **Tools** — `tools/audit_feature_matrix.py`, `tools/build_naukri_parity_report.py`, route matrix JSON.

## PDF report

Open: [`docs/TalentBridgeAI_Naukri_Parity_Report.pdf`](../TalentBridgeAI_Naukri_Parity_Report.pdf)

Screenshots: `docs/screenshots/naukri-parity/before` and `after`.

## Still partial (next phases)

- Employer dashboard (`cdashboard.js`) — partly `localStorage`
- Seeker profile “worlds” / smart card — browser storage (not Naukri profile DB)
- Email job alerts — needs SMTP in `.env`
- Live domain — needs **VPS Django**; GitHub Pages is preview only

## How to verify resume upload (like Naukri)

1. `START_TALENTBRIDGEAI.bat` (Django on **8000**).
2. Sign in as **job seeker** (not only admin).
3. Open **http://127.0.0.1:8000/resume-management/**.
4. Upload PDF/DOC/DOCX (max 5 MB).