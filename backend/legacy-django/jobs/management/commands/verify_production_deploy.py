"""Fail Render/CI build unless this checkout is the real TalentBridge Django app."""
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.urls import reverse


class Command(BaseCommand):
    help = "Verify production deploy has TalentBridge routes and safe DEBUG settings."

    def handle(self, *args, **options):
        try:
            google = reverse("social-login-start", kwargs={"provider": "google"})
            login = reverse("login")
        except Exception as exc:
            raise CommandError(
                "Wrong Django project on this host (missing TalentBridge auth routes). "
                "Connect Render service to MishraJi-Institute/Talent_Bridge_AI and redeploy."
            ) from exc
        if google != "/auth/social/google/":
            raise CommandError(f"Unexpected Google OAuth path: {google}")
        if login != "/login/":
            raise CommandError(f"Unexpected login path: {login}")
        env = getattr(settings, "DJANGO_ENV", "production")
        if env not in {"production", "staging"} and settings.DEBUG:
            raise CommandError("DEBUG must be off for production deploy (set DJANGO_ENV=production).")
        self.stdout.write(self.style.SUCCESS("VERIFY_PRODUCTION_DEPLOY OK: TalentBridgeAI routes present."))