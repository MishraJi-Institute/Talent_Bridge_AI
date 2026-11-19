from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Check that Django loaded both Google OAuth credentials without displaying them."

    def handle(self, *args, **options):
        client_id_present = bool(settings.GOOGLE_OAUTH_CLIENT_ID)
        client_secret_present = bool(settings.GOOGLE_OAUTH_CLIENT_SECRET)

        self.stdout.write(f"Project .env path: {settings.PROJECT_ROOT / '.env'}")
        self.stdout.write(f"Google OAuth Client ID loaded: {'yes' if client_id_present else 'no'}")
        self.stdout.write(
            f"Google OAuth Client Secret loaded: {'yes' if client_secret_present else 'no'}"
        )

        if not client_id_present or not client_secret_present:
            missing = []
            if not client_id_present:
                missing.append("GOOGLE_OAUTH_CLIENT_ID")
            if not client_secret_present:
                missing.append("GOOGLE_OAUTH_CLIENT_SECRET")
            raise CommandError(
                "Google OAuth is disabled until both values are present in the private "
                f"project-root .env. Missing: {', '.join(missing)}. "
                "The main website can continue using email/password authentication."
            )

        self.stdout.write(self.style.SUCCESS("Google OAuth configuration is loaded by Django."))
