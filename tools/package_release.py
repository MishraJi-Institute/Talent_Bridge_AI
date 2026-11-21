#!/usr/bin/env python3
"""Create protected local backups and verified, data-free portable releases."""

from __future__ import annotations

import argparse
import compileall
import os
import secrets
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKUP_DIR = ROOT / "backups" / "protected"
RELEASE_DIR = ROOT / "releases"

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "staticfiles",
    "private_media",
    "media",
    "uploads",
    "logs",
    "backups",
    "releases",
    "site",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".sqlite", ".sqlite3", ".db", ".log"}
REQUIRED_RELEASE_FILES = {
    ".env.example",
    ".vscode/tasks.json",
    "START_TALENTBRIDGEAI.bat",
    "legacy-django/manage.py",
    "legacy-django/requirements.txt",
    "legacy-django/jobs/migrations/__init__.py",
    "tools/windows_manager.py",
}


def relative_name(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def is_excluded(path: Path, *, include_private: bool) -> bool:
    parts = path.relative_to(ROOT).parts
    dirs = EXCLUDED_DIRS - ({"private_media", "media", "uploads"} if include_private else set())
    if any(part in dirs for part in parts[:-1]):
        return True
    name = path.name.lower()
    suffix = path.suffix.lower()
    if suffix in EXCLUDED_SUFFIXES and (not include_private or suffix not in {".sqlite", ".sqlite3", ".db"}):
        return True
    if name == ".django_secret_key" and not include_private:
        return True
    if name in {".talentbridge_django.pid", ".talentbridge_django.lock"}:
        return True
    if name.startswith(".talentbridge_") or name.endswith(".partial"):
        return True
    if name == ".env" or (name.startswith(".env.") and name != ".env.example"):
        return not include_private
    return False


def source_files(*, include_private: bool) -> list[Path]:
    result = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.is_symlink() or is_excluded(path, include_private=include_private):
            continue
        result.append(path)
    return sorted(result, key=relative_name)


def unique_archive_path(directory: Path, base_name: str) -> Path:
    candidate = directory / base_name
    suffix = 1
    while candidate.exists():
        candidate = directory / (Path(base_name).stem + f"_{suffix:02d}" + Path(base_name).suffix)
        suffix += 1
    return candidate


def write_verified_archive(
    destination: Path,
    files: list[Path],
    *,
    extra_text: tuple[str, str] | None = None,
) -> int:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=".talentbridge-",
            suffix=".partial",
            dir=destination.parent,
            delete=False,
        ) as temp:
            temp_path = Path(temp.name)
        with zipfile.ZipFile(temp_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for path in files:
                archive.write(path, relative_name(path))
            if extra_text:
                archive.writestr(extra_text[0], extra_text[1])
        with zipfile.ZipFile(temp_path, "r") as archive:
            corrupt_member = archive.testzip()
            if corrupt_member:
                raise RuntimeError(f"Archive integrity check failed at {corrupt_member}.")
            if len(archive.namelist()) < 2:
                raise RuntimeError("Archive verification failed: archive is unexpectedly empty.")
        try:
            os.link(temp_path, destination)
        except FileExistsError:
            raise FileExistsError(f"Refusing to overwrite an existing archive: {destination}")
        temp_path.unlink()
        temp_path = None
        return len(files)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


def create_backup() -> Path:
    files = source_files(include_private=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destination = unique_archive_path(BACKUP_DIR, f"TalentBridgeAI_PROTECTED_BACKUP_{stamp}.zip")
    warning = (
        "BACKUP CONTENTS: This archive includes the local .env, database files, "
        "and private media when present. It is NOT encrypted. Keep it on access-"
        "controlled storage and do not email or distribute it. Never extract it "
        "over a newer project without first reviewing its contents.\n"
    )
    count = write_verified_archive(
        destination,
        files,
        extra_text=("BACKUP_SCOPE.txt", warning),
    )
    print(f"Protected local backup created and verified: {destination}")
    print(f"Project files archived: {count}; ZIP CRC test: passed.")
    print("WARNING: This backup may contain credentials and personal data; the ZIP is not encrypted.")
    return destination


def validate_example_env(path: Path) -> None:
    if not path.is_file():
        raise RuntimeError("Release is missing the safe .env.example template.")
    sensitive_names = ("SECRET", "PASSWORD", "TOKEN", "API_KEY", "CLIENT_ID")
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = (part.strip() for part in line.split("=", 1))
        value = value.strip("\"'")
        if any(marker in key.upper() for marker in sensitive_names) and value:
            raise RuntimeError(f".env.example must not contain a value for sensitive variable {key}.")


def verify_release_archive(archive_path: Path) -> None:
    with zipfile.ZipFile(archive_path, "r") as archive:
        corrupt_member = archive.testzip()
        if corrupt_member:
            raise RuntimeError(f"Release ZIP is corrupt at {corrupt_member}.")
        names = set(archive.namelist())
        missing = REQUIRED_RELEASE_FILES - names
        if missing:
            raise RuntimeError("Release is missing required files: " + ", ".join(sorted(missing)))
        for name in names:
            member = Path(name)
            if member.is_absolute() or ".." in member.parts:
                raise RuntimeError(f"Unsafe archive path detected: {name}")
            if is_excluded(ROOT / Path(*member.parts), include_private=False):
                raise RuntimeError(f"Private or generated path included in release: {name}")
        migrations = [
            name for name in names
            if name.startswith("legacy-django/jobs/migrations/") and name.endswith(".py")
        ]
        if not migrations:
            raise RuntimeError("Release archive does not contain Django migrations.")


def test_extracted_copy(archive_path: Path, python_executable: str) -> None:
    with tempfile.TemporaryDirectory(prefix="TalentBridgeAI_release_verify_") as temp_dir:
        extract_root = Path(temp_dir) / "TalentBridgeAI"
        extract_root.mkdir()
        with zipfile.ZipFile(archive_path, "r") as archive:
            archive.extractall(extract_root)
        missing = [name for name in REQUIRED_RELEASE_FILES if not (extract_root / name).is_file()]
        if missing:
            raise RuntimeError("Extracted release is missing required files: " + ", ".join(sorted(missing)))
        if not compileall.compile_dir(str(extract_root), quiet=1, force=True):
            raise RuntimeError("Python compilation check failed for the extracted release.")
        env = os.environ.copy()
        env.update({
            "DJANGO_ENV": "development",
            "DJANGO_DEBUG": "true",
            "DJANGO_SECRET_KEY": secrets.token_urlsafe(48),
            "DJANGO_ALLOWED_HOSTS": "localhost,127.0.0.1,[::1]",
            "DB_ENGINE": "sqlite",
            "DB_NAME": "release_verification_never_migrated",
            "PYTHONDONTWRITEBYTECODE": "1",
        })
        check = subprocess.run(
            [python_executable, "manage.py", "check"],
            cwd=extract_root / "legacy-django",
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if check.returncode:
            raise RuntimeError("Extracted-copy Django check failed:\n" + check.stdout.strip())
        print("Extraction test: passed in a temporary directory.")
        print("Extracted-copy Python compilation and Django system check: passed.")


def create_release(python_executable: str) -> Path:
    files = source_files(include_private=False)
    if not files:
        raise RuntimeError("No project source files were found for the release.")
    validate_example_env(ROOT / ".env.example")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destination = unique_archive_path(RELEASE_DIR, f"TalentBridgeAI_Portable_{stamp}.zip")
    count = write_verified_archive(destination, files)
    try:
        verify_release_archive(destination)
        test_extracted_copy(destination, python_executable)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    print(f"Portable ZIP created: {destination}")
    print(f"Files archived: {count}; ZIP CRC test: passed; required files: present.")
    print("Excluded: .env/secrets, databases, private media/uploads, backups, logs, venvs, caches, bytecode, generated site/staticfiles.")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("backup", "release"))
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python executable used for the extracted-copy Django check (defaults to this interpreter).",
    )
    args = parser.parse_args()
    try:
        if args.action == "backup":
            create_backup()
        else:
            create_release(args.python)
    except (OSError, RuntimeError, zipfile.BadZipFile, subprocess.SubprocessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
