TalentBridgeAI new ZIP / folder-open automation

- VS Code folder-open task invokes .vscode/start-talentbridge.ps1.
- The task runs the managed launcher, which imports .env, SQLite DB and missing user media from the previous active checkout on the same Windows account.
- The last active project path is saved outside the ZIP at %LOCALAPPDATA%\TalentBridgeAI\active_project.txt.
- If no saved path exists, it also checks the prior path supplied in the project setup notes: E:\Job Folder 16 Nov 2026 2 pm\TalentBridgeAI.
- Existing destination .env/database files are backed up before importing the previous checkout. User media is merged without deleting destination files.
- The manager recreates a non-portable .venv, installs requirements, checks/migrates the database with a backup before pending migrations, collects static files, audits admin accounts and starts/checks the server.
- Extract the ZIP first, then open the extracted folder in VS Code. VS Code Workspace Trust / folder-open task permission is required.
- See PERMANENT_FIRST_OPEN_SETUP_HI.txt for limitations and one-time credentials setup.
