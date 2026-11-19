from django.apps import AppConfig


class JobsConfig(AppConfig):
    name = 'jobs'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        # Patch Google OAuth callback URL onto the Site/public origin so
        # redirect_uri always matches Google Cloud Console (127.0.0.1:8000).
        from .google_oauth import ensure_google_oauth_callback_patch

        ensure_google_oauth_callback_patch()