# Persistent Django startup fix

The screenshot's `Unable to connect` message means no process was listening on
127.0.0.1:8000 at the time. A browser refresh cannot start Django.

Run `FIX_SERVER_PERMANENTLY.bat` once on Windows. It registers a logon scheduled
task and starts the existing managed Django launcher hidden. It waits up to
90 seconds for HTTP 200 before reporting success. The existing launcher continues
to run dependency checks, Django checks, database connectivity checks and
non-destructive migrations; it does not reset users or replace the database.

Use `CHECK_DJANGO_SERVER.bat` to inspect status. Use
`DISABLE_AUTO_SERVER_STARTUP.bat` to remove the scheduled task.

Limits: this keeps the local server available after Windows sign-in while the
computer is on and awake. It is not cloud hosting and cannot serve the site when
the PC is off/asleep. Keep this project folder at the same path after setup.
