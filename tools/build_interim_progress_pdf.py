"""Build the pause-checkpoint interim PDF. No secrets and no invented screenshots."""
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "TalentBridgeAI_Interim_Progress_Report.pdf"


def main():
    styles = getSampleStyleSheet()
    title = ParagraphStyle("Title2", parent=styles["Title"], fontName="Times-Bold", fontSize=16, leading=20, spaceAfter=8)
    heading = ParagraphStyle("H2", parent=styles["Heading2"], fontName="Times-Bold", fontSize=12, leading=15, spaceBefore=10, spaceAfter=4)
    body = ParagraphStyle("Body2", parent=styles["BodyText"], fontName="Times-Roman", fontSize=10, leading=13, spaceAfter=4)
    sections = [
        ("TalentBridgeAI interim progress report", title),
        ("Pause checkpoint, 12 November 2026, 22:51 local. This PDF was written while development stayed paused. It is not the final visual report. The project is not complete.", body),
        ("1. Completion basis", heading),
        ("Twenty-four required areas are weighted equally. An area is complete only when the behavior is implemented and tested. Creating a file or changing a layout does not raise the percentage by itself.", body),
        ("Total project completion: 42 percent. Work remaining: 58 percent. Development implementation: 58 percent. Testing: 25 percent. Final verification: 20 percent. Completed tasks: 4 of 24. Remaining tasks: 20 of 24. The four completed areas are homepage navigation, the company directory, job search, and contact storage. Fourteen areas are partial. Six are not started or are prototypes only: resume library and builder, AI smart profile, AI assistant, mobile verification, the final visual PDF, and the secret-free ZIP.", body),
        ("2. Completed development tasks", heading),
        ("The existing Django project was kept. Step 2 foundation work remains: environment reload on restart, a single-server lock, site domain 127.0.0.1:8000, Google SocialApp sync, an interactive superuser command, and an admin login style fix.", body),
        ("Public pages verified in this development run: the approved-company directory at /companies/ and /companies/id/. The homepage Companies link. Browse Jobs search stays on /jobs/. Job detail navigation includes Companies, and the sample role no longer names Google. The contact form posts to /contact/submit/ and stores a valid message. About, Privacy, and Terms link to /jobs/ and /companies/. About was opened in the browser. Privacy and Terms returned HTTP 200. Categories, Help, FAQ, and Pricing also link to /jobs/ and /companies/ and each returned HTTP 200. They were not given separate visual screenshots.", body),
        ("Dashboard work: unsigned dashboard visits redirect to /login/. Seeker and employer dashboards link to the database pages. Application and saved-job counts, employer job and applicant counts, seeker application rows, and employer job and applicant rows are rendered from account records. The employer chart and the sample company name on that dashboard are still browser sample data. DashboardAccountCountTests passed once on Django's temporary test database. No logged-in dashboard screenshot was saved.", body),
        ("3. Frontend and backend", heading),
        ("Frontend edits include index.html, pages/about.html, pages/privacy.html, pages/terms.html, pages/contact.html, pages/job-detail.html, pages/categories.html, pages/help.html, pages/faq.html, pages/pricing.html, pages/dashboard/jdashboard.html, pages/dashboard/cdashboard.html, js/site-experience.js, js/job-preview.js, js/dashboard/jdashboard.js, and js/dashboard/cdashboard.js.", body),
        ("Backend edits include legacy-django/jobs/views.py, legacy-django/jobs/tests.py, and legacy-django/config/urls.py. Company templates live under legacy-django/jobs/templates/companies/. The contact, company, job, application, saved-job, and dashboard account queries use the existing models. No new schema migration was made for this checkpoint.", body),
        ("4. Database", heading),
        ("The live file is database/TalentBridgeAI.sqlite3, 323,584 bytes, last write time 12 November 2026 22:35:03. A read-only count at PDF creation, with no identities printed: 1 user, 0 superusers, 0 companies, 0 jobs, 0 applications, 0 contact inquiries, and 1 Google social account. That user is active, is not staff, and has an unusable password, which is the normal shape for a social-only account. Earlier in the same evening the counts were 0 users and 0 social accounts. This PDF did not create that account and did not recheck the browser session or logout. The backup backups/audit_20261112_154417/ was not modified. Automated tests used a temporary database and removed it.", body),
        ("5. Authentication and Google OAuth", heading),
        ("The project reads GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET. Values are not printed here. After the manual update, both names were present and non-empty, the client ID had the Web client suffix, Django matched the file, and one SocialApp matched that ID on site 127.0.0.1:8000. Django was restarted once so the new environment loaded. One listener remained on port 8000.", body),
        ("Google accepted the client and showed its account sign-in page for Talent Bridge AI. The redirect used by the project is http://127.0.0.1:8000/accounts/google/login/callback/. At the 22:51 pause, the open browser was still on Google's sign-in step and no callback had been confirmed by the agent. The later database row shows a Google account was linked. Callback handling, an active site session, and logout were not verified for this PDF, so Google Login is not marked complete. There is still no superuser. Admin password login is NOT TESTED. Email is not sent. The offline page guide is not an AI provider.", body),
        ("6. Tests and actual results", heading),
        ("PASS: ApprovedCompanyDirectoryTests, 2 tests. PASS: LandingPageTests.test_jobs_route_keeps_job_search_page, 1 test. PASS: ContactWorkflowTests, 2 tests. PASS: DashboardAccountCountTests, 1 test, including account rows. An earlier auth run of 46 tests was not repeated. The full suite is NOT TESTED. Mobile layouts are NOT TESTED. Google callback, session, and logout are NOT TESTED. Admin password login is NOT TESTED.", body),
        ("7. Website and server at PDF creation", heading),
        ("http://127.0.0.1:8000/ returned HTTP 200. Port 8000 had one listener, process 12384. The server was not restarted or replaced while this PDF was created. Development remains paused.", body),
        ("8. Screenshots", heading),
        ("Before screenshots were not saved in the project for the completed tasks. Browser views of the homepage, company directory, Browse Jobs, sample job detail, About, the login page, and Google's sign-in page happened during development, but those images were not saved under docs/progress/screenshots/. This PDF does not embed them and does not invent replacements. Mark every before-and-after pair for this checkpoint as unavailable.", body),
        ("9. Pending tasks and known issues", heading),
        ("Finish Google verification: callback, Django session, and logout. Replace the employer chart and sample company name with account records. Seeker job cards inside the dashboard are still sample browser data. Resume library, parsing, builder, and export are not done. AI smart profile and AI help are not connected. Employer editing, shortlist, and analytics are incomplete. Admin login has no superuser. Mobile layout is not verified. The final visual PDF and the secret-free ZIP are not created. Sample roles can still appear on Browse Jobs when DEBUG is on and the database has no jobs.", body),
        ("10. Exact next action after an explicit resume", heading),
        ("Verify the Google callback, the Django session, and logout before marking Google Login complete. Then replace the remaining sample employer chart and company name. Do not restart from Phase 1. Do not discard pending Review changes. Do not reset the database.", body),
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="TalentBridgeAI interim progress report",
    )
    flow = []
    for text, style in sections:
        flow.append(Paragraph(text, style))
        if style == title:
            flow.append(Spacer(1, 4))
    document.build(flow)
    data = OUTPUT.read_bytes()
    if not data.startswith(b"%PDF") or b"%%EOF" not in data[-2048:]:
        raise SystemExit("PDF verification failed")
    import base64
    import re
    import zlib

    text = []
    for match in re.finditer(rb"stream\n(.*?)~>endstream", data, re.S):
        raw = match.group(1) + b"~>"
        text.append(zlib.decompress(base64.a85decode(raw, adobe=True)).decode("latin1"))
    blob = "\n".join(text)
    visible = "".join(re.findall(r"\((?:\\.|[^\\)])*\)", blob)).replace("\\(", "(").replace("\\)", ")")
    required = (
        "42 percent",
        "DashboardAccountCountTests",
        "NOT TESTED",
        "323,584",
        "unavailable",
        "were not verified",
        "HTTP 200",
        "22:51",
    )
    missing = [item for item in required if item not in visible]
    if missing:
        raise SystemExit("PDF text missing: " + ", ".join(missing))
    print(f"PDF_OK BYTES {len(data)} TEXT {len(visible)}")


if __name__ == "__main__":
    main()
