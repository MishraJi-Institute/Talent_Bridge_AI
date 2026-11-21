"""Keep the local Django superuser password in sync with .env (local dev only)."""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model


def sync_local_admin_password() -> dict:
    """
  Update the configured superuser password from LOCAL_ADMIN_BOOTSTRAP_PASSWORD.

  Returns a small status dict; never includes the password.
  """
    password = (getattr(settings, "LOCAL_ADMIN_BOOTSTRAP_PASSWORD", "") or "").strip()
    username = (getattr(settings, "LOCAL_ADMIN_USERNAME", "") or "").strip()

    if not password:
        return {"synced": False, "reason": "no_bootstrap_password"}

    user_model = get_user_model()
    if username:
        user = user_model._default_manager.filter(
            username__iexact=username, is_superuser=True
        ).first()
    else:
        user = user_model._default_manager.filter(is_superuser=True).order_by("pk").first()

    if user is None:
        return {"synced": False, "reason": "no_superuser"}

    user.set_password(password)
    user.is_active = True
    user.is_staff = True
    user.is_superuser = True
    user.save(update_fields=["password", "is_active", "is_staff", "is_superuser"])

    if not authenticate(username=user.username, password=password):
        return {"synced": False, "reason": "auth_check_failed", "username": user.username}

    return {"synced": True, "username": user.username}