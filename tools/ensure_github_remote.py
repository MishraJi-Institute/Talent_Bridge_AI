#!/usr/bin/env python3
"""Verify this folder is linked to the TalentBridge GitHub repo."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EXPECTED = "github.com/MishraJi-Institute/Talent_Bridge_AI"
ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    if not (ROOT / ".git").is_dir():
        print("ERROR: Not a git repository.", file=sys.stderr)
        return 1
    out = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    url = (out.stdout or "").strip()
    if out.returncode or EXPECTED not in url.replace("\\", "/"):
        print(
            f"ERROR: origin must be MishraJi-Institute/Talent_Bridge_AI (got: {url or 'missing'})",
            file=sys.stderr,
        )
        return 1
    branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if branch != "main":
        print(f"WARN: branch is {branch}; domain deploys from main.", file=sys.stderr)
    print(f"GitHub OK: {url} (branch {branch})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())