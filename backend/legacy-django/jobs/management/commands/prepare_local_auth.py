"""Prepare local site and Google OAuth records without printing secrets."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.urls import reverse

from jobs.google_oauth import google_oauth_configured, sync_google_social_app


LOCAL_DOMAIN = "127.0.0.1:8000"
EXPECTED_CALLBACK = "/accounts/google/login/callback/"


class Command(BaseCommand):
    help = (
        "Point the local Django site at 127.0.0.1:8000 when it still uses a "
        "placeholder domain, then synchronize the Google provider if configured."
    )

    def handle(self, *args, **options):
        callback = reverse("google_callback")
        if callback != EXPECTED_CALLBACK:
            raise CommandError(
                f"Google callback route is {callback}, expected {EXPECTED_CALLBACK}."
            )

        site, created = Site.objects.get_or_create(
            pk=settings.SITE_ID,
            defaults={"domain": LOCAL_DOMAIN, "name": "TalentBridge AI"},
        )
        # Always pin local Site.domain to the Google Console host (:8000), even
        # when Django itself is temporarily listening on :8001 behind the bridge.
        if created or site.domain != LOCAL_DOMAIN or site.name != "TalentBridge AI":
            site.domain = LOCAL_DOMAIN
            site.name = "TalentBridge AI"
            site.save(update_fields=("domain", "name"))
            site_state = "updated"
        else:
            site_state = "unchanged"
        Site.objects.clear_cache()

        oauth_loaded = google_oauth_configured()
        if oauth_loaded:
            result = sync_google_social_app()
            sync_state = (
                "settings"
                if result is None
                else f"database created={result['created']} merged={result['merged']}"
            )
        else:
            sync_state = "skipped"

        superuser_present = get_user_model().objects.filter(is_superuser=True).exists()
        self.stdout.write(f"Local site domain: {site.domain} ({site_state})")
        self.stdout.write(f"Google callback path: {callback}")
        self.stdout.write(f"Google OAuth loaded: {'yes' if oauth_loaded else 'no'}")
        self.stdout.write(f"Google provider sync: {sync_state}")
        self.stdout.write(f"Superuser present: {'yes' if superuser_present else 'no'}")
        self.stdout.write("No passwords or OAuth secrets were printed. No user account was modified.")
