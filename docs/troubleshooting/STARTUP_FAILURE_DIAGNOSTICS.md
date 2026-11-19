# TalentBridgeAI startup failure diagnostics

If Firefox reports `Unable to connect` for `127.0.0.1:8000`, the Django server is not reachable. Refreshing the page or opening the port-5500 static preview does not start Django.

1. Run `START_TALENTBRIDGEAI.bat` and keep the terminal open.
2. If startup fails, the launcher now pauses so its error remains visible.
3. Run `DIAGNOSE_TALENTBRIDGEAI.bat`.
4. Share `logs/diagnostic_report.txt` after checking it contains no private values. The diagnostic intentionally does not read or print `.env` contents.

The diagnostic reports Python/virtual-environment availability, database file presence, port status, and the tails of local setup/server logs. It does not modify the database, credentials, or project configuration.
