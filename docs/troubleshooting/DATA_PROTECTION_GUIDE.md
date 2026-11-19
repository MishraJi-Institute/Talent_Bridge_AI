# TalentBridgeAI data protection

## What stays private

The distributable ZIP does not contain `.env`, OAuth credentials, signing keys,
database files, private resumes, uploads, media, backups, logs, or generated
runtime files. `.env.example` contains configuration names and blank or
non-secret placeholders only. Confirm that before publishing any release.

The separate protected backup intentionally includes private local settings,
databases, and private upload data so it can support recovery. It is not
encrypted by the backup script. Store it only on an access-controlled,
encrypted volume; do not upload, email, or distribute it.

## Safe update and migration

1. Stop the local server and create a protected backup.
2. Build or extract new source into a separate folder.
3. Never overwrite the original `.env`, database, resume files, or media with
   blank release files. A distributable ZIP has no database or upload folder.
4. For a database move, stop Django and back up both source and destination
   before copying. Keep the database name consistent with `.env`.
5. Copy private uploads only when they belong to the same database/account
   data set. Keep their access controls and storage paths private.
6. Start the new copy and review the reported checks. Migrations are additive
   project migrations; retain the backup until the new copy is verified.

## Access and credentials

Use unique passwords, keep `.env` out of source control and shared ZIPs, and
rotate OAuth/API credentials if they are ever exposed. Configure Google and
SMTP credentials only on the target machine. Do not include real personal
records in a demo/release database.
