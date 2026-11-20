#!/usr/bin/env python3
"""Build static site and publish to GitHub / Render when credentials are present."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _log(msg: str) -> None:
    print(msg, flush=True)


def _run(cmd: list[str], *, cwd: Path = ROOT, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, text=True, check=check)


def _parsed_env() -> dict[str, str]:
    path = ROOT / ".env"
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def build_static_site() -> None:
    _log("Building static site (GitHub Pages artifact)...")
    _run([sys.executable, str(ROOT / "tools" / "build_static.py")])


def git_push_if_ahead() -> None:
    if not (ROOT / ".git").is_dir():
        _log("Git: not a repository; skipping push.")
        return
    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture=True).stdout.strip()
    if not branch:
        return
    _run(["git", "fetch", "origin", branch], check=False)
    ahead = _run(
        ["git", "rev-list", "--count", f"origin/{branch}..HEAD"],
        capture=True,
        check=False,
    )
    count = (ahead.stdout or "0").strip()
    if not count.isdigit() or int(count) < 1:
        _log(f"Git: {branch} is already synced with origin (no push needed).")
        return
    _log(f"Git: pushing {count} commit(s) to origin/{branch} (triggers GitHub Pages Actions)...")
    _run(["git", "push", "origin", branch])


def render_sync_from_env() -> None:
    cfg = _parsed_env()
    api_key = (cfg.get("RENDER_API_KEY") or os.environ.get("RENDER_API_KEY", "")).strip()
    client_id = cfg.get("GOOGLE_OAUTH_CLIENT_ID", "").strip()
    client_secret = cfg.get("GOOGLE_OAUTH_CLIENT_SECRET", "").strip()
    if not api_key:
        _log("Render: RENDER_API_KEY not set in .env — skip live Django sync (add key once for auto-deploy).")
        return
    if not client_id or not client_secret:
        _log("Render: Google OAuth incomplete in .env — skip Render secret sync.")
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    def api(method: str, url: str, body: dict | list | None = None):
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))

    _log("Render: looking up service talentbridge-ai...")
    try:
        services = api("GET", "https://api.render.com/v1/services?limit=50")
    except urllib.error.HTTPError as exc:
        _log(f"Render API error: HTTP {exc.code}. Check RENDER_API_KEY.")
        return

    service_id = None
    host_name = None
    for row in services:
        item = row.get("service") if isinstance(row, dict) and row.get("service") else row
        if not isinstance(item, dict):
            continue
        if item.get("name") == "talentbridge-ai":
            service_id = item.get("id")
            details = item.get("serviceDetails") or {}
            host_name = details.get("hostName")
            break
    if not service_id:
        _log("Render: service 'talentbridge-ai' not found — connect Blueprint once at render.com.")
        return

    existing = api("GET", f"https://api.render.com/v1/services/{service_id}/env-vars")
    merged: dict[str, str] = {}
    for row in existing:
        ev = row.get("envVar") if isinstance(row, dict) and row.get("envVar") else row
        if isinstance(ev, dict) and ev.get("key"):
            merged[str(ev["key"])] = str(ev.get("value") or "")
    merged.update(
        {
            "GOOGLE_OAUTH_CLIENT_ID": client_id,
            "GOOGLE_OAUTH_CLIENT_SECRET": client_secret,
            "DJANGO_ENV": "production",
            "DJANGO_DEBUG": "false",
            "DJANGO_BEHIND_PROXY": "true",
            "DJANGO_SECURE_SSL_REDIRECT": "true",
        }
    )
    body = [{"key": k, "value": v} for k, v in sorted(merged.items())]
    api("PUT", f"https://api.render.com/v1/services/{service_id}/env-vars", body)
    api("POST", f"https://api.render.com/v1/services/{service_id}/deploys", {})
    _log("Render: Google secrets synced and deploy triggered (secrets not printed).")
    if host_name:
        _log(f"Render: when live, open https://{host_name}/login/")


def main() -> int:
    cfg = _parsed_env()
    auto = (cfg.get("TALENTBRIDGEAI_AUTO_PUBLISH", "1") or "1").strip().lower()
    if auto in {"0", "false", "no", "off"}:
        _log("TALENTBRIDGEAI_AUTO_PUBLISH is off; publish steps skipped.")
        return 0
    build_static_site()
    git_push_if_ahead()
    render_sync_from_env()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        _log(f"Publish failed: {exc}")
        raise SystemExit(exc.returncode or 1) from exc