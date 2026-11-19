# Portable ZIP release guide

## Build a release

From the project root, first create a protected backup:

```powershell
py tools\package_release.py backup
```

Then build and verify the data-free portable release. Use the existing project
environment so the extracted-copy Django system check has the required
packages:

```powershell
legacy-django\.venv\Scripts\python.exe tools\package_release.py release --python legacy-django\.venv\Scripts\python.exe
```

The ZIP is written to `releases\TalentBridgeAI_Portable_<timestamp>.zip`.
Python's built-in `zipfile` library is used; no paid archiver is needed.
Existing releases are never overwritten.

## Automatic verification

The release builder:

1. Omits secrets, databases, private uploads/media, backups, logs, virtual
   environments, bytecode, caches, generated `site`, and `staticfiles`.
2. Requires the startup script, requirements, migrations, VS Code task config,
   source manager, and safe `.env.example`.
3. Runs `ZipFile.testzip()`.
4. Extracts to a temporary directory, compiles Python files, and runs Django's
   system check against that extracted copy. It does not migrate or access the
   live database.

The temporary extraction directory is removed after verification. If release
verification fails, the incomplete release ZIP is removed and the command
returns an error.

For manual verification:

```powershell
py -c "import sys,zipfile; z=zipfile.ZipFile(sys.argv[1]); print(z.testzip() or 'ZIP integrity OK')" "releases\TalentBridgeAI_Portable_<timestamp>.zip"
```

Extract and install-test in a separate empty folder as described in
[PORTABLE_INSTALLATION_GUIDE.md](PORTABLE_INSTALLATION_GUIDE.md). Never add a
live `.env`, database, or user upload to the distributable archive.
