#!/usr/bin/env python3
"""Quick Naukri-style feature matrix for local Django (read-only HTTP checks)."""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8000"
ROUTES = [
    ("Home", "/"),
    ("Browse jobs", "/jobs/"),
    ("Companies", "/companies/"),
    ("Login", "/login/"),
    ("Resume library", "/resume-management/"),
    ("Apply flow entry", "/applied-jobs/"),
    ("Employer post job", "/posting-job/"),
    ("Seeker dashboard", "/pages/dashboard/jdashboard.html"),
    ("Contact", "/contact/"),
    ("Admin login", "/admin/login/"),
]


def fetch(path: str) -> tuple[int | None, str]:
    url = BASE + path
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.status, url
    except urllib.error.HTTPError as exc:
        return exc.code, url
    except OSError as exc:
        return None, f"{url} ({exc})"


def main() -> int:
    rows = []
    for name, path in ROUTES:
        code, detail = fetch(path)
        rows.append({"feature": name, "path": path, "http": code, "detail": detail})
    out = ROOT / "docs" / "reports" / "NAUKRI_FEATURE_MATRIX.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"base": BASE, "routes": rows}, indent=2), encoding="utf-8")
    failures = [r for r in rows if r["http"] != 200]
    print(f"Wrote {out.relative_to(ROOT)}")
    for row in rows:
        mark = "OK" if row["http"] == 200 else "FAIL"
        print(f"  [{mark}] {row['feature']} {row['path']} -> {row['http']}")
    if failures and any(r["http"] is None for r in failures):
        print("\nDjango may be down. Start START_TALENTBRIDGEAI.bat on port 8000.")
        return 1
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())