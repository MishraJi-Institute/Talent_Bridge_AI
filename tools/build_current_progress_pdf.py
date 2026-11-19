"""Build the interim progress PDF from recorded project facts. No secrets."""
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "TalentBridgeAI_Current_Progress_Report.pdf"


def main():
    styles = getSampleStyleSheet()
    title = ParagraphStyle("Title2", parent=styles["Title"], fontName="Times-Bold", fontSize=16, leading=20, spaceAfter=8)
    heading = ParagraphStyle("H2", parent=styles["Heading2"], fontName="Times-Bold", fontSize=12, leading=15, spaceBefore=10, spaceAfter=4)
    body = ParagraphStyle("Body2", parent=styles["BodyText"], fontName="Times-Roman", fontSize=10, leading=13, spaceAfter=4)
    sections = [
        ("TalentBridgeAI current progress report", title),
        ("Interim snapshot, 12 November 2026, about 20:47 local. This is not the final delivery report. The project is not complete.", body),
        ("1. Original project condition", heading),
        ("The existing Django project was already present. The jobs app, SQLite database, public HTML pages, authentication code, and Windows start scripts were in place. Step 2 foundation repair had been accepted: startup environment reload, a single-server lock, the local site domain, Google SocialApp sync, an interactive superuser command, and an admin login CSS fix. No superuser existed. Google consent and an admin password login had not been tested. Dashboards were still partly browser-storage prototypes.", body),
        ("2. Work completed so far", heading),
        ("Phase 1, audit and plan: written and preserved. Phase 2, public pages: started and not finished. Later phases for dashboards, resumes, AI, employer workflow completion, the final PDF, and the ZIP have not been completed.", body),
        ("Verified in this development run: the approved-company directory was restored at /companies/ and /companies/&lt;id&gt;/. The homepage shows a Companies link. Browse Jobs search stays on /jobs/. The job detail page includes Companies and its HTML source no longer names Google. The contact form posts to /contact/submit/ and the recording endpoint test passed.", body),
        ("3. Pages created or modified", heading),
        ("Created earlier and still present: company directory templates under legacy-django/jobs/templates/companies/. Modified: index.html, pages/about.html, pages/job-detail.html, pages/contact.html, js/site-experience.js, js/job-preview.js, and the Browse Jobs template. Many other public pages already existed and were not redesigned in this run.", body),
        ("4. Screenshots", heading),
        ("The Cursor preview showed the homepage, the company empty state, Browse Jobs with the designer search, the sample job detail page, and the contact form. Those images were not saved as files in this project, so this PDF does not embed them. No screenshot is invented here.", body),
        ("5. Files created or modified", heading),
        ("Created: DEVELOPMENT_PROGRESS.md, ACTIVITY_NOW.md, LIVE_PREVIEW_README.md, LIVE_PREVIEW_PROGRESS.md, tools/activity_notify.ps1, tools/activity_pulse.ps1, company directory templates, and this PDF. Modified and left in place: pages/job-detail.html, js/job-preview.js, pages/contact.html, the Browse Jobs template, jobs/views.py, jobs/tests.py, config/urls.py, index.html, js/site-experience.js, and the progress documents. Pending editor review was left intact. Nothing was discarded.", body),
        ("6. Features actually implemented", heading),
        ("Password and Google configuration code exists. The Google button depends on environment values and was previously observed as enabled after a restart. Live Google consent is NOT TESTED. Public job search, approved-company directory, contact inquiry storage, resume upload checks for one file, saved jobs, applications, interviews, and employer approval views exist in the Django app. This run verified only the items named in the test section.", body),
        ("7. Partially implemented", heading),
        ("Homepage, about, pricing, categories, help, privacy, terms, login, registration, password reset, seeker and employer dashboards, resume management, notifications, job posting, and admin dashboard. Sample roles still appear on Browse Jobs when DEBUG is on and no database jobs exist. They are labeled sample roles.", body),
        ("8. Not yet implemented", heading),
        ("Resume library for multiple files, resume builder, PDF and DOCX resume export, a real AI provider, smart profile card saved from confirmed profile data, context-aware AI help beyond the offline page guide, job editing, shortlist pipeline, full admin analytics, email verification, and the final ZIP. Email is not sent.", body),
        ("9. Tests and real results", heading),
        ("PASS: ApprovedCompanyDirectoryTests, 2 tests. PASS: LandingPageTests.test_jobs_route_keeps_job_search_page, 1 test. PASS: the empty-listing sample-role test when addressed on the correct class. PASS: ContactWorkflowTests, 2 tests. An earlier attempt to run the jobs search test on PageRoutingTests failed because that method is not on that class; the test itself passed when run on LandingPageTests. A previously recorded auth run of 46 tests was not repeated for this PDF. The full suite is NOT TESTED in this snapshot. Google consent: NOT TESTED. Admin password login: NOT TESTED. Mobile layouts: NOT TESTED.", body),
        ("10. Bugs and root causes", heading),
        ("A Windows taskkill made Django exit with code 1, and the launcher treated that as a crash. That was fixed earlier with a stop marker. The company routes were missing from the running URL configuration, so /companies/ returned 404 even though templates and tests existed. The Browse Jobs form submitted to the homepage, so the search left the jobs page. The contact form posted to the contact page view, which does not record an inquiry. The job detail sample markup named Google before the script replaced it.", body),
        ("11. Fixes and verification", heading),
        ("Company routes were restored. /companies/ returned HTTP 200 and the empty state, and 2 directory tests passed. The jobs form now uses the jobs route; the designer search stayed on the page and 1 route test passed. The contact form now uses contact_submit; 2 contact tests passed and no inquiry was written to the live database. The job detail source no longer contains Google, confirmed by a later page fetch. The first fetch in the same session still contained Google, before the file change was being served.", body),
        ("12. Server and live preview", heading),
        ("At the check for this PDF, port 8000 had one listener, PID 1288. The preview address remains http://127.0.0.1:8000/. CSS and JavaScript are served with Cache-Control no-store while DEBUG is on. A second server was not started.", body),
        ("13. Notification system", heading),
        ("tools/activity_notify.ps1 writes ACTIVITY_NOW.md and logs/activity.log, shows a Windows balloon, and can play C:\\Windows\\Media\\Windows Notify.wav. Recorded results include PLAYSYNC_OK and BALLOON_SHOWN. A Realtek audio device reported Status OK. Speaker output was not heard from this session, so sound reaching the user is NOT VERIFIED. The two-minute pulse reports WORKING only while a fresh heartbeat exists. Chat messages are not sent every two minutes.", body),
        ("14. Database", heading),
        ("database/TalentBridgeAI.sqlite3 is 323,584 bytes. Counts at this snapshot: 0 users, 0 superusers, 0 companies, 0 jobs, 0 applications, 0 contact inquiries. Automated tests used a temporary test database and removed it. The backup backups/audit_20261112_154417/ was not modified. The database file timestamp changed at 19:59:33 without a count change.", body),
        ("15. External configuration", heading),
        ("Google Login: configuration code and a prior settings load were recorded. Live consent is NOT TESTED. Admin Login: the login page was repaired earlier. Password login is NOT TESTED because there is no superuser. AI provider: not connected. Do not treat the offline page guide as an AI model. Email: not configured. Contact messages are stored and not mailed.", body),
        ("16. Pending review", heading),
        ("All listed file edits remain for review. Do not use Undo All. No review item was discarded while preparing this PDF.", body),
        ("17. Remaining work, in order", heading),
        ("Finish public navigation on Privacy, Terms, and About. Connect seeker and employer dashboards to the database. Complete resume library and builder without pretending an AI model is connected. Finish employer and admin workflows. Run the broader test set. Produce the final PDF and the secret-free ZIP. Ask before a schema migration, a paid API, SMTP, a superuser password, or a Windows power-setting change.", body),
        ("18. Exact next development task", heading),
        ("Add the working Companies and Browse Jobs navigation to Privacy, Terms, and About, then verify those pages in the browser. Do not restart from Phase 1.", body),
        ("Windows sleep, checked and not changed", heading),
        ("The active plan is Balanced. On AC power the computer sleeps after 30 minutes and the screen turns off after 10 minutes. On battery the computer sleeps after 15 minutes and the screen turns off after 5 minutes. Hibernate is 3 hours on both. Hybrid sleep is off. Screen off is not the same as computer sleep. No power setting was changed for this report.", body),
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm, title="TalentBridgeAI current progress report")
    flow = []
    for text, style in sections:
        flow.append(Paragraph(text, style))
        if style == title:
            flow.append(Spacer(1, 4))
    document.build(flow)
    data = OUTPUT.read_bytes()
    if not data.startswith(b"%PDF") or b"%%EOF" not in data[-1024:]:
        raise SystemExit("PDF verification failed")
    print(f"PDF_OK {OUTPUT} BYTES {len(data)} PAGES {data.count(b'/Type /Page') - data.count(b'/Type /Pages')}")


if __name__ == "__main__":
    main()
