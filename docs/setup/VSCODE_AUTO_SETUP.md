# VS Code automatic setup

1. Extract this ZIP to a permanent writable folder.
2. Open the **TalentBridgeAI** folder in VS Code, or open `TalentBridgeAI.code-workspace`.
3. If VS Code asks whether to allow automatic tasks for this folder, choose **Allow**.
   VS Code requires this one-time trust confirmation for security.
4. The task `TalentBridgeAI: auto-start Django` runs when the folder opens. It starts the
   managed server in the background, waits up to 120 seconds for HTTP 200 from
   `http://127.0.0.1:8000/`, and opens the browser after the health check passes.
5. Keep the project folder at the same path. The task runs on later VS Code opens after
   automatic tasks have been allowed.

If startup fails, inspect `logs/setup.log` and `logs/server.log`, or run
`FIX_TALENTBRIDGEAI_SERVER_NOW.bat` from the project root.

The setup does not reset the SQLite database, delete users, or replace `.env`.
The local server is available only while the computer is on and awake.
