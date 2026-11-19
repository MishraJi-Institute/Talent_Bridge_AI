# TalentBridgeAI local ports

## Problem this solves

Bookmarks and older docs often open `http://127.0.0.1:8000/…`. The managed Django server may listen on **8001** when 8000 was busy once. Opening the wrong port showed Firefox “Unable to connect”.

## Permanent behavior

`tools/windows_manager.py` now:

1. Prefers port **8000** on a fresh start when it is free.
2. Keeps a running managed server on whatever port it already owns (often 8001).
3. Starts `tools/talentbridge_port_bridge.py` on the unused alias port so **both** work:

| You open | What happens |
| --- | --- |
| `http://127.0.0.1:8000/` | Site or auto-redirect to live Django |
| `http://127.0.0.1:8001/` | Site or auto-redirect to live Django |

## Correct login URL

Use:

- `http://127.0.0.1:8000/login/`
- or `http://127.0.0.1:8001/login/`

`/pages/login.html` also works once the server is up, but `/login/` is the canonical route.

## Commands

```bat
scripts\startup\START_TALENTBRIDGEAI.bat
scripts\startup\OPEN_TALENTBRIDGE.bat
python tools\windows_manager.py status
python tools\windows_manager.py bridge
```
