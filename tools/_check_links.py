"""Check local HTML references for the static site."""

from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent
HTML_FILES = [
    ROOT / "index.html",
    ROOT / "404.html",
    *sorted((ROOT / "pages").rglob("*.html")),
]
CSS_FILES = sorted((ROOT / "css").rglob("*.css"))
missing = []

for html_file in HTML_FILES:
    text = html_file.read_text(encoding="utf-8-sig")
    for attribute, value in re.findall(
        r"""(href|src|action)\s*=\s*["']([^"']+)["']""", text, re.IGNORECASE
    ):
        value = value.strip()
        if not value or value.startswith(
            ("http://", "https://", "//", "mailto:", "tel:", "data:", "javascript:", "#")
        ):
            continue
        if "{%" in value or "{{" in value or value.startswith("/"):
            continue
        path = urlsplit(value).path
        if not path:
            continue
        target = (html_file.parent / path).resolve()
        if not target.exists():
            missing.append((html_file.relative_to(ROOT), attribute, value))

for css_file in CSS_FILES:
    text = css_file.read_text(encoding="utf-8-sig")
    for value in re.findall(r"""url\(\s*(['"]?)(.*?)\1\s*\)""", text, re.IGNORECASE):
        value = unquote(value[1].strip())
        if not value or value.startswith(
            ("http://", "https://", "//", "data:", "blob:", "#")
        ):
            continue
        path = urlsplit(value).path
        if not path:
            continue
        target = (css_file.parent / path).resolve()
        if not target.exists():
            missing.append((css_file.relative_to(ROOT), "url()", value))

if missing:
    print("Missing local references:")
    for item in missing:
        print(f"  {item[0]} ({item[1]}): {item[2]}")
    raise SystemExit(1)

print(
    f"Checked {len(HTML_FILES)} static HTML files and {len(CSS_FILES)} CSS files; "
    "no missing local references."
)
