"""Google OAuth configuration and database synchronization helpers."""

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import transaction
from django.urls import reverse

from allauth.socialaccount.models import SocialApp, SocialToken

# Local Google Cloud Console redirect URIs are registered against this host.
DEFAULT_GOOGLE_OAUTH_PUBLIC_HOST = "127.0.0.1:8000"


def google_settings_apps():
    """Return explicitly configured allauth apps, or None for env/database setup."""
    provider_config = settings.SOCIALACCOUNT_PROVIDERS.get("google", {})
    if "APPS" in provider_config:
        return provider_config.get("APPS") or []
    if provider_config.get("APP") is not None:
        return [provider_config["APP"]]
    return None


def google_oauth_configured():
    apps = google_settings_apps()
    if apps is not None:
        return any(app.get("client_id") and app.get("secret") for app in apps)
    return bool(settings.GOOGLE_OAUTH_CLIENT_ID and settings.GOOGLE_OAUTH_CLIENT_SECRET)


def _site_domain(request=None) -> str:
    try:
        return (Site.objects.get_current(request).domain or "").strip()
    except Exception:
        return ""


def _is_local_oauth_site_domain(domain: str) -> bool:
    value = (domain or "").lower()
    return value.startswith("127.0.0.1:") or value.startswith("localhost:")


def google_oauth_public_origin(request=None):
    """Origin Google must redirect back to (matches Cloud Console + Site.domain)."""
    configured = getattr(settings, "GOOGLE_OAUTH_REDIRECT_ORIGIN", "").strip().rstrip("/")
    if configured:
        return configured

    domain = _site_domain(request) or DEFAULT_GOOGLE_OAUTH_PUBLIC_HOST
    if request is not None:
        scheme = "https" if request.is_secure() else "http"
    elif domain.lower().startswith(("127.0.0.1", "localhost")):
        scheme = "http"
    else:
        scheme = "https"
    return f"{scheme}://{domain}"


def google_oauth_callback_url(request=None):
    """Callback absolute URL. Local dual-port installs always use Site.domain (:8000)."""
    from allauth.utils import build_absolute_uri

    path = reverse("google_callback")
    domain = _site_domain(request)
    if _is_local_oauth_site_domain(domain):
        return f"{google_oauth_public_origin(request)}{path}"
    if request is not None:
        return build_absolute_uri(request, path)
    return f"{google_oauth_public_origin(request)}{path}"


def google_oauth_request_matches_public_host(request) -> bool:
    domain = _site_domain(request)
    if not _is_local_oauth_site_domain(domain):
        # Non-local / test hosts: never bounce the browser to 127.0.0.1:8000.
        return True
    return (request.get_host() or "").lower() == domain.lower()


def ensure_google_oauth_callback_patch():
    """Force allauth Google callbacks onto the public Site origin for local dual-port."""
    from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter

    if getattr(GoogleOAuth2Adapter, "_talentbridge_callback_patched", False):
        return

    def get_callback_url(self, request, app):
        return google_oauth_callback_url(request)

    GoogleOAuth2Adapter.get_callback_url = get_callback_url
    GoogleOAuth2Adapter._talentbridge_callback_patched = True


def google_apps_from_settings(client_id=None):
    """Build Google SocialApp objects for allauth settings-backed credentials."""
    apps = google_settings_apps()
    if apps is None:
        return []

    result = []
    for config in apps:
        if client_id and config.get("client_id") != client_id:
            continue
        app = SocialApp(provider="google")
        for field in ("name", "provider_id", "client_id", "secret", "key", "settings"):
            if field in config:
                setattr(app, field, config[field])
        if app.client_id and app.secret:
            result.append(app)
    return result


def sync_google_social_app():
    """Ensure this deployment has one Google app associated with SITE_ID.

    Duplicate Google app rows are consolidated into one row. Existing site links
    and social tokens are preserved, including tokens that cannot be moved
    because the canonical app already has a token for the same account.
    """
    if google_settings_apps() is not None:
        # Settings-backed apps are handled directly by the social adapter.
        return {"created": False, "merged": 0, "site_id": settings.SITE_ID}

    client_id = settings.GOOGLE_OAUTH_CLIENT_ID
    secret = settings.GOOGLE_OAUTH_CLIENT_SECRET
    if not client_id or not secret:
        return {"created": False, "merged": 0, "site_id": settings.SITE_ID}

    with transaction.atomic():
        try:
            site = Site.objects.select_for_update().get(pk=settings.SITE_ID)
        except Site.DoesNotExist:
            site = Site.objects.create(
                pk=settings.SITE_ID,
                domain="localhost",
                name="TalentBridge AI",
            )

        apps = list(
            SocialApp.objects.select_for_update()
            .filter(provider="google")
            .order_by("pk")
        )
        matching = [app for app in apps if app.client_id == client_id]
        canonical = (matching or apps or [None])[0]
        created = canonical is None
        if created:
            canonical = SocialApp(provider="google", name="Google")

        site_ids = {site.pk}
        for app in apps:
            site_ids.update(app.sites.values_list("pk", flat=True))

        merged = 0
        for duplicate in apps:
            if duplicate.pk == canonical.pk:
                continue
            tokens = SocialToken.objects.select_for_update().filter(app=duplicate)
            for token in tokens:
                already_linked = SocialToken.objects.filter(
                    app=canonical,
                    account_id=token.account_id,
                ).exists()
                token.app = None if already_linked else canonical
                token.save(update_fields=("app",))
            duplicate.delete()
            merged += 1

        canonical.provider = "google"
        canonical.provider_id = ""
        canonical.name = "Google"
        canonical.client_id = client_id
        canonical.secret = secret
        canonical.save()
        canonical.sites.set(site_ids)

    return {"created": created, "merged": merged, "site_id": site.pk}
