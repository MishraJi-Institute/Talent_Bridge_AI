from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.urls import reverse

import requests

from jobs.google_oauth import google_oauth_callback_url, sync_google_social_app


class Command(BaseCommand):
    help = "Verify .env Google OAuth (no secrets printed) and sync the SocialApp row."

    def handle(self, *args, **options):
        client_id = (settings.GOOGLE_OAUTH_CLIENT_ID or "").strip()
        client_secret = (settings.GOOGLE_OAUTH_CLIENT_SECRET or "").strip()

        self.stdout.write(f"Project .env path: {settings.PROJECT_ROOT / '.env'}")
        self.stdout.write(f"Google OAuth Client ID loaded: {'yes' if client_id else 'no'}")
        self.stdout.write(
            f"Google OAuth Client Secret loaded: {'yes' if client_secret else 'no'}"
        )
        if not client_id or not client_secret:
            missing = []
            if not client_id:
                missing.append("GOOGLE_OAUTH_CLIENT_ID")
            if not client_secret:
                missing.append("GOOGLE_OAUTH_CLIENT_SECRET")
            raise CommandError(
                "Google OAuth is disabled until both values are present in the private "
                f"project-root .env. Missing: {', '.join(missing)}."
            )

        if not client_id.endswith(".apps.googleusercontent.com"):
            self.stdout.write(
                self.style.SUCCESS("Google OAuth configuration is loaded by Django.")
            )
            return

        sync_google_social_app()
        self.stdout.write("Google SocialApp synchronized from .env.")

        redirect_uri = google_oauth_callback_url()
        expected_path = reverse("google_callback")
        if not redirect_uri.endswith(expected_path):
            self.stdout.write(
                self.style.WARNING(f"Callback URL {redirect_uri!r} (expected path {expected_path}).")
            )

        resp = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "grant_type": "authorization_code",
                "code": "talentbridge-oauth-health-check",
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
            },
            timeout=20,
        )
        try:
            error = (resp.json() or {}).get("error", "")
        except ValueError:
            error = "non_json_response"

        if error in {"invalid_client", "deleted_client", "invalid_client_id"}:
            raise CommandError(
                f"Google rejected OAuth credentials ({error}). "
                "In Cloud Console use an active Web client: copy Client ID + Client secret "
                "into .env, set redirect URI to "
                f"{redirect_uri!r}, then run RESTART_TALENTBRIDGEAI.bat."
            )
        if error == "invalid_grant":
            self.stdout.write(
                self.style.SUCCESS(
                    "Google accepts this Client ID + secret (probe code expected invalid_grant)."
                )
            )
            return

        raise CommandError(
            f"Unexpected Google token response (HTTP {resp.status_code}, error={error!r})."
        )