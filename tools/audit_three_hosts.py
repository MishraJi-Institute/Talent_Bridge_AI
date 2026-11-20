#!/usr/bin/env python3
"""Smoke-check key routes on local Django, GitHub Pages domain, and github.io."""
from __future__ import annotations

import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES_ROUTES = (
    "/",
    "/pages/login.html",
    "/pages/jobseeker-signup.html",
    "/pages/company-signup.html",
    "/pages/signup-role.html",
    "/login/",
)
DJANGO_ROUTES = (
    "/",
    "/login/",
    "/signup/job-seeker/",
    "/signup/employer/",
)

HOSTS = {
    "local_django": "http://127.0.0.1:8000",
    "pages_domain_http": "http://talentbridge.qd.je",
    "pages_domain_https": "https://talentbridge.qd.je",
    "github_io": "https://mishraji-institute.github.io/Talent_Bridge_AI",
}
# HTTPS custom domain blocked until GitHub Pages issues TLS for talentbridge.qd.je (Google OAuth needs it).
HTTPS_DOMAIN_KNOWN_BLOCKER = "pages_domain_https"


def fetch(url: str, timeout: float = 12) -> tuple[int | None, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "TalentBridge-audit/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(200_000).decode("utf-8", "replace")
            return resp.status, body
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read(80_000).decode("utf-8", "replace")
        except Exception:
            body = ""
        return exc.code, body
    except Exception as exc:
        return None, str(exc)


def checks(html: str, *, static_pages: bool) -> list[str]:
    issues: list[str] = []
    if "<title>Redirecting" in html and "host-runtime.js" not in html:
        return issues
    if "{%" in html or "{{" in html:
        issues.append("unrendered_django_template")
    if "google-oauth-client-id" in html and 'data-oauth-provider="google"' in html:
        if "google-pages-signin.js" not in html:
            issues.append("google_oauth_missing_script")
        if 'name="google-oauth-client-id"' not in html and "static-live" not in html:
            pass  # only on pages with meta injection
        elif 'data-oauth-provider="google"' in html and 'name="google-oauth-client-id"' not in html:
            issues.append("google_oauth_missing_client_meta")
    if static_pages and "host-runtime.js" not in html and "<html" in html.lower():
        issues.append("missing_host_runtime")
    return issues


def main() -> int:
    failures: list[str] = []
    print("TalentBridge three-host audit\n" + "=" * 60)
    for host_key, base in HOSTS.items():
        print(f"\n## {host_key} ({base})")
        routes = DJANGO_ROUTES if host_key == "local_django" else PAGES_ROUTES
        for route in routes:
            url = base.rstrip("/") + route
            status, body = fetch(url)
            if status is None:
                ssl_blocked = host_key == HTTPS_DOMAIN_KNOWN_BLOCKER and "CERTIFICATE" in body.upper()
                if ssl_blocked and route == routes[0]:
                    print(f"  SKIP (known) TLS not ready on custom domain — fix GitHub Pages certificate")
                if ssl_blocked:
                    continue
                print(f"  FAIL {route} — {body[:120]}")
                failures.append(f"{host_key}{route}: {body[:80]}")
                continue
            if status >= 400:
                print(f"  HTTP {status} {route}")
                failures.append(f"{host_key}{route}: HTTP {status}")
                continue
            static_pages = host_key != "local_django"
            route_issues = checks(body, static_pages=static_pages)
            tag = "OK" if not route_issues else "WARN"
            extra = f" ({', '.join(route_issues)})" if route_issues else ""
            print(f"  {tag} {status} {route}{extra}")
            for issue in route_issues:
                failures.append(f"{host_key}{route}: {issue}")
    print("\n" + "=" * 60)
    if failures:
        print(f"Issues: {len(failures)}")
        for line in failures[:40]:
            print(f"  - {line}")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())