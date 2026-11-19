# Database Backup and Recovery

## What is in the delivery ZIP
- `database/TalentBridgeAI.sqlite3` is copied from the latest uploaded archive.
- Existing user, profile and social-account identity rows are retained.
- The distributable copy has stored Google OAuth client ID/secret/key/settings cleared and Django session rows removed. This prevents old OAuth secrets and browser sessions from travelling with the project.
- At inspection the source DB contained 3 user rows, 3 profile rows and 3 social-account identity rows. No password was reset or rewritten.

## What is intentionally not bundled
- `.env` and `.django_secret_key` (private configuration/signing material).
- `private_media/` (may contain private resumes and other user documents).
- `backups/`, logs, virtual environments and caches.

The original uploaded ZIP is unchanged. Keep it as the source archive and retain a separate private backup of `private_media/` on your own machine if you need to preserve uploaded resumes.

## Before switching your local project
1. Stop the old Django process.
2. Keep a copy of the current local `database/TalentBridgeAI.sqlite3`.
3. Keep the current `.env` privately; do not upload it or put it in chat.
4. If you have private resume uploads, keep a private copy of `private_media/`.

## Restoring the delivered database
1. Extract the project ZIP into a new folder.
2. Copy your private `.env` into the project root, or let `START_TALENTBRIDGEAI.bat` create one from `.env.example`.
3. If using the DB supplied in the ZIP, leave `DB_ENGINE=sqlite` and `DB_NAME=TalentBridgeAI`.
4. If you have newer local records than the uploaded archive, use your newer private DB backup instead of overwriting it with the bundled DB.
5. Start the project using `START_TALENTBRIDGEAI.bat`. The launcher checks the DB, backs it up before pending migrations, applies migrations and then checks the homepage/login/signup routes.

## Google OAuth
The database copy does not carry Google client credentials. Set `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` in your private root `.env`, then run `RESTART_TALENTBRIDGEAI.bat`. Never commit or share that file.
