"""Reset the local superuser password from .env or an interactive prompt."""

from getpass import getpass

import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from jobs.admin_sync import sync_local_admin_password


class Command(BaseCommand):
    help = (
        "Reset local superuser password. Uses LOCAL_ADMIN_BOOTSTRAP_PASSWORD from .env "
        "when set; otherwise prompts in the terminal."
    )

    def handle(self, *args, **options):
        password = (
            getattr(settings, "LOCAL_ADMIN_BOOTSTRAP_PASSWORD", "") or ""
        ).strip() or os.environ.get("LOCAL_ADMIN_BOOTSTRAP_PASSWORD", "").strip()

        if password:
            result = sync_local_admin_password()
            if not result.get("synced"):
                raise CommandError(
                    f"Could not sync admin password ({result.get('reason', 'unknown')})."
                )
            self.stdout.write(self.style.SUCCESS("Local admin password updated and verified."))
            self.stdout.write(f"Username: {result.get('username')}")
            self.stdout.write("Login: http://127.0.0.1:8000/admin/login/")
            return

        user_model = get_user_model()
        user = user_model._default_manager.filter(is_superuser=True).order_by("pk").first()
        if user is None:
            raise CommandError("No superuser found. Run CREATE_SUPERUSER.bat first.")

        self.stdout.write(f"Set password for superuser: {user.username}")
        password = getpass("New admin password: ")
        confirm = getpass("Confirm: ")
        if not password or password != confirm:
            raise CommandError("Password empty or mismatch.")

        os.environ["LOCAL_ADMIN_BOOTSTRAP_PASSWORD"] = password
        from django.conf import settings as django_settings

        django_settings.LOCAL_ADMIN_BOOTSTRAP_PASSWORD = password
        result = sync_local_admin_password()
        if not result.get("synced"):
            raise CommandError("Password save verification failed.")

        self.stdout.write(self.style.SUCCESS("Local admin password updated and verified."))
        self.stdout.write(
            "Tip: add LOCAL_ADMIN_BOOTSTRAP_PASSWORD to .env so START/RESTART keeps it in sync."
        )