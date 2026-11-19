"""Authentication backend supporting username and unambiguous email login.

When multiple user records share an email address, authenticate only the single
record whose password matches. Never silently select the first duplicate.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        identifier = (username or kwargs.get("email") or "").strip()

        if not identifier or not password:
            return None

        if "@" in identifier:
            candidates = User._default_manager.filter(email__iexact=identifier)
        else:
            field = User.USERNAME_FIELD
            candidates = User._default_manager.filter(**{field + "__iexact": identifier})

        # Resolve duplicates using the supplied password, not queryset ordering.
        matches = [
            user for user in candidates
            if user.check_password(password) and self.user_can_authenticate(user)
        ]
        return matches[0] if len(matches) == 1 else None
