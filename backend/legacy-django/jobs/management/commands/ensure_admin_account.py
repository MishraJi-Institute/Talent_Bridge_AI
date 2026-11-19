from getpass import getpass

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = (
        "Create the first TalentBridgeAI superuser when the database has none. "
        "Existing accounts and passwords are never changed."
    )

    def handle(self, *args, **options):
        User = get_user_model()
        existing = User._default_manager.filter(is_superuser=True).order_by("pk").first()
        if existing:
            self.stdout.write(self.style.SUCCESS(
                f"Superuser already exists: {getattr(existing, User.USERNAME_FIELD)}. No account or password changed."
            ))
            return

        if not getattr(__import__("sys").stdin, "isatty", lambda: False)():
            raise CommandError(
                "No superuser exists, and this command needs an interactive terminal. "
                "Run CREATE_ADMIN_AND_START.bat from the project folder."
            )

        self.stdout.write(self.style.WARNING(
            "No superuser exists in this database. Create the first admin now."
        ))
        username_field = User.USERNAME_FIELD
        identifier_label = "Username" if username_field == "username" else username_field.replace("_", " ").title()
        identifier = input(f"{identifier_label}: ").strip()
        if not identifier:
            raise CommandError(f"{identifier_label} cannot be empty.")

        email = ""
        if any(field.name == "email" for field in User._meta.fields):
            email = input("Admin email address: ").strip().lower()
            if not email:
                raise CommandError("Admin email cannot be empty.")

        if User._default_manager.filter(**{f"{username_field}__iexact": identifier}).exists():
            raise CommandError(f"{identifier_label} is already in use by a non-superuser. Choose a different admin username.")
        if email and User._default_manager.filter(email__iexact=email).exists():
            raise CommandError("That email is already assigned to another account. No account was changed.")

        while True:
            password = getpass("New admin password: ")
            confirm = getpass("Confirm admin password: ")
            if not password:
                self.stderr.write("Password cannot be empty.")
                continue
            if password != confirm:
                self.stderr.write("Passwords do not match. Try again.")
                continue
            break

        with transaction.atomic():
            user = User()
            setattr(user, username_field, identifier)
            if email:
                user.email = email
            user.is_active = True
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()

        user.refresh_from_db()
        if not user.check_password(password):
            raise CommandError("Admin was saved but password verification failed. Check database connectivity.")
        self.stdout.write(self.style.SUCCESS(
            f"Admin created and password verified. Login URL: http://127.0.0.1:8000/admin/login/"
        ))
        self.stdout.write(f"Username: {getattr(user, username_field)}")
        self.stdout.write("Password is not displayed or saved in a text file.")
