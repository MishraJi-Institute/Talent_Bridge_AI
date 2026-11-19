from getpass import getpass
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = "Replace all existing Django superusers with one newly chosen administrator."

    def handle(self, *args, **options):
        User = get_user_model()
        username_field = User.USERNAME_FIELD
        label = "Username" if username_field == "username" else username_field.replace("_", " ").title()

        self.stdout.write(self.style.WARNING(
            "This will delete every existing superuser in THIS project's configured database, "
            "then create exactly one new superuser. Normal user accounts are not deleted."
        ))
        confirm = input("Type REPLACE-ALL-ADMINS to continue: ").strip()
        if confirm != "REPLACE-ALL-ADMINS":
            raise CommandError("Cancelled. No account was changed.")

        identifier = input(f"New admin {label}: ").strip()
        if not identifier:
            raise CommandError(f"{label} cannot be empty.")

        existing = User._default_manager.filter(**{f"{username_field}__iexact": identifier}).first()
        if existing and not existing.is_superuser:
            raise CommandError(f"That {label} belongs to a normal user. Choose a different {label}; no account was changed.")

        email = ""
        if any(field.name == "email" for field in User._meta.fields):
            email = input("New admin email: ").strip().lower()
            if not email:
                raise CommandError("Email cannot be empty.")
            email_owner = User._default_manager.filter(email__iexact=email).exclude(pk=getattr(existing, "pk", None)).first()
            if email_owner:
                raise CommandError("That email belongs to another account. Choose another email; no account was changed.")

        while True:
            password = getpass("New admin password (minimum 12 characters): ")
            confirm_password = getpass("Confirm new admin password: ")
            if len(password) < 12:
                self.stderr.write("Use at least 12 characters.")
            elif password != confirm_password:
                self.stderr.write("Passwords do not match. Try again.")
            else:
                break

        with transaction.atomic():
            User._default_manager.filter(is_superuser=True).delete()
            admin = User()
            setattr(admin, username_field, identifier)
            if email:
                admin.email = email
            admin.is_active = True
            admin.is_staff = True
            admin.is_superuser = True
            admin.set_password(password)
            admin.save()

        admin.refresh_from_db()
        if not admin.check_password(password) or not admin.is_superuser or not admin.is_staff:
            raise CommandError("Post-save verification failed. Check the configured database.")

        self.stdout.write(self.style.SUCCESS("New superuser created and password verified."))
        self.stdout.write(f"Admin {label}: {getattr(admin, username_field)}")
        self.stdout.write("Password stored as a Django password hash in the configured database; it is not written to a text file.")
        self.stdout.write("Admin login: http://127.0.0.1:8000/admin/login/")
