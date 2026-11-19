"""Create the first superuser interactively. Never change an existing account."""
import sys

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = "Keep an existing superuser or interactively create one when none exists."

    def handle(self, *args, **options):
        user_model = get_user_model()
        if user_model.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.SUCCESS(
                "Existing superuser account found. No account or password was changed."
            ))
            return

        if not sys.stdin.isatty():
            self.stderr.write(self.style.ERROR(
                "No superuser exists. Run CREATE_SUPERUSER.bat in a terminal and enter "
                "the username and password there. No account was created."
            ))
            return

        self.stdout.write(self.style.WARNING(
            "No superuser exists. Django will ask for a username, email, and password. "
            "Nothing is hardcoded, and no existing user will be modified."
        ))
        call_command("createsuperuser", interactive=True)
        if not user_model.objects.filter(is_superuser=True).exists():
            self.stderr.write(self.style.ERROR("No superuser was created. Admin login will not be available."))
            return
        self.stdout.write(self.style.SUCCESS("Administrator account created."))
