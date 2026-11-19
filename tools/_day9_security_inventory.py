"""Day 9: safe security inventory — never prints secret values."""
from __future__ import annotations

import ast
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DJANGO = ROOT / "backend" / "legacy-django"
OUT = ROOT / "docs" / "reports" / "_day9_security_inventory.json"

sys.path.insert(0, str(DJANGO))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Load dotenv without printing values
try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except Exception:
    pass

import django

django.setup()
from django.conf import settings
from django.urls import get_resolver

SECRET_NAME_HINTS = re.compile(
    r"(SECRET|PASSWORD|PASSWD|TOKEN|API[_-]?KEY|PRIVATE[_-]?KEY|CLIENT_SECRET|AWS_|GCP_|AZURE_)",
    re.I,
)
HARDCODED_ASSIGN = re.compile(
    r"""(?i)(SECRET_KEY|PASSWORD|CLIENT_SECRET|API_KEY|ACCESS_TOKEN|PRIVATE_KEY)\s*=\s*['\"][^'\"]{8,}['\"]"""
)


def redact_env_presence(keys: list[str]) -> dict:
    out = {}
    for k in keys:
        v = os.environ.get(k)
        if v is None or v == "":
            out[k] = "UNSET"
        else:
            out[k] = f"SET(len={len(v)})"
    return out


def scan_file_for_patterns(path: Path) -> list[dict]:
    findings = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return [{"file": str(path), "error": type(e).__name__}]
    # skip large binaries / media
    if len(text) > 2_000_000:
        return findings
    for i, line in enumerate(text.splitlines(), 1):
        if HARDCODED_ASSIGN.search(line):
            # never include the value — only var-ish left side
            left = line.split("=", 1)[0].strip()[:80]
            findings.append(
                {
                    "file": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "line": i,
                    "kind": "hardcoded_assign_pattern",
                    "lhs": left,
                }
            )
    return findings


interesting_ext = {".py", ".js", ".ps1", ".bat", ".cmd", ".env", ".yml", ".yaml", ".toml", ".json", ".md", ".txt", ".html"}
skip_dirs = {
    ".venv",
    "venv",
    "node_modules",
    "staticfiles",
    "private_media",
    "backups",
    "releases",
    "__pycache__",
    ".git",
    "unslop",
}

hardcoded_hits: list[dict] = []
for p in ROOT.rglob("*"):
    if not p.is_file():
        continue
    if any(part in skip_dirs for part in p.parts):
        continue
    if p.suffix.lower() not in interesting_ext and p.name not in {".env.example", "Pipfile"}:
        continue
    # never open .env contents for reporting secrets — only note existence
    if p.name == ".env" or p.name.startswith(".env.") and p.name != ".env.example":
        continue
    hardcoded_hits.extend(scan_file_for_patterns(p))

# Settings snapshot (safe)
safe_settings = {
    "DEBUG": bool(settings.DEBUG),
    "ALLOWED_HOSTS": list(settings.ALLOWED_HOSTS),
    "SECRET_KEY_len": len(getattr(settings, "SECRET_KEY", "") or ""),
    "SECRET_KEY_prefix_insecure": str(getattr(settings, "SECRET_KEY", "")).startswith("django-insecure"),
    "MEDIA_ROOT": str(settings.MEDIA_ROOT),
    "MEDIA_URL": repr(getattr(settings, "MEDIA_URL", None)),
    "DATA_UPLOAD_MAX_MEMORY_SIZE": getattr(settings, "DATA_UPLOAD_MAX_MEMORY_SIZE", None),
    "FILE_UPLOAD_MAX_MEMORY_SIZE": getattr(settings, "FILE_UPLOAD_MAX_MEMORY_SIZE", None),
    "CSRF_TRUSTED_ORIGINS": list(getattr(settings, "CSRF_TRUSTED_ORIGINS", [])),
    "SESSION_COOKIE_SECURE": getattr(settings, "SESSION_COOKIE_SECURE", None),
    "CSRF_COOKIE_SECURE": getattr(settings, "CSRF_COOKIE_SECURE", None),
    "SESSION_COOKIE_HTTPONLY": getattr(settings, "SESSION_COOKIE_HTTPONLY", None),
    "SESSION_COOKIE_SAMESITE": getattr(settings, "SESSION_COOKIE_SAMESITE", None),
    "CSRF_COOKIE_HTTPONLY": getattr(settings, "CSRF_COOKIE_HTTPONLY", None),
    "SECURE_SSL_REDIRECT": getattr(settings, "SECURE_SSL_REDIRECT", None),
    "SECURE_HSTS_SECONDS": getattr(settings, "SECURE_HSTS_SECONDS", None),
    "SECURE_CONTENT_TYPE_NOSNIFF": getattr(settings, "SECURE_CONTENT_TYPE_NOSNIFF", None),
    "SECURE_REFERRER_POLICY": getattr(settings, "SECURE_REFERRER_POLICY", None),
    "X_FRAME_OPTIONS": getattr(settings, "X_FRAME_OPTIONS", None),
    "MIDDLEWARE": list(settings.MIDDLEWARE),
    "INSTALLED_APPS": list(settings.INSTALLED_APPS),
    "AUTH_PASSWORD_VALIDATORS_count": len(settings.AUTH_PASSWORD_VALIDATORS),
    "EMAIL_BACKEND": settings.EMAIL_BACKEND,
    "DATABASE_ENGINE": settings.DATABASES["default"]["ENGINE"],
    "DATABASE_NAME": str(settings.DATABASES["default"].get("NAME")),
}

env_presence = redact_env_presence(
    [
        "DJANGO_SECRET_KEY",
        "DJANGO_DEBUG",
        "DJANGO_ENV",
        "DJANGO_ALLOWED_HOSTS",
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "EMAIL_HOST",
        "EMAIL_HOST_PASSWORD",
        "DB_PASSWORD",
        "DB_USER",
        "DB_NAME",
        "DB_ENGINE",
    ]
)

# FileField / ImageField inventory
from django.apps import apps

upload_fields = []
for model in apps.get_models():
    for field in model._meta.get_fields():
        if field.__class__.__name__ in {"FileField", "ImageField"}:
            upload_fields.append(
                {
                    "model": f"{model._meta.app_label}.{model.__name__}",
                    "field": field.name,
                    "class": field.__class__.__name__,
                    "upload_to": getattr(field, "upload_to", None)
                    if not callable(getattr(field, "upload_to", None))
                    else "<callable>",
                }
            )

# mark_safe / |safe / RawSQL
code_risk = {"mark_safe": [], "safe_filter": [], "raw_sql": [], "csrf_exempt": [], "open_redirect_next": []}
py_roots = [DJANGO / "jobs", DJANGO / "config", ROOT / "tools"]
for base in py_roots:
    if not base.exists():
        continue
    for p in base.rglob("*.py"):
        text = p.read_text(encoding="utf-8", errors="replace")
        rel = str(p.relative_to(ROOT)).replace("\\", "/")
        for i, line in enumerate(text.splitlines(), 1):
            if "mark_safe" in line or "SafeString" in line:
                code_risk["mark_safe"].append({"file": rel, "line": i, "snip": line.strip()[:120]})
            if "RawSQL" in line or "cursor.execute" in line or ".raw(" in line:
                code_risk["raw_sql"].append({"file": rel, "line": i, "snip": line.strip()[:120]})
            if "csrf_exempt" in line:
                code_risk["csrf_exempt"].append({"file": rel, "line": i, "snip": line.strip()[:120]})
            if "redirect(" in line and ("next" in line or "request.GET.get" in line):
                code_risk["open_redirect_next"].append({"file": rel, "line": i, "snip": line.strip()[:120]})

# template |safe
for p in (ROOT / "frontend").rglob("*.html"):
    if "unslop" in p.parts:
        continue
    text = p.read_text(encoding="utf-8", errors="replace")
    rel = str(p.relative_to(ROOT)).replace("\\", "/")
    for i, line in enumerate(text.splitlines(), 1):
        if "|safe" in line or "| safeseq" in line:
            code_risk["safe_filter"].append({"file": rel, "line": i, "snip": line.strip()[:120]})

payload = {
    "project_root": str(ROOT),
    "django_version": django.get_version(),
    "python_version": sys.version.split()[0],
    "settings": safe_settings,
    "env_presence": env_presence,
    "upload_fields": upload_fields,
    "hardcoded_pattern_hits": hardcoded_hits[:80],
    "hardcoded_hit_count": len(hardcoded_hits),
    "code_risk_counts": {k: len(v) for k, v in code_risk.items()},
    "code_risk": {k: v[:40] for k, v in code_risk.items()},
    "dotenv_example_exists": (ROOT / ".env.example").exists(),
    "dotenv_exists": (ROOT / ".env").exists(),
    "django_secret_file_exists": (ROOT / ".django_secret_key").exists(),
    "private_media_exists": (ROOT / "private_media").exists(),
    "git_dir_exists": (ROOT / ".git").exists(),
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
print("wrote", OUT)
print("django", payload["django_version"], "python", payload["python_version"], "DEBUG", safe_settings["DEBUG"])
print("upload_fields", len(upload_fields), "hardcoded_hits", len(hardcoded_hits))
print("code_risk", payload["code_risk_counts"])
