from pathlib import Path
import os
import sys
import traceback

from django.conf import settings
from django.core.management import call_command
from django.test import Client
from django.urls import get_resolver
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

PROJECT = Path(settings.BASE_DIR).resolve().parent
DJANGO = Path(settings.BASE_DIR).resolve()

SKIP = {
    ".git", ".venv", "venv", "node_modules",
    "__pycache__", ".idea", ".vscode"
}

def files(exts):
    result = []
    for base, dirs, names in os.walk(PROJECT):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for name in names:
            if Path(name).suffix.lower() in exts:
                result.append(Path(base) / name)
    return sorted(result)

print("\n" + "=" * 65)
print("       TALENTBRIDGE AI - COMPLETE PROJECT AUDIT")
print("=" * 65)

# 1. HTML FILE AUDIT
html = files({".html"})
print(f"\n[1] HTML FILES FOUND: {len(html)}")

for f in html:
    print("FOUND:", f.relative_to(PROJECT))

# 2. PYTHON FILE AUDIT
py = files({".py"})
print(f"\n[2] PYTHON FILES FOUND: {len(py)}")

for f in py:
    if ".venv" not in str(f):
        print("PYTHON:", f.relative_to(PROJECT))

# 3. CSS AND JS AUDIT
for ext, label in [( {".css"}, "CSS"), ({".js"}, "JAVASCRIPT")]:
    found = files(ext)
    print(f"\n[3] {label} FILES: {len(found)}")
    for f in found:
        print("FOUND:", f.relative_to(PROJECT))

# 4. URL ROUTE AUDIT
print("\n[4] DJANGO URL ROUTES")

def show_routes(patterns, prefix=""):
    for p in patterns:
        route = prefix + str(p.pattern)
        if hasattr(p, "url_patterns"):
            show_routes(p.url_patterns, route)
        else:
            print("ROUTE:", route, "| NAME:", p.name)

show_routes(get_resolver().url_patterns)

# 5. HTML HTTP TEST
print("\n[5] HTML PAGE HTTP TEST")

client = Client(HTTP_HOST="127.0.0.1")
client.raise_request_exception = False

for f in html:
    try:
        rel = f.relative_to(PROJECT).as_posix()

        if rel.startswith("pages/"):
            url = "/" + rel
        elif rel == "index.html":
            url = "/"
        else:
            print("FILE ONLY (URL NOT INFERRED):", rel)
            continue

        response = client.get(url)
        print(response.status_code, "|", url)

    except Exception as e:
        print("ERROR:", f.name, "|", str(e))

# 6. DJANGO SYSTEM CHECK
print("\n[6] DJANGO SYSTEM CHECK")
try:
    call_command("check", verbosity=1)
except Exception:
    traceback.print_exc()

# 7. DATABASE CHECK
print("\n[7] DATABASE CONNECTION")
try:
    connection.ensure_connection()
    print("DATABASE CONNECTED:", connection.vendor)
    print("DATABASE NAME:", connection.settings_dict["NAME"])

    executor = MigrationExecutor(connection)
    pending = executor.migration_plan(executor.loader.graph.leaf_nodes())
    print("PENDING MIGRATIONS:", len(pending))

    for migration, backwards in pending:
        print("PENDING:", migration.app_label, migration.name)

except Exception:
    traceback.print_exc()

# 8. OAUTH CONFIGURATION CHECK (never print secrets)
print("\n[8] GOOGLE OAUTH CONFIGURATION")
try:
    providers = getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    google = providers.get("google", {})
    app = google.get("APP", {})
    print("GOOGLE PROVIDER:", "CONFIGURED" if google else "NOT FOUND")
    print("CLIENT ID:", "PRESENT" if app.get("client_id") else "NOT CONFIGURED")
    print("CLIENT SECRET:", "PRESENT" if app.get("secret") else "NOT CONFIGURED")
except Exception as e:
    print("OAUTH CHECK ERROR:", e)

# 9. IMPORTANT FILES
print("\n[9] IMPORTANT PROJECT FILES")
important = [
    "manage.py",
    "config/settings.py",
    "config/urls.py",
    "database/TalentBridgeAI.sqlite3",
    ".env",
    ".env.example",
]

for item in important:
    p = PROJECT / item
    if not p.exists():
        p = DJANGO / item
    print(("FOUND " if p.exists() else "MISSING ") + item)

print("\n" + "=" * 65)
print("             COMPLETE AUDIT FINISHED")
print("=" * 65)
