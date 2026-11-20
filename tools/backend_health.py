"""Check that a public Django origin is TalentBridgeAI (not a wrong Render app)."""
from __future__ import annotations

import json
import urllib.error
import urllib.request

APP_ID = "talentbridge-ai-legacy"
HEALTH_PATH = "/__deploy__/health/"


def origin_is_healthy(origin: str, *, timeout: float = 20.0) -> bool:
    base = (origin or "").strip().rstrip("/")
    if not base.startswith("https://"):
        return False
    url = base + HEALTH_PATH
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "TalentBridge-HealthCheck/1", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                return False
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError):
        return False
    return payload.get("app") == APP_ID