"""Day 8 helper: find relative *.html hrefs that resolve under nested paths."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "frontend" / "pages"
OUT = ROOT / "docs" / "reports" / "_day8_relative_hrefs.json"

# href="about.html" or href='../foo.html' — not absolute /, http, #, mailto, {% 
PAT = re.compile(
    r"""href\s*=\s*["'](?!https?:|/|#|mailto:|tel:|javascript:|{%)([^"']+\.html(?:\?[^"']*)?)["']""",
    re.I,
)

hits: dict[str, list[str]] = {}
for f in sorted(PAGES.rglob("*.html")):
    if "unslop" in f.parts:
        continue
    text = f.read_text(encoding="utf-8", errors="replace")
    found = sorted(set(PAT.findall(text)))
    if found:
        rel = str(f.relative_to(ROOT)).replace("\\", "/")
        hits[rel] = found

OUT.write_text(json.dumps({"count_pages": len(hits), "pages": hits}, indent=2), encoding="utf-8")
print(f"pages_with_relative_html={len(hits)}")
for k, v in list(hits.items())[:40]:
    print(f"{k} => {v}")
