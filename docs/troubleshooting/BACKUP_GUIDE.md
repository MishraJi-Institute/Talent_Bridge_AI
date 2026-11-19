# TalentBridgeAI backup guide

## Create a manual backup

Before an important update, database change, or release build, run from the project root:

```powershell
py tools\package_release.py backup
```

The script creates a timestamped ZIP under `backups\protected\`. It verifies the
archive with Python's ZIP CRC check before publishing it. Existing archives are
never overwritten; a numeric suffix is added if two backups are created in the
same second. A failed/incomplete temporary archive is not published as a
successful backup.

The protected backup includes the current source, `.env`, `.django_secret_key`,
SQLite databases, and private upload directories when present. It omits
re-creatable virtual environments, caches, generated `staticfiles`/`site`,
logs, and previous backup archives. Non-SQLite database servers must be backed
up separately using the configured database provider's approved backup method.

## Protect and restore

The backup ZIP is **not encrypted** and may contain OAuth credentials, signing
keys, user records, and private resumes. Keep it on access-controlled storage;
use an encrypted volume (for example BitLocker) for sensitive or off-device
storage. Do not email it or include it in a distributable ZIP.

To restore, stop TalentBridgeAI, create a fresh backup of the current folder,
and extract the protected ZIP into a separate temporary directory first.
Review its contents. Restore only the needed files (`.env`, key, database, or
uploads) into the intended project, preserving newer files unless a deliberate
rollback is required. Never extract the archive over an active project without
review. Start with `START_TALENTBRIDGEAI.bat`; the launcher checks the database
and applies only pending migrations.

For SQLite-only recovery details, also see
[docs/guides/DATABASE_BACKUP_AND_RECOVERY.md](docs/guides/DATABASE_BACKUP_AND_RECOVERY.md).
