# TalentBridgeAI scripts

All operational scripts live here (not in the project root).

| Folder | Purpose |
| --- | --- |
| `install/` | Install, first-run, superuser, Google OAuth connect |
| `startup/` | Start / restart / open site / enable auto-start |
| `shutdown/` | Stop server / disable auto-start |
| `maintenance/` | Repair, update, permanent fixes |
| `backup/` | Backup and portable release |
| `diagnostics/` | Status checks and diagnose |

Start the site:

```bat
scripts\startup\START_TALENTBRIDGEAI.bat
```

Stop:

```bat
scripts\shutdown\STOP_TALENTBRIDGEAI.bat
```

Django project path: `backend\legacy-django\`
