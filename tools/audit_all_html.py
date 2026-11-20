#!/usr/bin/env python3
"""Scan built site/ HTML for common publish bugs."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def main() -> int:
    if not SITE.is_dir():
        print("Run tools/build_static.py first.")
        return 1
    issues: list[str] = []
    for html in sorted(SITE.rglob("*.html")):
        text = html.read_text(encoding="utf-8-sig")
        rel = html.relative_to(SITE).as_posix()
        if re.search(r"\{%|{{", text):
            issues.append(f"{rel}: unrendered Django template syntax")
        if 'data-oauth-provider="google"' in text:
            if "google-pages-signin.js" not in text:
                issues.append(f"{rel}: Google form without google-pages-signin.js")
            if 'name="google-oauth-client-id"' not in text:
                issues.append(f"{rel}: Google form without client-id meta")
    print(f"Scanned {len(list(SITE.rglob('*.html')))} HTML files under site/")
    if issues:
        print(f"Issues: {len(issues)}")
        for line in issues:
            print(f"  - {line}")
        return 1
    print("No HTML publish issues found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())