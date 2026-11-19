"""Organize frontend CSS/JS into logical subfolders and rewrite references.

Safety:
  - Default mode is dry-run (no moves, no rewrites).
  - Use --apply to perform changes.
  - --apply creates a timestamped backup inventory under backups/.
  - Existing destinations are compared by SHA-256; collisions are not overwritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = ROOT / "frontend" / "css"
JS = ROOT / "frontend" / "js"
LOG: list[dict] = []

CSS_MAP = {
    "base": [
        "style.css",
        "tb-foundation.css",
        "tb-premium-system.css",
        "portal-pages.css",
        "redesign.css",
        "pro-upgrade.css",
    ],
    "components": [
        "site-header.css",
        "site-experience.css",
        "motion.css",
        "dark-mode.css",
        "landing-intro.css",
        "auth-enhancements.css",
        "auth-provider.css",
        "reference-image-integration.css",
        "admin.css",
        "dev-preview.css",
    ],
    "layouts": [],
    "pages": [
        "login.css",
        "login-10sec.css",
        "login-motion.css",
        "signup-role.css",
        "jobseeker-signup.css",
        "company-signup.css",
        "forgot-password.css",
        "job-listings.css",
        "jobseaker.css",
        "posting-job.css",
        "pricing.css",
        "resume-builder.css",
        "tb-homepage.css",
        "tb-homepage-attract.css",
        "tb-homepage-premium.css",
        "tb-homepage-elevate.css",
        "tb-layout-lock.css",
    ],
    "responsive": [
        "responsive-all.css",
        "responsive-fixes.css",
    ],
}

JS_MAP = {
    "core": [
        "script.js",
        "site-experience.js",
        "motion.js",
        "dark-mode.js",
        "demo-forms.js",
        "remove-static-preview-notice.js",
        "landing-intro.js",
        "pro-upgrade.js",
        "dev-preview.js",
        "tb-hero-network.js",
    ],
    "components": [],
    "authentication": [
        "google-oauth.js",
        "login-10sec.js",
        "company-signup.js",
        "dashboard-guard.js",
    ],
    "jobs": [
        "job-listings.js",
        "job-preview.js",
        "posting-job.js",
        "jobseaker.js",
        "resume-builder.js",
    ],
    "dashboards": [],  # existing dashboard/ tree stays
    "notifications": [],
}

# old filename -> new relative path under css/ or js/
css_targets: dict[str, str] = {}
js_targets: dict[str, str] = {}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def move_group(
    base: Path,
    mapping: dict[str, list[str]],
    targets: dict[str, str],
    *,
    dry_run: bool,
    allow_missing: bool,
) -> int:
    """Return number of hard errors."""
    errors = 0
    for folder, names in mapping.items():
        dest_dir = base / folder
        if dry_run:
            LOG.append({"action": "mkdir-planned", "path": _rel(dest_dir)})
        else:
            dest_dir.mkdir(parents=True, exist_ok=True)
            LOG.append({"action": "mkdir", "path": _rel(dest_dir)})
        for name in names:
            src = base / name
            dst = dest_dir / name
            rel_target = f"{folder}/{name}"
            if dst.exists() and not src.exists():
                targets[name] = rel_target
                LOG.append({"action": "already-at-destination", "dst": _rel(dst)})
                continue
            if not src.exists():
                LOG.append({"action": "skip-missing", "src": _rel(src)})
                if not allow_missing:
                    # Missing flat source is OK when destination already organized.
                    if not dst.exists():
                        errors += 1
                        LOG.append({"action": "error-missing-both", "name": name, "folder": folder})
                continue
            if dst.exists():
                src_hash = _sha256(src)
                dst_hash = _sha256(dst)
                if src_hash == dst_hash:
                    targets[name] = rel_target
                    LOG.append(
                        {
                            "action": "skip-exists-same",
                            "src": _rel(src),
                            "dst": _rel(dst),
                            "sha256": src_hash,
                        }
                    )
                else:
                    errors += 1
                    LOG.append(
                        {
                            "action": "error-collision-different",
                            "src": _rel(src),
                            "dst": _rel(dst),
                            "src_sha256": src_hash,
                            "dst_sha256": dst_hash,
                        }
                    )
                continue
            targets[name] = rel_target
            if dry_run:
                LOG.append({"action": "move-planned", "src": _rel(src), "dst": _rel(dst)})
            else:
                shutil.move(str(src), str(dst))
                LOG.append({"action": "move", "src": _rel(src), "dst": _rel(dst)})
    return errors


def rewrite_text(text: str) -> str:
    for name, rel in css_targets.items():
        patterns = [
            (rf'(["\'])(/?css/){re.escape(name)}', rf"\1\2{rel}"),
            (rf'(["\'])(\.\./+css/){re.escape(name)}', rf"\1\2{rel}"),
            (rf'(["\'])(css/){re.escape(name)}', rf"\1\2{rel}"),
        ]
        for pat, repl in patterns:
            text = re.sub(pat, repl, text)
    for name, rel in js_targets.items():
        patterns = [
            (rf'(["\'])(/?js/){re.escape(name)}', rf"\1\2{rel}"),
            (rf'(["\'])(\.\./+js/){re.escape(name)}', rf"\1\2{rel}"),
            (rf'(["\'])(js/){re.escape(name)}', rf"\1\2{rel}"),
        ]
        for pat, repl in patterns:
            text = re.sub(pat, repl, text)
    return text


def rewrite_file(path: Path, *, dry_run: bool) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        LOG.append({"action": "skip-encoding", "path": _rel(path)})
        return False
    updated = rewrite_text(text)
    if updated == text:
        return False
    if dry_run:
        LOG.append({"action": "rewrite-planned", "path": _rel(path)})
    else:
        path.write_text(updated, encoding="utf-8")
        LOG.append({"action": "rewrite", "path": _rel(path)})
    return True


def scan_roots() -> list[Path]:
    return [
        ROOT / "index.html",
        ROOT / "frontend" / "index.html",
        ROOT / "frontend" / "pages",
        ROOT / "frontend" / "js",
        ROOT / "frontend" / "css",
        ROOT / "backend" / "legacy-django" / "templates",
        ROOT / "backend" / "legacy-django" / "jobs" / "templates",
        ROOT / "backend" / "legacy-django" / "jobs",
        ROOT / "backend" / "legacy-django" / "config",
        ROOT / "tools" / "build_static.py",
    ]


def ensure_readme_stubs(*, dry_run: bool) -> None:
    for folder in [
        CSS / "layouts",
        JS / "components",
        JS / "dashboards",
        JS / "notifications",
    ]:
        readme = folder / "README.md"
        if readme.exists():
            continue
        if dry_run:
            LOG.append({"action": "readme-planned", "path": _rel(readme)})
            continue
        folder.mkdir(parents=True, exist_ok=True)
        readme.write_text(
            f"# {folder.name}\n\nReserved for TalentBridgeAI {folder.parent.name} organization.\n",
            encoding="utf-8",
        )
        LOG.append({"action": "readme", "path": _rel(readme)})


def write_backup_inventory(stamp: str) -> Path:
    backup_dir = ROOT / "backups" / f"css_js_organize_{stamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        f"TalentBridgeAI CSS/JS organize inventory",
        f"Created: {datetime.now(timezone.utc).isoformat()}",
        f"ProjectRoot: {ROOT}",
        "Note: hash inventory only; files are not copied here.",
        "",
    ]
    for base in (CSS, JS):
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            lines.append(f"{_rel(path)} | {path.stat().st_size} | {_sha256(path)}")
    out = backup_dir / "INVENTORY.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    LOG.append({"action": "backup-inventory", "path": _rel(out)})
    return backup_dir


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Perform moves/rewrites. Default is dry-run only.",
    )
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Do not treat missing source+destination pairs as errors.",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=None,
        help="Optional log output path (JSON).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    dry_run = not args.apply
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    LOG.clear()
    css_targets.clear()
    js_targets.clear()

    LOG.append({"action": "mode", "dry_run": dry_run, "allow_missing": args.allow_missing})
    if args.apply:
        write_backup_inventory(stamp)

    errors = 0
    errors += move_group(CSS, CSS_MAP, css_targets, dry_run=dry_run, allow_missing=args.allow_missing)
    errors += move_group(JS, JS_MAP, js_targets, dry_run=dry_run, allow_missing=args.allow_missing)
    ensure_readme_stubs(dry_run=dry_run)

    for root in scan_roots():
        if root.is_file():
            rewrite_file(root, dry_run=dry_run)
        elif root.is_dir():
            for path in root.rglob("*"):
                if path.suffix.lower() in {".html", ".js", ".css", ".md", ".py"}:
                    # Avoid rewriting this organizer itself mid-run via jobs/tools noise:
                    if path.name.startswith("_organize_"):
                        continue
                    rewrite_file(path, dry_run=dry_run)

    default_log = (
        ROOT
        / "backups"
        / ("css_js_organize_dryrun_" + stamp if dry_run else f"css_js_organize_{stamp}")
        / "css_js_move_log.json"
    )
    out = args.log or default_log
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "dry_run": dry_run,
        "css_targets": css_targets,
        "js_targets": js_targets,
        "errors": errors,
        "log": LOG,
    }
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"mode={'dry-run' if dry_run else 'apply'}")
    print(f"CSS targets: {len(css_targets)}")
    print(f"JS targets: {len(js_targets)}")
    print(f"errors: {errors}")
    print(f"LOG={out}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
