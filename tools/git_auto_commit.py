#!/usr/bin/env python3
"""Commit tracked project changes when TALENTBRIDGEAI_AUTO_COMMIT=1 in .env."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PATH_PARTS = {".venv", "venv", "site", "__pycache__", "logs", "backups", "private_media"}


def _env_flag() -> bool:
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return False
    for line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line.startswith("TALENTBRIDGEAI_AUTO_COMMIT="):
            return line.split("=", 1)[1].strip().lower() in {"1", "true", "yes", "on"}
    return False


def _status_porcelain() -> str:
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return r.stdout or ""


def _should_skip(path: str) -> bool:
    parts = Path(path.replace("\\", "/")).parts
    return any(p in SKIP_PATH_PARTS for p in parts)


def main() -> int:
    if not _env_flag():
        print("AUTO_COMMIT off (set TALENTBRIDGEAI_AUTO_COMMIT=1 in .env to commit+push on sync).")
        return 0
    lines = [ln for ln in _status_porcelain().splitlines() if ln.strip()]
    paths = []
    for ln in lines:
        if len(ln) < 4:
            continue
        path = ln[3:].strip()
        if _should_skip(path):
            continue
        paths.append(path)
    if not paths:
        print("Nothing to auto-commit.")
        return 0
    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=True)
    subprocess.run(
        [
            "git",
            "commit",
            "-m",
            "Auto sync from local workstation (domain + localhost profiles).",
        ],
        cwd=ROOT,
        check=True,
    )
    print(f"Auto-committed {len(paths)} path(s).")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"Auto-commit failed: {exc}", file=sys.stderr)
        raise SystemExit(exc.returncode or 1) from exc