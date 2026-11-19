from django.contrib.auth import get_user_model
from django.test import TestCase

from .backends import EmailOrUsernameBackend


class EmailOrUsernameBackendTests(TestCase):
    def setUp(self):
        self.backend = EmailOrUsernameBackend()
        self.User = get_user_model()

    def test_duplicate_email_resolves_to_unique_password_match(self):
        self.User.objects.create_user(
            username="first-user", email="shared@example.test", password="First-Strong-Password-123!"
        )
        second = self.User.objects.create_user(
            username="second-user", email="shared@example.test", password="Second-Strong-Password-456!"
        )

        authenticated = self.backend.authenticate(
            None, username="shared@example.test", password="Second-Strong-Password-456!"
        )
        self.assertEqual(authenticated.pk, second.pk)

    def test_duplicate_email_with_same_password_is_rejected_as_ambiguous(self):
        self.User.objects.create_user(
            username="first-user", email="shared@example.test", password="Same-Strong-Password-123!"
        )
        self.User.objects.create_user(
            username="second-user", email="shared@example.test", password="Same-Strong-Password-123!"
        )

        authenticated = self.backend.authenticate(
            None, username="shared@example.test", password="Same-Strong-Password-123!"
        )
        self.assertIsNone(authenticated)

    def test_username_login_still_works_for_admin_accounts(self):
        user = self.User.objects.create_superuser(
            username="site-admin", email="admin@example.test", password="Admin-Strong-Password-123!"
        )
        authenticated = self.backend.authenticate(
            None, username="site-admin", password="Admin-Strong-Password-123!"
        )
        self.assertEqual(authenticated.pk, user.pk)
