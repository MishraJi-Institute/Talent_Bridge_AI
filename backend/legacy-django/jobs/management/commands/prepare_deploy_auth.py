"""Pin Site.domain and sync Google SocialApp for a deployed Django host."""

from urllib.parse import urlparse

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

from jobs.google_oauth import google_oauth_configured, sync_google_social_app


class Command(BaseCommand):
    help = (
        "Configure Sites + Google SocialApp for production using "
        "GOOGLE_OAUTH_REDIRECT_ORIGIN or RENDER_EXTERNAL_URL / RENDER_EXTERNAL_HOSTNAME."
    )

    def handle(self, *args, **options):
        origin = (getattr(settings, "GOOGLE_OAUTH_REDIRECT_ORIGIN", "") or "").strip().rstrip("/")
        if not origin:
            render_url = (os_environ_get("RENDER_EXTERNAL_URL") or "").strip().rstrip("/")
            host = (os_environ_get("RENDER_EXTERNAL_HOSTNAME") or "").strip()
            if render_url:
                origin = render_url
            elif host:
                origin = f"https://{host}"

        if not origin:
            self.stderr.write(
                "Set GOOGLE_OAUTH_REDIRECT_ORIGIN (e.g. https://your-app.onrender.com) "
                "before preparing deploy auth."
            )
            return

        parsed = urlparse(origin if "://" in origin else f"https://{origin}")
        domain = parsed.netloc or parsed.path
        if not domain:
            self.stderr.write(f"Could not parse deploy domain from {origin!r}")
            return

        site, created = Site.objects.get_or_create(
            pk=settings.SITE_ID,
            defaults={"domain": domain, "name": "TalentBridge AI"},
        )
        if created or site.domain != domain or site.name != "TalentBridge AI":
            site.domain = domain
            site.name = "TalentBridge AI"
            site.save(update_fields=("domain", "name"))
        Site.objects.clear_cache()
        self.stdout.write(f"Deploy site domain: {site.domain}")

        if google_oauth_configured():
            sync_google_social_app()
            self.stdout.write("Google SocialApp synchronized.")
        else:
            self.stdout.write("Google OAuth env not fully set; SocialApp sync skipped.")


def os_environ_get(name: str) -> str:
    import os

    return os.environ.get(name, "")
