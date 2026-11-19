from django.core.management.base import BaseCommand

from jobs.google_oauth import google_oauth_configured, sync_google_social_app


class Command(BaseCommand):
    help = "Synchronize the configured Google OAuth app with this site's allauth record."

    def handle(self, *args, **options):
        if not google_oauth_configured():
            self.stdout.write("Google OAuth is not configured; no database changes were made.")
            return

        result = sync_google_social_app()
        if result is None:
            self.stdout.write("Google OAuth is provided through allauth settings; no database changes were needed.")
            return

        self.stdout.write(
            "Google OAuth app synchronized "
            f"for site id {result['site_id']} "
            f"(created={result['created']}, merged duplicates={result['merged']})."
        )
