#!/usr/bin/env python3
"""Build static site and push to GitHub (triggers Pages deploy)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _log(msg: str) -> None:
    print(msg, flush=True)


def _run(cmd: list[str], *, cwd: Path = ROOT, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, text=True, check=check)


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


def main() -> int:
    _run([sys.executable, str(ROOT / "tools" / "ensure_github_remote.py")])
    build_static_site()
    git_push_if_ahead()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        _log(f"Publish failed: {exc}")
        raise SystemExit(exc.returncode or 1) from exc