"""Light rate limiting for the public contact form."""
from __future__ import annotations

from django.core.cache import cache

from .login_protection import client_ip

_WINDOW = 3600
_MAX_PER_HOUR = 8


def contact_blocked_message(request) -> str | None:
    key = f"tb:contact:ip:{client_ip(request)}"
    if cache.get(key, 0) >= _MAX_PER_HOUR:
        return "Too many messages were submitted recently. Please try again later."
    return None


def record_contact_submission(request) -> None:
    key = f"tb:contact:ip:{client_ip(request)}"
    cache.add(key, 0, _WINDOW)
    cache.incr(key)