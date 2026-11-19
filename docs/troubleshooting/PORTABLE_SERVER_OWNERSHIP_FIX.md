# Portable server ownership fix

This update tightens Django process identification.

- A running server is considered managed by this checkout only when its command line contains this checkout's exact `legacy-django/manage.py` path or its project virtual-environment path.
- The broad `talentbridgeai` substring match has been removed.
- The VS Code startup script will not terminate a Python/Django process on port 8000 unless its command line proves it belongs to this exact project folder.
- If another application owns port 8000, startup stops safely and explains the conflict instead of killing an unrelated process.

No database, user data, `.env`, OAuth credentials, or migrations were changed by this packaging edit.

Important: this ZIP has not been executed on the user's Windows PC. Django runtime/HTTP health and Google OAuth still require verification in that environment. Google OAuth requires real credentials from Google Cloud Console.
