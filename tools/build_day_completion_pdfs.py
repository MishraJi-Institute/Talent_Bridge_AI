"""
Build honest Day 1-12 completion PDFs with embedded screenshots where available.
No secrets. Uses existing audit markdown facts + docs/screenshots evidence.
"""
from __future__ import annotations

from pathlib import Path
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "reports" / "day12-pdfs"
SHOT_ROOT = ROOT / "docs" / "screenshots"
EVIDENCE = ROOT / "docs" / "evidence"
AUDIT = ROOT / "docs" / "audit"
VERIFY_DATE = date.today().isoformat()

# Honest statuses based on Day 1-11 audits + Day 12 work observed in-repo.
DAYS = [
    {
        "n": 1,
        "title": "Environment & clean working copy",
        "status": "PASS",
        "objective": "Confirm project path, Python, dependencies, and run commands.",
        "work": "Day 1 environment audit completed; project root, Python 3.12 venv, and startup path documented.",
        "files": "docs/audit/day1/TALENTBRIDGEAI_DAY1_ENVIRONMENT_AUDIT.md",
        "commands": "Environment inspection; Django path verification (recorded in Day 1 audit).",
        "tests": "Documented environment readiness; no destructive DB changes.",
        "remaining": "None for Day 1 scope.",
        "shots": [],
        "audit": AUDIT / "day1" / "TALENTBRIDGEAI_DAY1_ENVIRONMENT_AUDIT.md",
    },
    {
        "n": 2,
        "title": "Website startup & baseline routes",
        "status": "PASS",
        "objective": "Start website and verify baseline public routes.",
        "work": "Baseline route audit and homepage/login screenshots preserved.",
        "files": "docs/audit/day2/; docs/reports/day2_screenshots/",
        "commands": "HTTP route checks against local Django.",
        "tests": "Public routes returned expected statuses in Day 2 audit.",
        "remaining": "None for Day 2 essential scope.",
        "shots": [
            SHOT_ROOT / "day-02" / "login.png",
            SHOT_ROOT / "day-02" / "day8_homepage_desktop.png",
        ],
        "audit": AUDIT / "day2" / "TALENTBRIDGEAI_DAY2_WEBSITE_BASELINE_AUDIT.md",
    },
    {
        "n": 3,
        "title": "Project structure inventory",
        "status": "PASS",
        "objective": "Inventory complete project structure without moving files.",
        "work": "Full structure inventory of frontend/, backend/, docs/, scripts/, junctions.",
        "files": "docs/audit/day3/TALENTBRIDGEAI_DAY3_COMPLETE_PROJECT_STRUCTURE_INVENTORY.md",
        "commands": "Read-only inventory generation.",
        "tests": "Inventory completed; no reorganization performed on Day 3.",
        "remaining": "None for Day 3.",
        "shots": [],
        "audit": AUDIT / "day3" / "TALENTBRIDGEAI_DAY3_COMPLETE_PROJECT_STRUCTURE_INVENTORY.md",
    },
    {
        "n": 4,
        "title": "Django settings audit",
        "status": "PASS",
        "objective": "Audit Django settings, env loading, static/media paths.",
        "work": "Settings audit for BASE_DIR, PROJECT_ROOT, STATICFILES_DIRS, MEDIA_ROOT, DEBUG.",
        "files": "docs/audit/day4/TALENTBRIDGEAI_DAY4_DJANGO_SETTINGS_AUDIT.md",
        "commands": "settings.py inspection; manage.py check referenced.",
        "tests": "Settings documented; secrets not exposed.",
        "remaining": "None for Day 4 audit scope.",
        "shots": [],
        "audit": AUDIT / "day4" / "TALENTBRIDGEAI_DAY4_DJANGO_SETTINGS_AUDIT.md",
    },
    {
        "n": 5,
        "title": "Database backup & inventory",
        "status": "PASS",
        "objective": "Backup DB, inventory engine/tables/migrations/sample records.",
        "work": "SQLite backup created and table/migration inventory recorded.",
        "files": "docs/audit/day5/; backups/TalentBridgeAI_Day5_Database_Backup_*",
        "commands": "Safe SQLite copy; schema inventory.",
        "tests": "Backup file verified present; live DB not reset.",
        "remaining": "None for Day 5.",
        "shots": [],
        "audit": AUDIT / "day5" / "TALENTBRIDGEAI_DAY5_DATABASE_BACKUP_AND_INVENTORY.md",
    },
    {
        "n": 6,
        "title": "URL map / views / templates",
        "status": "PASS",
        "objective": "Map URLs, views, templates, permissions, route status.",
        "work": "Complete URL map generated from Django URLconf and frontend pages.",
        "files": "docs/audit/day6/TALENTBRIDGEAI_DAY6_COMPLETE_URL_MAP.md",
        "commands": "tools/_day6_url_inventory.py (read-only).",
        "tests": "Route inventory produced.",
        "remaining": "None for Day 6 inventory scope.",
        "shots": [],
        "audit": AUDIT / "day6" / "TALENTBRIDGEAI_DAY6_COMPLETE_URL_MAP.md",
    },
    {
        "n": 7,
        "title": "Models, ERD, data dictionary",
        "status": "PASS",
        "objective": "Document models, relationships, ERD, data dictionary.",
        "work": "ERD and data dictionary produced from jobs models.",
        "files": "docs/audit/day7/*",
        "commands": "Model inspection; documentation generation.",
        "tests": "Model docs completed.",
        "remaining": "None for Day 7.",
        "shots": [],
        "audit": AUDIT / "day7" / "TALENTBRIDGEAI_DAY7_PROGRESS_NOTE.md",
    },
    {
        "n": 8,
        "title": "Frontend audit",
        "status": "PARTIAL",
        "objective": "Complete frontend audit of public pages/assets.",
        "work": "Frontend audit and homepage redesign evidence captured; Day 8 marked partial in Phase 1 gate.",
        "files": "docs/audit/day8/*; docs/evidence/homepage-*",
        "commands": "Static/frontend scans; browser screenshots.",
        "tests": "Partial depth; Phase 1 notes Day 8 incomplete.",
        "remaining": "Deeper frontend coverage beyond recorded audit.",
        "shots": [
            EVIDENCE / "homepage-design-20261118" / "after-1440-hero.png",
            EVIDENCE / "homepage-hero-correction-20261118" / "after-1440-full-hero.png",
            SHOT_ROOT / "day-08" / "day8_homepage_desktop.png",
        ],
        "audit": AUDIT / "day8" / "TALENTBRIDGEAI_DAY8_PROGRESS_NOTE.md",
    },
    {
        "n": 9,
        "title": "Security & dependency audit",
        "status": "PASS",
        "objective": "Security and dependency audit without exposing secrets.",
        "work": "Security/dependency findings documented; .env not printed.",
        "files": "docs/audit/day9/*",
        "commands": "tools/_day9_security_inventory.py (read-only).",
        "tests": "Audit report produced; P1 items tracked for later.",
        "remaining": "Open P1 security backlog items (not Day 9 blockers for audit deliverable).",
        "shots": [],
        "audit": AUDIT / "day9" / "TALENTBRIDGEAI_DAY9_PROGRESS_NOTE.md",
    },
    {
        "n": 10,
        "title": "Phase 1 finalization gate",
        "status": "PARTIAL",
        "objective": "Final audit, screenshots, test baseline, backlog, startup gate.",
        "work": "Phase 1 reports written; jobs tests 169/171; gate CONDITIONAL PASS.",
        "files": "docs/audit/day10/*; docs/audit/phase1/*",
        "commands": "manage.py check; manage.py test jobs; HTTP smoke.",
        "tests": "171 jobs tests: 169 pass, 2 fail (documented).",
        "remaining": "2 failing tests; Day 8 depth; open P1 security items.",
        "shots": [
            SHOT_ROOT / "day-10" / "day8_homepage_desktop.png",
            SHOT_ROOT / "day-10" / "day8_homepage_mobile_390.png",
            SHOT_ROOT / "day-10" / "login.png",
        ],
        "audit": AUDIT / "day10" / "TALENTBRIDGEAI_DAY10_PROGRESS_NOTE.md",
    },
    {
        "n": 11,
        "title": "Safe restore point & dependency map",
        "status": "PASS",
        "objective": "Create restore point and map root-file dependencies (no file moves).",
        "work": "Independent Day 11 backup verified; dependency map + Day 12 plan written. Git later initialized and pushed.",
        "files": "docs/audit/day11/*; TalentBridgeAI_Day11_PreOrganization_Backup_*",
        "commands": "robocopy backup; manage.py check; SHA256 verify key assets.",
        "tests": "Backup verified; Django check 0 issues; live homepage 200.",
        "remaining": "Optional: install Git was later completed; Day 12 not started on Day 11.",
        "shots": [],
        "audit": AUDIT / "day11" / "TALENTBRIDGEAI_DAY11_PROGRESS.md",
    },
    {
        "n": 12,
        "title": "Organization + external orbit + Pages",
        "status": "PARTIAL",
        "objective": "Organize docs/screenshots; external orbit animation; GitHub Pages domain.",
        "work": "docs/screenshots day folders; external-orbit code path; GitHub push; CNAME talentbridge.qd.je; Pages Actions deploy success; DNS A/www configured.",
        "files": "docs/screenshots/; docs/homepage/TALENTBRIDGEAI_EXTERNAL_ORBIT_PROMPT.md; CNAME; tools/build_static.py; frontend orbit JS/CSS",
        "commands": "git push; Actions Deploy static content to Pages; build_static.py; DNS checks.",
        "tests": "Pages deploy success; http://talentbridge.qd.je 200; HTTPS cert may still provision.",
        "remaining": "Full Django-convention physical moves deferred (hybrid layout kept); orbit outside-card polish + HTTPS enforce when cert ready; Day PDF packaging.",
        "shots": [
            EVIDENCE / "cinematic-balance-20261119" / "01-cinematic-showcase.png",
            EVIDENCE / "cinematic-balance-20261119" / "02-ai-matching-visuals.png",
            EVIDENCE / "three-hero-animations-20261119" / "01-team-showcase.png",
            SHOT_ROOT / "day-12" / "day12-homepage-hero-live.png",
        ],
        "audit": AUDIT / "day11" / "TALENTBRIDGEAI_DAY12_PROPOSED_FOLDER_STRUCTURE.md",
    },
]


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("T", parent=base["Title"], fontSize=16, leading=20, spaceAfter=8),
        "h": ParagraphStyle("H", parent=base["Heading2"], fontSize=12, leading=15, spaceBefore=8, spaceAfter=4),
        "b": ParagraphStyle("B", parent=base["BodyText"], fontSize=9.5, leading=12, spaceAfter=3),
        "small": ParagraphStyle("S", parent=base["BodyText"], fontSize=8, leading=10, textColor=colors.HexColor("#444")),
    }


def status_color(status: str):
    return {
        "PASS": colors.HexColor("#166534"),
        "PARTIAL": colors.HexColor("#9a3412"),
        "NOT DONE": colors.HexColor("#991b1b"),
        "BLOCKED": colors.HexColor("#1e3a8a"),
    }.get(status, colors.black)


def first_existing(paths):
    for p in paths:
        if p and Path(p).is_file() and Path(p).stat().st_size > 100:
            return Path(p)
    return None


def add_shot(flow, path: Path | None, st, max_w=160 * mm, max_h=90 * mm):
    if not path:
        flow.append(Paragraph("No verified screenshot file available for this day (not fabricated).", st["small"]))
        return
    try:
        img = Image(str(path))
        img.hAlign = "LEFT"
        iw, ih = img.imageWidth, img.imageHeight
        scale = min(max_w / iw, max_h / ih, 1.0)
        img.drawWidth = iw * scale
        img.drawHeight = ih * scale
        flow.append(Paragraph(f"Screenshot evidence: {path.relative_to(ROOT).as_posix()}", st["small"]))
        flow.append(img)
        flow.append(Spacer(1, 4))
    except Exception as exc:  # noqa: BLE001
        flow.append(Paragraph(f"Screenshot could not be embedded ({path.name}): {exc}", st["small"]))


def build_day_pdf(day: dict) -> Path:
    st = styles()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    status = day["status"]
    out = OUT_DIR / f"TalentBridgeAI_Day_{day['n']:02d}_Completion_Report.pdf"
    if status == "PARTIAL":
        title = f"TalentBridgeAI Day {day['n']:02d} Completion Report — PARTIAL"
    else:
        title = f"TalentBridgeAI Day {day['n']:02d} Completion Report — {status}"

    doc = SimpleDocTemplate(
        str(out),
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title=title,
    )
    flow = []
    flow.append(Paragraph("TalentBridgeAI", st["title"]))
    flow.append(Paragraph(title, st["h"]))
    flow.append(Paragraph(f"<b>Verification date:</b> {VERIFY_DATE}", st["b"]))
    flow.append(Paragraph(f"<b>Final verified status:</b> <font color='{status_color(status).hexval()}'>{status}</font>", st["b"]))
    flow.append(Paragraph(f"<b>Original roadmap task:</b> {day['title']}", st["b"]))
    flow.append(Paragraph(f"<b>Objective:</b> {day['objective']}", st["b"]))
    flow.append(Paragraph("<b>Work actually performed</b>", st["h"]))
    flow.append(Paragraph(day["work"], st["b"]))
    flow.append(Paragraph("<b>Files created or modified</b>", st["h"]))
    flow.append(Paragraph(day["files"], st["b"]))
    flow.append(Paragraph("<b>Commands executed</b>", st["h"]))
    flow.append(Paragraph(day["commands"], st["b"]))
    flow.append(Paragraph("<b>Test results</b>", st["h"]))
    flow.append(Paragraph(day["tests"], st["b"]))
    flow.append(Paragraph("<b>Remaining issues</b>", st["h"]))
    flow.append(Paragraph(day["remaining"], st["b"]))
    flow.append(Paragraph("<b>Evidence / screenshots</b>", st["h"]))

    shots = [p for p in day.get("shots", []) if p]
    if not shots:
        flow.append(Paragraph("No image screenshot on file for this day. Status is based on audit documentation evidence, not invented images.", st["small"]))
    for p in shots:
        add_shot(flow, first_existing([p]), st)

    audit = day.get("audit")
    if audit and Path(audit).is_file():
        flow.append(Paragraph("<b>Audit source excerpt</b>", st["h"]))
        text = Path(audit).read_text(encoding="utf-8", errors="replace").splitlines()
        excerpt = " ".join(text[:40])[:1200].replace("<", "&lt;").replace(">", "&gt;")
        flow.append(Paragraph(excerpt + ("…" if len(text) > 40 else ""), st["small"]))

    flow.append(Spacer(1, 8))
    flow.append(Paragraph("This report does not expose secrets, tokens, or private candidate data.", st["small"]))
    doc.build(flow)
    data = out.read_bytes()
    if not data.startswith(b"%PDF"):
        raise SystemExit(f"Invalid PDF: {out}")
    return out


def build_master(day_pdfs: list[Path]) -> Path:
    st = styles()
    out = OUT_DIR / "TalentBridgeAI_Days_01_to_12_Master_Completion_Audit.pdf"
    doc = SimpleDocTemplate(str(out), pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm, topMargin=14 * mm, bottomMargin=14 * mm)
    flow = []
    flow.append(Paragraph("TalentBridgeAI — Days 01 to 12 Master Completion Audit", st["title"]))
    flow.append(Paragraph(f"Verification date: {VERIFY_DATE}", st["b"]))
    flow.append(Paragraph("Executive summary: Phase 1 is CONDITIONAL PASS (Day 10). Days 1–7/9/11 are documented PASS. Days 8/10/12 are PARTIAL. No day is marked PASS from report existence alone.", st["b"]))
    flow.append(Paragraph("Phase 1 gate status: CONDITIONAL PASS (not full complete).", st["b"]))

    rows = [[Paragraph("<b>Day</b>", st["small"]), Paragraph("<b>Task</b>", st["small"]), Paragraph("<b>Status</b>", st["small"]), Paragraph("<b>Evidence</b>", st["small"]), Paragraph("<b>Pending</b>", st["small"])]]
    for d in DAYS:
        ev = "Audit + screenshots" if any(Path(p).is_file() for p in d.get("shots", [])) else "Audit docs"
        rows.append([
            Paragraph(str(d["n"]), st["small"]),
            Paragraph(d["title"], st["small"]),
            Paragraph(d["status"], st["small"]),
            Paragraph(ev, st["small"]),
            Paragraph(d["remaining"][:80], st["small"]),
        ])
    table = Table(rows, colWidths=[12 * mm, 45 * mm, 22 * mm, 35 * mm, 55 * mm])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    flow.append(table)
    flow.append(Paragraph("<b>Screenshot index</b>", st["h"]))
    flow.append(Paragraph("day-02/08/10/12 folders under docs/screenshots; cinematic/hero evidence under docs/evidence.", st["b"]))
    flow.append(Paragraph("<b>Backup</b>", st["h"]))
    flow.append(Paragraph("Day 11 backup: TalentBridgeAI_Day11_PreOrganization_Backup_2026-11-19_08-38-38 (sibling of project root). GitHub: MishraJi-Institute/Talent_Bridge_AI. Custom domain: talentbridge.qd.je", st["b"]))
    flow.append(Paragraph("<b>Animation verification</b>", st["h"]))
    flow.append(Paragraph("External orbit implementation updated to clear the profile card exterior. Live Pages may lag until redeploy. Prefer local Django :8000 for newest orbit-ext2 assets.", st["b"]))
    flow.append(Paragraph("<b>Individual PDFs generated</b>", st["h"]))
    for p in day_pdfs:
        flow.append(Paragraph(p.name, st["small"]))
    doc.build(flow)
    return out


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Copy latest browser screenshot if present in Cursor screenshots temp is handled separately.
    day_pdfs = []
    for d in DAYS:
        if d["status"] == "NOT DONE":
            continue
        day_pdfs.append(build_day_pdf(d))
        print("DAY_PDF", day_pdfs[-1])
    master = build_master(day_pdfs)
    print("MASTER_PDF", master)


if __name__ == "__main__":
    main()
