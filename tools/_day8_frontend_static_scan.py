"""Day 8 read-only static frontend scan: links, forms, asset refs."""
from __future__ import annotations

import json
import os
import re
import sys
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
PAGES = FRONTEND / "pages"
BASE = "http://127.0.0.1:8000"

sys.path.insert(0, str(ROOT / "backend" / "legacy-django"))
os.chdir(ROOT / "backend" / "legacy-django")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

django.setup()
from django.urls import NoReverseMatch, reverse, get_resolver
from django.conf import settings
from config import urls as root_urls


class LinkFormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.forms = []
        self._form = None
        self._link_href = None
        self._link_text = []

    def handle_starttag(self, tag, attrs):
        ad = dict(attrs)
        if tag == "a":
            self._link_href = ad.get("href", "")
            self._link_text = []
        elif tag == "form":
            self._form = {
                "action": ad.get("action", ""),
                "method": (ad.get("method") or "get").lower(),
                "enctype": ad.get("enctype", ""),
                "inputs": [],
                "has_csrf": False,
                "has_submit": False,
            }
        elif tag in {"input", "button", "textarea", "select"} and self._form is not None:
            name = ad.get("name", "")
            typ = ad.get("type", tag if tag != "input" else "text")
            if name == "csrfmiddlewaretoken" or "csrf" in name.lower():
                self._form["has_csrf"] = True
            if tag == "button" or typ in {"submit", "image"}:
                self._form["has_submit"] = True
            if typ == "file":
                self._form["has_file"] = True
            self._form["inputs"].append({"tag": tag, "type": typ, "name": name})

    def handle_data(self, data):
        if self._link_href is not None:
            self._link_text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._link_href is not None:
            text = " ".join("".join(self._link_text).split())[:80]
            self.links.append({"href": self._link_href, "text": text})
            self._link_href = None
            self._link_text = []
        elif tag == "form" and self._form is not None:
            self.forms.append(self._form)
            self._form = None


def collect_html_files():
    files = [FRONTEND / "index.html"]
    files.extend(sorted(PAGES.rglob("*.html")))
    return [f for f in files if f.is_file()]


def static_scan():
    url_tag = re.compile(r"""\{%\s*url\s+['\"]([^'\"]+)['\"]""")
    static_tag = re.compile(r"""\{%\s*static\s+['\"]([^'\"]+)['\"]""")
    href_re = re.compile(r"""href=["']([^"']+)["']""", re.I)
    action_re = re.compile(r"""<form[^>]*action=["']([^"']*)["']""", re.I)
    method_re = re.compile(r"""<form[^>]*method=["']([^"']+)["']""", re.I)

    pages = []
    hash_links = []
    empty_href = []
    js_pages_links = []
    url_reverse_fail = []
    forms_summary = []

    for path in collect_html_files():
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        text = path.read_text(encoding="utf-8", errors="replace")
        parser = LinkFormParser()
        try:
            parser.feed(text)
        except Exception:
            pass
        for link in parser.links:
            href = link["href"].strip()
            if href in {"",}:
                empty_href.append({"file": rel, "text": link["text"]})
            elif href == "#" or href.startswith("#") and len(href) < 3:
                hash_links.append({"file": rel, "text": link["text"], "href": href})
            if "/js/pages/" in href or href.startswith("js/pages/"):
                js_pages_links.append({"file": rel, "href": href, "text": link["text"]})
        for name in url_tag.findall(text):
            try:
                reverse(name)
            except NoReverseMatch as exc:
                url_reverse_fail.append({"file": rel, "name": name, "error": str(exc)[:120]})
            except Exception as exc:
                # needs args
                if "arguments" in str(exc).lower() or "keyword" in str(exc).lower():
                    continue
                url_reverse_fail.append({"file": rel, "name": name, "error": str(exc)[:120]})
        for form in parser.forms:
            forms_summary.append(
                {
                    "file": rel,
                    "action": form.get("action", ""),
                    "method": form.get("method", "get"),
                    "enctype": form.get("enctype", ""),
                    "has_csrf": form.get("has_csrf", False),
                    "has_submit": form.get("has_submit", False),
                    "has_file": form.get("has_file", False),
                    "input_count": len(form.get("inputs", [])),
                }
            )
        pages.append(
            {
                "file": rel,
                "link_count": len(parser.links),
                "form_count": len(parser.forms),
            }
        )

    return {
        "html_files": len(pages),
        "pages": pages,
        "hash_or_placeholder_links": hash_links[:80],
        "hash_link_count": len(hash_links),
        "empty_href_count": len(empty_href),
        "empty_href": empty_href[:40],
        "js_pages_links": js_pages_links,
        "url_reverse_fail": url_reverse_fail[:40],
        "forms": forms_summary,
        "pages_slugs": list(root_urls.PAGES.keys()),
    }


def http_probe(paths):
    results = {}
    for path in paths:
        url = urljoin(BASE + "/", path.lstrip("/"))
        try:
            req = Request(url, method="GET", headers={"User-Agent": "TalentBridgeDay8Audit/1.0"})
            with urlopen(req, timeout=12) as resp:
                body = resp.read(200000)
                results[path] = {
                    "status": resp.status,
                    "final": resp.geturl(),
                    "bytes": len(body),
                    "ctype": resp.headers.get("Content-Type", "")[:60],
                }
        except HTTPError as exc:
            loc = exc.headers.get("Location", "") if exc.headers else ""
            results[path] = {"status": exc.code, "final": loc, "bytes": 0, "ctype": ""}
        except Exception as exc:
            results[path] = {"status": "ERR", "final": type(exc).__name__, "bytes": 0, "ctype": ""}
    return results


def extract_links_from_html(html: str, base_url: str):
    hrefs = re.findall(r"""(?:href|src)=["']([^"']+)["']""", html, flags=re.I)
    out = []
    for h in hrefs:
        if h.startswith(("mailto:", "tel:", "javascript:", "data:")):
            continue
        abs_url = urljoin(base_url, h)
        parsed = urlparse(abs_url)
        if parsed.hostname not in {None, "127.0.0.1", "localhost"}:
            continue
        out.append(parsed.path + (("?" + parsed.query) if parsed.query else ""))
    return sorted(set(out))


def crawl_key_pages():
    key = [
        "/",
        "/login/",
        "/signup/",
        "/signup/job-seeker/",
        "/signup/employer/",
        "/jobs/",
        "/companies/",
        "/pricing/",
        "/faq/",
        "/about/",
        "/contact/",
        "/job-search/",
        "/employer/",
        "/jobseaker/",
        "/forgot-password/",
        "/dashboard/",
        "/profile/",
        "/saved-jobs/",
        "/resume-builder/",
        "/admin-dashboard/",
        "/faqs/",
        "/trust/",
        "/search/",
    ]
    probe = http_probe(key)
    # fetch homepage + login + jobs HTML for link checking
    link_checks = {}
    for path in ["/", "/login/", "/jobs/", "/signup/", "/pricing/", "/contact/"]:
        url = urljoin(BASE + "/", path.lstrip("/"))
        try:
            with urlopen(Request(url, headers={"User-Agent": "TalentBridgeDay8Audit/1.0"}), timeout=12) as resp:
                html = resp.read().decode("utf-8", "replace")
            links = extract_links_from_html(html, url)
            # probe up to 40 internal paths from this page
            sample = [p for p in links if not p.startswith(("/css/", "/js/", "/images/", "/static/"))][:35]
            assets = [p for p in links if p.startswith(("/css/", "/js/", "/images/"))][:20]
            broken = {}
            for p in sample + assets:
                r = http_probe([p])[p]
                if isinstance(r["status"], int) and r["status"] >= 400:
                    broken[p] = r
                if r["status"] == "ERR":
                    broken[p] = r
            link_checks[path] = {
                "internal_link_sample": len(sample),
                "asset_sample": len(assets),
                "broken": broken,
                "all_internal_count": len(links),
            }
        except Exception as exc:
            link_checks[path] = {"error": type(exc).__name__, "msg": str(exc)[:120]}
    return probe, link_checks


def main():
    static = static_scan()
    probe, link_checks = crawl_key_pages()
    # post forms without submit: CSRF presence on login template via HTTP
    login_html = ""
    try:
        with urlopen(Request(BASE + "/login/", headers={"User-Agent": "TalentBridgeDay8Audit/1.0"}), timeout=12) as resp:
            login_html = resp.read().decode("utf-8", "replace")
    except Exception:
        pass
    out = {
        "base": BASE,
        "static": static,
        "http_probe": probe,
        "link_checks": link_checks,
        "login_has_csrf": "csrfmiddlewaretoken" in login_html,
        "login_has_password_type": 'type="password"' in login_html or "type='password'" in login_html,
    }
    dest = ROOT / "docs" / "reports" / "_day8_frontend_scan.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("HTML_FILES", static["html_files"])
    print("HASH_LINKS", static["hash_link_count"])
    print("JS_PAGES_LINKS", len(static["js_pages_links"]))
    print("URL_REVERSE_FAIL", len(static["url_reverse_fail"]))
    print("FORMS", len(static["forms"]))
    print("LOGIN_CSRF", out["login_has_csrf"])
    for p, r in probe.items():
        print("PROBE", p, r["status"], r["final"][:60] if isinstance(r["final"], str) else r["final"])
    for p, info in link_checks.items():
        print("LINKS", p, "broken", len(info.get("broken", {})), info.get("broken", {}) or info.get("error"))
    print("WROTE", dest)


if __name__ == "__main__":
    main()
