"""Day 8: probe rendered asset/link status for key pages."""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend" / "legacy-django"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

django.setup()
from jobs.models import Job  # noqa: E402

BASE = "http://127.0.0.1:8000"
OUT = ROOT / "docs" / "reports" / "_day8_http_asset_probe.json"
ATTR = re.compile(r"""(?:href|src|action)=["']([^"']+)["']""", re.I)


def fetch(path: str) -> tuple[int | None, str, str]:
    url = path if path.startswith("http") else BASE + path
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            body = r.read().decode("utf-8", "replace")
            return r.status, url, body
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", "replace")
        except Exception:
            body = ""
        return e.code, url, body
    except Exception as e:
        return None, url, str(e)


def abs_url(page_url: str, ref: str) -> str | None:
    if not ref or ref.startswith(("#", "mailto:", "tel:", "javascript:", "{%")):
        return None
    if ref.startswith("http://") or ref.startswith("https://"):
        return ref
    if ref.startswith("//"):
        return "http:" + ref
    if ref.startswith("/"):
        return BASE + ref
    # relative to page directory
    from urllib.parse import urljoin

    return urljoin(page_url if page_url.endswith("/") else page_url + "/", ref)


results: dict = {"pages": {}, "job_id": None}
job = Job.objects.filter(is_active=True).order_by("id").first() or Job.objects.order_by("id").first()
if job:
    results["job_id"] = job.id

pages = ["/", "/login/", "/jobs/", "/contact/", "/signup/", "/pricing/", "/employer/", "/jobseaker/", "/companies/", "/forgot-password/", "/about/", "/faq/"]
if job:
    pages.append(f"/jobs/{job.id}/")

for path in pages:
    status, final, body = fetch(path)
    entry: dict = {"status": status, "final": final, "broken": [], "forms": [], "pages_root_links": []}
    if status and status < 400 and body:
        refs = ATTR.findall(body)
        checked = set()
        for ref in refs:
            full = abs_url(final, ref)
            if not full or not full.startswith(BASE):
                continue
            # only check internal html/css/js/images and relative form actions
            if not any(x in full for x in (".html", "/css/", "/js/", "/images/", ".css", ".js", ".png", ".svg", ".webp", ".jpg")) and not ref.endswith(".html"):
                # still record bare /pages/
                if full.rstrip("/").endswith("/pages") or full.endswith("/pages/"):
                    entry["pages_root_links"].append(ref)
                continue
            if full in checked:
                continue
            checked.add(full)
            st, _, _ = fetch(full.replace(BASE, "") if full.startswith(BASE) else full)
            if st is None or st >= 400:
                entry["broken"].append({"ref": ref, "resolved": full.replace(BASE, ""), "status": st})
            if len(entry["broken"]) >= 25:
                break
        for m in re.finditer(r"<form\b[^>]*>", body, re.I):
            tag = m.group(0)
            am = re.search(r'action=["\']([^"\']*)["\']', tag, re.I)
            mm = re.search(r'method=["\']([^"\']*)["\']', tag, re.I)
            entry["forms"].append({"action": am.group(1) if am else "", "method": (mm.group(1) if mm else "get").lower()})
        # bare /pages/ links
        for ref in refs:
            if ref in ("/pages/", "/pages"):
                entry["pages_root_links"].append(ref)
    results["pages"][path] = entry
    print(path, status, "broken", len(entry["broken"]), "forms", entry["forms"][:3])

OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
print("wrote", OUT)
