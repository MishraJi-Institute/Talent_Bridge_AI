"""Login and public POST abuse protection using the default cache backend."""
from __future__ import annotations

from django.conf import settings
from django.core.cache import cache

_WINDOW = 900  # 15 minutes
_IP_MAX_ATTEMPTS = 25
_ACCOUNT_FAIL_MAX = 8
_LOCKOUT_SECONDS = 300  # 5 minutes after threshold


def _enabled() -> bool:
    return getattr(settings, "LOGIN_RATE_LIMIT_ENABLED", True)


def client_ip(request) -> str:
    forwarded = (request.META.get("HTTP_X_FORWARDED_FOR") or "").split(",")[0].strip()
    if forwarded:
        return forwarded[:64]
    return (request.META.get("REMOTE_ADDR") or "unknown")[:64]


def _ip_key(request) -> str:
    return f"tb:login:ip:{client_ip(request)}"


def _fail_key(email: str) -> str:
    return f"tb:login:fail:{email.strip().lower()[:254]}"


def _lock_key(email: str) -> str:
    return f"tb:login:lock:{email.strip().lower()[:254]}"


def login_blocked_message(request, email: str = "") -> str | None:
    if not _enabled():
        return None
    if cache.get(_lock_key(email)):
        return (
            "Too many failed sign-in attempts for this account. "
            "Please wait a few minutes and try again."
        )
    if cache.get(_ip_key(request), 0) >= _IP_MAX_ATTEMPTS:
        return (
            "Too many sign-in attempts from this network. "
            "Please wait before trying again."
        )
    return None


def record_failed_login(request, email: str = "") -> None:
    if not _enabled():
        return
    ip_key = _ip_key(request)
    cache.add(ip_key, 0, _WINDOW)
    cache.incr(ip_key)
    if email:
        fail_key = _fail_key(email)
        cache.add(fail_key, 0, _WINDOW)
        failures = cache.incr(fail_key)
        if failures >= _ACCOUNT_FAIL_MAX:
            cache.set(_lock_key(email), 1, _LOCKOUT_SECONDS)


def clear_login_attempts(request, email: str = "") -> None:
    if not _enabled():
        return
    cache.delete(_ip_key(request))
    if email:
        cache.delete(_fail_key(email))
        cache.delete(_lock_key(email))