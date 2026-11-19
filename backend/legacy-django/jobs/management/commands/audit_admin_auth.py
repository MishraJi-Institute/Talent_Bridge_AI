from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Read-only audit of active staff/superuser accounts and password usability.'

    def handle(self, *args, **options):
        User = get_user_model()
        users = User._default_manager.filter(is_staff=True) | User._default_manager.filter(is_superuser=True)
        if not users.exists():
            self.stdout.write(self.style.WARNING('No staff/superuser accounts were found. No account was created or changed.'))
            return
        for user in users.distinct().order_by(User.USERNAME_FIELD):
            self.stdout.write(
                f'{getattr(user, User.USERNAME_FIELD)} | active={user.is_active} '
                f'| staff={user.is_staff} | superuser={user.is_superuser} '
                f'| password_usable={user.has_usable_password()}'
            )
            if not user.has_usable_password():
                self.stdout.write(self.style.WARNING(
                    '  Password is unusable. Use the interactive Django changepassword command for this existing account; do not reset the database.'
                ))
