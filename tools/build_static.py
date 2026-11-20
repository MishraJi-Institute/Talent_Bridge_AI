from pathlib import Path
import os
import re
import shutil
import sys
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backend_health import origin_is_healthy  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]  # repo root (script lives in tools/)
OUTPUT = ROOT / "site"
# Repo-root names remain the static publish layout. After Step 1 organization these
# paths are compatibility junctions into frontend/ (pages, css, js, assets/...).
FRONTEND = ROOT / "frontend"
PUBLIC_DIR_MAP = {
    "css": FRONTEND / "css",
    "js": FRONTEND / "js",
    "pages": FRONTEND / "pages",
    "images": FRONTEND / "assets" / "images",
    "videos": FRONTEND / "assets" / "videos",
}
STATIC_ROUTE_PAGES = {
    "home": "index.html",
    "signup": "pages/signup-role.html",
    "company-signup": "pages/company-signup.html",
    "employer_signup": "pages/company-signup.html",
    "jobseeker_signup": "pages/jobseeker-signup.html",
    "jobseeker_signup_page": "pages/jobseeker-signup.html",
    "employer_signup_page": "pages/company-signup.html",
    "employer": "pages/employer.html",
    "employee": "pages/employee.html",
    "login": "pages/login.html",
    "login_page": "pages/login.html",
    "pricing": "pages/pricing.html",
    "posting-job": "pages/posting-job.html",
    "create_job": "pages/posting-job.html",
    "companies": "pages/companies.html",
    "candidate-search": "pages/candidate-search.html",
    "dashboard-profile-save": "pages/dashboard/jdashboard.html",
    "edit-job": "pages/manage-jobs.html",
    "resume_delete": "pages/resume-management.html",
    "resume_preview": "pages/resume-management.html",
    "terms": "pages/terms.html",
    "privacy": "pages/privacy.html",
    "about": "pages/about.html",
    "contact": "pages/contact.html",
    "contact_submit": "pages/contact.html",
    "help": "pages/help.html",
    "faq": "pages/faq.html",
    "categories": "pages/categories.html",
    "jobs": "pages/job-listings.html",
    "job_detail": "pages/job-detail.html",
    "apply_job": "pages/application-form.html",
    "application-success": "pages/application-success.html",
    "saved-jobs": "pages/saved-jobs.html",
    "toggle-saved-job": "pages/saved-jobs.html",
    "recommended-jobs": "pages/recommended-jobs.html",
    "applied-jobs": "pages/applied-jobs.html",
    "profile": "pages/profile.html",
    "edit-profile": "pages/edit-profile.html",
    "account-security": "pages/account-security.html",
    "company-details": "pages/company-details.html",
    "resume-management": "pages/resume-management.html",
    "resume-builder": "pages/resume-builder.html",
    "resume_download": "pages/resume-management.html",
    "manage-jobs": "pages/manage-jobs.html",
    "toggle-job-active": "pages/manage-jobs.html",
    "manage-applications": "pages/manage-applications.html",
    "update-application-status": "pages/manage-applications.html",
    "candidate-details": "pages/candidate-details.html",
    "notifications": "pages/notifications.html",
    "interviews": "pages/interviews.html",
    "admin-dashboard": "pages/admin-dashboard.html",
    "approve-company": "pages/admin-dashboard.html",
    "employer_pending": "pages/employer-pending.html",
    "forgot-password": "pages/forgot-password.html",
    "password-reset": "pages/password-reset.html",
    "password-reset-confirm": "pages/password-reset-confirm.html",
    "password-reset-complete": "pages/password-reset-complete.html",
    "logout": "pages/login.html",
    "social-login-start": "pages/login.html",
    "socialaccount_signup": "pages/socialaccount/signup.html",
    "admin:index": "pages/admin-dashboard.html",
}
STATIC_PATH_PAGES = {
    "/dashboard/": "pages/dashboard/jdashboard.html",
    "/companies/": "pages/companies.html",
    "/login/": "pages/login.html",
    "/jobs/": "pages/job-listings.html",
    "/remote-jobs/": "pages/job-listings.html",
    "/startup-jobs/": "pages/job-listings.html",
    "/jobseaker/": "pages/jobseaker.html",
    "/job-seekers/": "pages/jobseaker.html",
    "/for-job-seekers/": "pages/jobseaker.html",
    "/employer/": "pages/employer.html",
    "/employers/": "pages/employer.html",
    "/for-employers/": "pages/employer.html",
    "/pricing/": "pages/pricing.html",
    "/careers/": "pages/careers.html",
    "/resources/": "pages/careers.html",
    "/about/": "pages/about.html",
    "/blog/": "pages/blog.html",
    "/faq/": "pages/faq.html",
    "/signup/": "pages/signup-role.html",
    "/signup/job-seeker/": "pages/jobseeker-signup.html",
    "/signup/employer/": "pages/company-signup.html",
    "/forgot-password/": "pages/forgot-password.html",
    "/password-reset/": "pages/password-reset.html",
    "/help/": "pages/help.html",
    "/privacy/": "pages/privacy.html",
    "/terms/": "pages/terms.html",
    "/contact/": "pages/contact.html",
    "/posting-job/": "pages/posting-job.html",
    "/categories/": "pages/categories.html",
    "/customer-stories/": "pages/customer-stories.html",
    "/trust-center/": "pages/trust-center.html",
    "/platform-status/": "pages/platform-status.html",
    "/cookie-preferences/": "pages/cookie-preferences.html",
    "/ai-audit-center/": "pages/ai-audit-center.html",
    "/salary-calculator/": "pages/salary-calculator.html",
    "/remote-work-guide/": "pages/remote-work-guide.html",
    "/recommended-jobs/": "pages/recommended-jobs.html",
    "/job-search/": "pages/job-search.html",
    "/saved-jobs/": "pages/saved-jobs.html",
    "/applied-jobs/": "pages/applied-jobs.html",
    "/profile/": "pages/profile.html",
    "/edit-profile/": "pages/edit-profile.html",
    "/resume-management/": "pages/resume-management.html",
    "/resume-builder/": "pages/resume-builder.html",
    "/manage-jobs/": "pages/manage-jobs.html",
    "/manage-applications/": "pages/manage-applications.html",
    "/candidate-search/": "pages/candidate-search.html",
    "/candidate-details/": "pages/candidate-details.html",
    "/notifications/": "pages/notifications.html",
    "/interviews/": "pages/interviews.html",
    "/employer-profile/": "pages/employer-profile.html",
    "/company-details/": "pages/company-details.html",
    "/employer/pending/": "pages/employer-pending.html",
    "/auth/social/google/": "pages/login.html",
    "/accounts/google/login/": "pages/login.html",
    "/accounts/google/login/callback/": "pages/login.html",
}
TEMPLATE_TOKEN = re.compile(r"(\{%.*?%\}|{{.*?}})", re.DOTALL)
STATIC_TEMPLATE_VALUES = {
    "active_job_count": "—",
    "approved_company_count": "—",
    "candidate_count": "—",
}


def _resolve_django_origin() -> str:
    """Production Django HTTPS origin for static→OAuth handoff (not localhost)."""
    origin = os.environ.get("TALENTBRIDGE_DJANGO_ORIGIN", "").strip()
    if not origin:
        cfg = ROOT / "config" / "talentbridge_django_origin.txt"
        if cfg.is_file():
            for line in cfg.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                origin = line
                break
    origin = origin.rstrip("/")
    if origin and ("127.0.0.1" in origin or "localhost" in origin.lower()):
        raise RuntimeError(
            "TALENTBRIDGE_DJANGO_ORIGIN must be the public HTTPS Django host, not localhost."
        )
    if origin and not origin_is_healthy(origin):
        print(
            f"WARN: {origin} is not the TalentBridge Django app "
            f"(missing {origin}/__deploy__/health/). "
            "Omitting production OAuth meta until Render deploys this repo."
        )
        return ""
    return origin


def _static_link(target, from_page):
    destination = OUTPUT / target
    relative = os.path.relpath(destination, (OUTPUT / from_page).parent)
    return relative.replace("\\", "/")


def _static_condition(expression):
    expression = expression.strip()
    if expression == "validlink":
        return True
    # The static preview cannot inspect the server's OAuth credentials. Keep
    # provider buttons active so demo-forms.js can forward them to Django,
    # where the live configuration is checked before OAuth starts.
    if expression == "google_login_enabled":
        return True
    if expression == "demo_role":
        return True
    if expression.lower() in {"true", "1"}:
        return True
    if expression.startswith("not "):
        return not _static_condition(expression[4:])
    return False


def _render_static_preview(text, from_page):
    output = []
    stack = []
    visible = True

    for token in TEMPLATE_TOKEN.split(text):
        if not token:
            continue
        if token.startswith("{{"):
            if visible:
                output.append(STATIC_TEMPLATE_VALUES.get(token[2:-2].strip(), ""))
            continue
        if not token.startswith("{%"):
            if visible:
                output.append(token)
            continue

        tag = token[2:-2].strip()
        command, _, argument = tag.partition(" ")
        argument = argument.strip()
        if command == "if":
            condition = _static_condition(argument)
            stack.append({"kind": "if", "parent": visible, "matched": condition})
            visible = visible and condition
        elif command == "elif":
            if not stack or stack[-1]["kind"] != "if":
                raise RuntimeError(f"Unmatched Django elif tag in {from_page}")
            frame = stack[-1]
            condition = _static_condition(argument)
            visible = frame["parent"] and not frame["matched"] and condition
            frame["matched"] = frame["matched"] or condition
        elif command == "else":
            if not stack or stack[-1]["kind"] != "if":
                raise RuntimeError(f"Unmatched Django else tag in {from_page}")
            frame = stack[-1]
            visible = frame["parent"] and not frame["matched"]
            frame["matched"] = True
        elif command == "endif":
            if not stack or stack[-1]["kind"] != "if":
                raise RuntimeError(f"Unmatched Django endif tag in {from_page}")
            visible = stack.pop()["parent"]
        elif command == "for":
            stack.append({"kind": "for", "parent": visible})
            visible = False
        elif command == "empty":
            if not stack or stack[-1]["kind"] != "for":
                raise RuntimeError(f"Unmatched Django empty tag in {from_page}")
            visible = stack[-1]["parent"]
        elif command == "endfor":
            if not stack or stack[-1]["kind"] != "for":
                raise RuntimeError(f"Unmatched Django endfor tag in {from_page}")
            visible = stack.pop()["parent"]
        elif command == "with":
            stack.append({"kind": "with", "parent": visible})
        elif command == "endwith":
            if not stack or stack[-1]["kind"] != "with":
                raise RuntimeError(f"Unmatched Django endwith tag in {from_page}")
            visible = stack.pop()["parent"]
        elif command == "url":
            if visible:
                match = re.match(r"""['"]([^'"]+)['"]""", argument)
                if not match:
                    raise RuntimeError(f"Unsupported Django URL tag in {from_page}: {tag}")
                route_name = match.group(1)
                # Static preview: map known routes; unknown routes become inert anchors.
                if route_name in STATIC_ROUTE_PAGES:
                    output.append(_static_link(STATIC_ROUTE_PAGES[route_name], from_page))
                else:
                    output.append("#")
        elif command == "static":
            if visible:
                match = re.fullmatch(r"""['"]([^'"]+)['"]""", argument)
                if not match:
                    raise RuntimeError(f"Unsupported Django static tag in {from_page}: {tag}")
                asset = Path(match.group(1))
                if asset.is_absolute() or ".." in asset.parts:
                    raise RuntimeError(f"Invalid Django static asset in {from_page}: {tag}")
                if asset.parts and asset.parts[0] in PUBLIC_DIR_MAP:
                    mapped = PUBLIC_DIR_MAP[asset.parts[0]] / Path(*asset.parts[1:])
                    target = asset.as_posix()
                    found = mapped.is_file()
                else:
                    matches = []
                    for directory, src_root in PUBLIC_DIR_MAP.items():
                        candidate = src_root / asset
                        if candidate.is_file():
                            matches.append(f"{directory}/{asset.as_posix()}")
                    # Fallback: unique basename search (e.g. static 'site-header.css')
                    if not matches and asset.name == asset.as_posix():
                        for directory, src_root in PUBLIC_DIR_MAP.items():
                            if not src_root.is_dir():
                                continue
                            for candidate in src_root.rglob(asset.name):
                                if candidate.is_file():
                                    rel = candidate.relative_to(src_root).as_posix()
                                    matches.append(f"{directory}/{rel}")
                    if len(matches) != 1:
                        raise RuntimeError(
                            f"Could not uniquely resolve Django static asset in {from_page}: {tag} "
                            f"(matches={matches})"
                        )
                    target = matches[0]
                    found = True
                if not found:
                    raise RuntimeError(f"Missing Django static asset in {from_page}: {tag}")
                output.append(_static_link(target, from_page))
        elif command not in {"csrf_token", "load", "block", "endblock"}:
            raise RuntimeError(f"Unsupported Django template tag in {from_page}: {tag}")

    if stack:
        raise RuntimeError(f"Unclosed Django template block in {from_page}")

    rendered = "".join(output)

    def rewrite_path(match):
        prefix, quote, path, _ = match.groups()
        route = urlsplit(path)
        target = STATIC_PATH_PAGES.get(route.path)
        if target is None:
            return match.group(0)
        suffix = f"?{route.query}" if route.query else ""
        if route.fragment:
            suffix += f"#{route.fragment}"
        return f"{prefix}{quote}{_static_link(target, from_page)}{suffix}{quote}"

    return re.sub(
        r"""((?:href|action)\s*=\s*)(["'])(/[^"']*)(\2)""",
        lambda match: rewrite_path(match),
        rendered,
        flags=re.IGNORECASE,
    )


def build():
    # `site/` is generated output. Remove stale files before copying current sources,
    # so deleted/renamed assets and templates cannot linger in the static preview.
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(FRONTEND / "index.html", OUTPUT / "index.html")
    favicon_src = FRONTEND / "assets" / "images" / "talentbridge-mark.svg"
    if favicon_src.is_file():
        shutil.copy2(favicon_src, OUTPUT / "favicon.svg")
    for directory, source in PUBLIC_DIR_MAP.items():
        if source.is_dir():
            shutil.copytree(source, OUTPUT / directory, dirs_exist_ok=True)
    shutil.copy2(FRONTEND / "pages" / "404.html", OUTPUT / "404.html")
    for html_file in OUTPUT.rglob("*.html"):
        text = html_file.read_text(encoding="utf-8-sig")
        from_page = html_file.relative_to(OUTPUT)
        text = _render_static_preview(text, from_page)
        if re.search(r"\{%|{{", text):
            raise RuntimeError(f"Unrendered Django template syntax in {html_file.relative_to(OUTPUT)}")

        relative_stylesheet = Path(
            *([".."] * len(from_page.parent.parts)), "css", "site-experience.css"
        )
        relative_script = Path(
            *([".."] * len(from_page.parent.parts)), "js", "site-experience.js"
        )
        relative_favicon = Path(
            *([".."] * len(from_page.parent.parts)), "favicon.svg"
        )
        if 'rel="icon"' not in text and "rel='icon'" not in text:
            favicon = f'<link rel="icon" type="image/svg+xml" href="{relative_favicon.as_posix()}">\n'
            text = re.sub(r"</head>", favicon + "</head>", text, count=1, flags=re.IGNORECASE)
        if "site-experience.css" not in text:
            stylesheet = f'<link rel="stylesheet" href="{relative_stylesheet.as_posix()}">\n'
            text = re.sub(r"</head>", stylesheet + "</head>", text, count=1, flags=re.IGNORECASE)
        if "site-experience.js" not in text:
            script = f'<script src="{relative_script.as_posix()}"></script>\n'
            text = re.sub(r"</body>", script + "</body>", text, count=1, flags=re.IGNORECASE)

        if "</body>" in text and "js/core/host-runtime.js" not in text:
            depth = [".."] * len(from_page.parent.parts)
            bust = "20261120-universal"
            host_path = Path(*depth, "js/core/host-runtime.js")
            demo_path = Path(*depth, "js/core/demo-forms.js")
            scripts = ""
            if "js/core/demo-forms.js" not in text:
                scripts = (
                    f'<script src="{host_path.as_posix()}?v={bust}"></script>\n'
                    f'<script src="{demo_path.as_posix()}?v={bust}"></script>\n'
                )
            text = text.replace("</body>", scripts + "</body>")
            html_file.write_text(text, encoding="utf-8")
        else:
            html_file.write_text(text, encoding="utf-8")

    # Pretty URL folders so /login/, /jobs/, /employer/, etc. work on GitHub Pages.
    _write_pretty_route_indexes()

    # Mark static Pages HTML + inject production Django origin for real Google OAuth.
    django_origin = _resolve_django_origin()
    if not django_origin:
        print(
            "WARN: No TALENTBRIDGE_DJANGO_ORIGIN — Pages Google sign-in will show config error "
            "until config/talentbridge_django_origin.txt is set."
        )
    else:
        print(f"Django OAuth handoff origin: {django_origin}")

    origin_block = (
        '<meta name="talentbridge-django-origin-local" content="http://127.0.0.1:8000">\n'
    )
    if django_origin:
        safe_js = django_origin.replace("\\", "\\\\").replace('"', '\\"')
        origin_block += (
            f'<meta name="talentbridge-django-origin" content="{django_origin}">\n'
            f'<script>window.TALENTBRIDGE_DJANGO_ORIGIN="{safe_js}";</script>\n'
        )

    for html_file in OUTPUT.rglob("*.html"):
        text = html_file.read_text(encoding="utf-8-sig")
        if "data-static-preview" not in text:
            text = re.sub(
                r"<html\b([^>]*)>",
                r'<html\1 data-static-preview="1">',
                text,
                count=1,
                flags=re.IGNORECASE,
            )
        if origin_block and 'name="talentbridge-django-origin-local"' not in text:
            text = re.sub(
                r"<head\b([^>]*)>",
                r"<head\1>\n" + origin_block,
                text,
                count=1,
                flags=re.IGNORECASE,
            )
        html_file.write_text(text, encoding="utf-8")

    # Custom domain for GitHub Pages (committed at repo root; copied into publish output).
    cname_src = ROOT / "CNAME"
    if cname_src.is_file():
        shutil.copy2(cname_src, OUTPUT / "CNAME")
    # Prevent GitHub Pages from running Jekyll on the uploaded artifact.
    (OUTPUT / ".nojekyll").write_text("", encoding="utf-8")

    print(f"Static site built in {OUTPUT.relative_to(ROOT)}")


def _write_pretty_route_indexes():
    """Create /route/index.html redirects for GitHub Pages pretty URLs."""
    routes = dict(STATIC_PATH_PAGES)
    # Auto-map every public HTML page so /posting-job/ etc. never 404 on Pages.
    pages_dir = OUTPUT / "pages"
    if pages_dir.is_dir():
        for html_file in pages_dir.glob("*.html"):
            if html_file.name.lower() == "404.html":
                continue
            slug = html_file.stem
            routes.setdefault(f"/{slug}/", f"pages/{html_file.name}")

    for route_path, target in routes.items():
        slug = route_path.strip("/")
        if not slug:
            continue
        target_path = OUTPUT / target
        if not target_path.is_file():
            continue
        dest_dir = OUTPUT / Path(slug)
        dest_dir.mkdir(parents=True, exist_ok=True)
        relative = os.path.relpath(target_path, dest_dir).replace("\\", "/")
        (dest_dir / "index.html").write_text(
            (
                "<!DOCTYPE html>\n"
                '<html lang="en" data-static-preview="1">\n'
                "<head>\n"
                '  <meta charset="utf-8">\n'
                f'  <meta http-equiv="refresh" content="0; url={relative}">\n'
                f'  <link rel="canonical" href="/{target}">\n'
                f"  <script>location.replace({relative!r});</script>\n"
                "  <title>Redirecting…</title>\n"
                "</head>\n"
                f'<body><p><a href="{relative}">Continue to TalentBridge AI</a></p></body>\n'
                "</html>\n"
            ),
            encoding="utf-8",
        )


if __name__ == "__main__":
    build()
