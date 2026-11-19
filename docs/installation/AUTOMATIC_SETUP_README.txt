TalentBridgeAI - Integrated VS Code Automatic Setup

This archive already contains ONE integrated TalentBridgeAI/.vscode folder.
Do not copy a second .vscode folder into the project.

INSTALL:
1. Extract this ZIP.
2. Open the extracted TalentBridgeAI folder in VS Code (File > Open Folder).
3. If VS Code asks whether to allow automatic tasks, choose Allow.
4. If VS Code asks Workspace Trust, choose Trust this folder.
5. Reload window once (Ctrl+Shift+P > Developer: Reload Window).

The integrated .vscode/settings.json enables task.allowAutomaticTasks.
The integrated .vscode/tasks.json contains the folder-open Django startup task.
The startup scripts and server helper files are included in the project.

NOTE:
Automatic startup requires Windows PowerShell and the project's expected Django environment/dependencies.
This ZIP has not been live-tested on your Windows machine. If startup fails, use the included
START_TALENTBRIDGEAI.bat / diagnostic files and share the exact error text.


LOGIN + AUTO-START REPAIR (2026-11)
- Email/password authentication now resolves duplicate email records by the supplied password;
  it never silently picks the first duplicate account.
- Django username/password login remains enabled for admin/superusers.
- Every server start/restart checks Django, database connectivity, migrations (backing up
  SQLite before applying pending migrations), static collection, admin/login routes, and
  admin CSS. Read-only staff/superuser password-usability audit is logged.
- INSTALL_TALENTBRIDGEAI.bat installs checks, registers a hidden Windows sign-in startup
  entry for the current user, then starts the server.
- No passwords are created or reset automatically. Use Django's changepassword command
  for accounts that do not have a usable password.
- Keep the existing .env, database/, and private_media/ when applying this update.
