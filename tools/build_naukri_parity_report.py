#!/usr/bin/env python3
"""Build before/after Naukri parity PDF from screenshots + matrix JSON."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors

ROOT = Path(__file__).resolve().parents[1]
SHOT_BEFORE = ROOT / "docs" / "screenshots" / "naukri-parity" / "before"
SHOT_AFTER = ROOT / "docs" / "screenshots" / "naukri-parity" / "after"
MATRIX = ROOT / "docs" / "reports" / "NAUKRI_FEATURE_MATRIX.json"
OUTPUT = ROOT / "docs" / "TalentBridgeAI_Naukri_Parity_Report.pdf"


def _img_flow(path: Path, width_mm: float = 170):
    if not path.is_file():
        return Paragraph(f"<i>Missing screenshot: {path.name}</i>", getSampleStyleSheet()["Italic"])
    img = Image(str(path))
    max_w = width_mm * mm
    ratio = max_w / float(img.imageWidth)
    img.drawWidth = max_w
    img.drawHeight = img.imageHeight * ratio
    return img


def main() -> int:
    styles = getSampleStyleSheet()
    title = ParagraphStyle("T", parent=styles["Title"], fontSize=16, spaceAfter=6)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=12, spaceBefore=8, spaceAfter=4)
    body = ParagraphStyle("B", parent=styles["BodyText"], fontSize=10, leading=13)

    story = [
        Paragraph("TalentBridge AI — Naukri parity progress report", title),
        Paragraph(datetime.now().strftime("%d %B %Y, %H:%M local"), body),
        Spacer(1, 6),
        Paragraph(
            "Comparison target: Naukri.com job-seeker + SME employer MVP (search, profile, resume, "
            "apply, employer post, applicants). Full Naukri monetization (Resdex, paid plans) remains out of scope.",
            body,
        ),
        Paragraph("<b>Before (baseline)</b>: dashboards mixed browser demo data with SQLite; "
                  "some footer links opened static .html paths; resume upload only works on Django :8000.",
                  body),
        Paragraph("<b>After (this build)</b>: live jobs wired into seeker dashboard Apply; "
                  "canonical /resume-management/ and /applied-jobs/ links; clearer resume upload guidance; "
                  "feature matrix audit script.", body),
    ]

    if MATRIX.is_file():
        data = json.loads(MATRIX.read_text(encoding="utf-8"))
        rows = [["Route", "HTTP"]] + [[r["path"], str(r["http"])] for r in data.get("routes", [])]
        table = Table(rows, colWidths=[120 * mm, 25 * mm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8f0fe")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                ]
            )
        )
        story += [Paragraph("Route health (local Django)", h2), table, Spacer(1, 8)]

    for label, folder in (("Before", SHOT_BEFORE), ("After", SHOT_AFTER)):
        story.append(Paragraph(f"Screenshots — {label}", h2))
        images = sorted(folder.glob("*.png"))
        if not images:
            story.append(Paragraph(f"No PNG files in {folder.relative_to(ROOT)}", body))
        else:
            for shot in images:
                story.append(Paragraph(shot.stem.replace("-", " "), body))
                story.append(_img_flow(shot))
                story.append(Spacer(1, 6))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm)
    doc.build(story)
    print(f"PDF_OK {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())