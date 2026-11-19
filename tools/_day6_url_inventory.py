"""Day 6 read-only URL inventory. Writes docs/reports/_day6_url_inventory.json."""
from __future__ import annotations

import inspect
import json
import os
import re
from collections import Counter, defaultdict
from io import StringIO
from pathlib import Path

DJANGO_ROOT = Path(__file__).resolve().parents[1] / "backend" / "legacy-django"
os.chdir(DJANGO_ROOT)
import sys

sys.path.insert(0, str(DJANGO_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.conf import settings
from django.core.management import call_command
from django.test import Client
from django.urls import NoReverseMatch, URLPattern, URLResolver, get_resolver, reverse

FRONTEND = Path(settings.FRONTEND_ROOT)
PAGES_DIR = FRONTEND / "pages"
AUTH_MARKERS = (
    "login_required",
    "permission_required",
    "user_passes_test",
    "staff_member_required",
)


def pattern_str(pattern) -> str:
    return str(pattern)


def view_info(callback):
    if callback is None:
        return {"kind": "none", "qual": "", "file": "", "decorators": [], "mixins": []}
    target = callback
    decorators = []
    seen = set()
    while hasattr(target, "__wrapped__") and id(target) not in seen:
        seen.add(id(target))
        n = getattr(target, "__name__", "")
        if n and n not in {"view", "wrapper", "inner", "bound_method"}:
            decorators.append(n)
        target = target.__wrapped__
    cls = getattr(callback, "view_class", None) or getattr(target, "view_class", None)
    if cls is not None:
        bases = [
            b.__name__
            for b in cls.__mro__
            if b.__name__.endswith("Mixin")
            or b.__name__
            in {
                "View",
                "TemplateView",
                "FormView",
                "PasswordResetView",
                "PasswordResetDoneView",
                "PasswordResetConfirmView",
                "PasswordResetCompleteView",
                "RedirectView",
            }
        ]
        return {
            "kind": "cbv",
            "qual": f"{cls.__module__}.{cls.__name__}",
            "file": inspect.getsourcefile(cls) or "",
            "decorators": decorators,
            "mixins": bases,
        }
    mod = getattr(target, "__module__", "")
    name = getattr(target, "__name__", getattr(callback, "__name__", "?"))
    try:
        file = inspect.getsourcefile(target) or inspect.getsourcefile(callback) or ""
    except TypeError:
        file = ""
    return {
        "kind": "fbv",
        "qual": f"{mod}.{name}" if mod else name,
        "file": file,
        "decorators": decorators,
        "mixins": [],
    }


routes = []
name_to_patterns = defaultdict(list)


def walk(resolver, prefix="", namespace=None):
    for p in resolver.url_patterns:
        if isinstance(p, URLResolver):
            walk(p, prefix + pattern_str(p.pattern), p.namespace or namespace)
        elif isinstance(p, URLPattern):
            full = prefix + pattern_str(p.pattern)
            name = p.name
            full_name = f"{namespace}:{name}" if namespace and name else name
            vi = view_info(p.callback)
            default_args = dict(getattr(p, "default_args", None) or {})
            entry = {
                "pattern": full,
                "name": full_name,
                "namespace": namespace,
                "view": vi["qual"],
                "view_kind": vi["kind"],
                "view_file": vi["file"],
                "decorators": vi["decorators"],
                "mixins": vi["mixins"],
                "default_args": {
                    k: v if isinstance(v, (str, int, float, bool)) or v is None else str(v)
                    for k, v in default_args.items()
                },
            }
            routes.append(entry)
            if full_name:
                name_to_patterns[full_name].append(full)


walk(get_resolver())
name_counts = Counter(r["name"] for r in routes if r["name"])
dup_names = {n: c for n, c in name_counts.items() if c > 1}

import jobs.dev_preview_views as dpv
import jobs.views as jv


def analyze_func(fn):
    try:
        src = inspect.getsource(fn)
    except OSError as exc:
        return {"error": str(exc)}
    wraps = []
    cur = fn
    seen = set()
    while hasattr(cur, "__wrapped__") and id(cur) not in seen:
        seen.add(id(cur))
        wraps.append(getattr(cur, "__name__", "?"))
        cur = cur.__wrapped__
    templates = re.findall(r"['\"]([\w./-]+\.html)['\"]", src)
    methods = []
    if "require_POST" in src[:800]:
        methods.append("POST")
    m = re.search(r"require_http_methods\(\[([^\]]+)\]\)", src)
    if m:
        methods = re.findall(r"'(\w+)'", m.group(1))
    roles = []
    if "role" in src and ("employer" in src or "job_seeker" in src):
        roles.append("role-check-in-body")
    if "is_staff" in src or "is_superuser" in src:
        roles.append("staff-check-in-body")
    if "company__owner" in src or "owned_company" in src or "owner=request.user" in src:
        roles.append("ownership-check")
    return {
        "auth_markers": [m for m in AUTH_MARKERS if m in src[:1000]],
        "wraps": wraps,
        "templates": list(dict.fromkeys(templates))[:15],
        "methods": methods,
        "roles": roles,
        "login_required_wrap": "login_required" in wraps,
    }


view_analysis = {}
for name, obj in inspect.getmembers(jv, inspect.isfunction):
    if obj.__module__ == "jobs.views":
        view_analysis[f"jobs.views.{name}"] = analyze_func(obj)
for name, obj in inspect.getmembers(dpv, inspect.isfunction):
    if obj.__module__ == "jobs.dev_preview_views":
        view_analysis[f"jobs.dev_preview_views.{name}"] = analyze_func(obj)

from config import urls as root_urls

page_templates = {}
for slug, filename in dict(root_urls.PAGES).items():
    path = PAGES_DIR / filename
    page_templates[slug] = {
        "file": filename,
        "exists": path.is_file(),
        "path": str(path),
    }

reverse_ok = {}
reverse_err = {}
for n in sorted({r["name"] for r in routes if r["name"]}):
    try:
        reverse_ok[n] = reverse(n)
        continue
    except NoReverseMatch:
        pass
    pat = next((r["pattern"] for r in routes if r["name"] == n), "")
    kwargs = {}
    for m in re.finditer(r"<int:(\w+)>", pat):
        kwargs[m.group(1)] = 1
    for m in re.finditer(r"<str:(\w+)>", pat):
        kwargs[m.group(1)] = "google"
    if "uidb64" in pat:
        kwargs["uidb64"] = "MQ"
        kwargs["token"] = "dummy-token"
    try:
        reverse_ok[n] = reverse(n, kwargs=kwargs) if kwargs else reverse(n)
    except Exception as exc:  # noqa: BLE001
        reverse_err[n] = str(exc).split("\n")[0][:160]

buf = StringIO()
call_command("check", stdout=buf, stderr=buf)
check_out = buf.getvalue().strip() or "System check identified no issues (0 silenced)."

client = Client()
smoke = {}
public_paths = [
    "/",
    "/login/",
    "/signup/",
    "/signup/job-seeker/",
    "/signup/employer/",
    "/jobs/",
    "/companies/",
    "/faq/",
    "/faqs/",
    "/pricing/",
    "/about/",
    "/contact/",
    "/forgot-password/",
    "/password-reset/",
    "/trust/",
    "/search/",
    "/css/base/style.css",
    "/js/core/script.js",
    "/images/talentbridge-mark.svg",
    "/admin/login/",
    "/accounts/login/",
]
protected_paths = [
    "/dashboard/",
    "/resume-builder/",
    "/saved-jobs/",
    "/notifications/",
    "/interviews/",
    "/admin-dashboard/",
    "/jobs/create/",
    "/resume/download/",
    "/profile/",
    "/manage-jobs/",
]
for p in public_paths + protected_paths:
    try:
        r = client.get(p, follow=False)
        smoke[p] = {"status": r.status_code, "loc": (r.headers.get("Location") or "")[:120]}
    except Exception as exc:  # noqa: BLE001
        smoke[p] = {"status": "ERR", "loc": type(exc).__name__}

out = {
    "project_root": str(settings.PROJECT_ROOT),
    "route_count_total": len(routes),
    "dup_names": dup_names,
    "dup_name_patterns": {n: name_to_patterns[n] for n in dup_names},
    "reverse_ok_count": len(reverse_ok),
    "reverse_err_count": len(reverse_err),
    "reverse_err": reverse_err,
    "check": check_out,
    "pages_missing_templates": {
        k: v for k, v in page_templates.items() if not v["exists"]
    },
    "smoke": smoke,
    "routes": routes,
    "view_analysis": view_analysis,
    "page_templates": page_templates,
}

dest = Path(settings.PROJECT_ROOT) / "docs" / "reports" / "_day6_url_inventory.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print("ROUTES", len(routes))
print("DUP_NAMES", dup_names)
print("REVERSE_OK", len(reverse_ok), "ERR", len(reverse_err))
print("MISSING_PAGE_TEMPLATES", list(out["pages_missing_templates"]))
print("CHECK", check_out)
print("JSON", dest)
for p, v in smoke.items():
    print("SMOKE", p, v["status"], v["loc"])
