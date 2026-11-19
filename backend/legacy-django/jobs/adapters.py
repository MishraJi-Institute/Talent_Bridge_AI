from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from .google_oauth import google_apps_from_settings
from .models import Company, Profile, SignupRecord


class TalentBridgeAccountAdapter(DefaultAccountAdapter):
    def _get_account_redirect_url(self, request):
        session = getattr(request, "session", None)
        next_url = ""
        if session is not None:
            next_url = session.pop("talentbridge.social_login_next", "")
        profile = Profile.objects.filter(user=request.user).first()
        company = Company.objects.filter(owner=request.user).first()
        if profile and profile.role == "employer":
            if company and not company.is_approved:
                return reverse("employer_pending")

        next_url = request.GET.get("next", "") or next_url
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return next_url
        return reverse("dashboard")

    def get_login_redirect_url(self, request):
        request.session.pop("talentbridge.social_signup_role", None)
        return self._get_account_redirect_url(request)

    def get_signup_redirect_url(self, request):
        request.session.pop("talentbridge.social_signup_role", None)
        return self._get_account_redirect_url(request)


class TalentBridgeSocialAccountAdapter(DefaultSocialAccountAdapter):
    def list_apps(self, request, provider=None, client_id=None):
        if provider == "google":
            settings_apps = google_apps_from_settings(client_id=client_id)
            if settings_apps:
                return settings_apps
        return super().list_apps(request, provider=provider, client_id=client_id)

    def is_auto_signup_allowed(self, request, sociallogin):
        return False

    def pre_social_login(self, request, sociallogin):
        super().pre_social_login(request, sociallogin)
        user = getattr(sociallogin, "user", None)
        if not user or not getattr(user, "pk", None) or not (user.email or ""):
            return
        verified = any(
            bool(getattr(address, "verified", False))
            and (getattr(address, "email", "").lower() == user.email.lower())
            for address in getattr(sociallogin, "email_addresses", [])
        )
        if verified:
            SignupRecord.objects.filter(user=user).update(email_verified=True)
            if not user.is_active:
                user.is_active = True
                user.save(update_fields=["is_active"])

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        if form is None:
            return user

        role = form.cleaned_data["role"]
        # Google-created accounts also receive a local password so both login
        # methods work from the first signup session.
        user.set_password(form.cleaned_data["password1"])
        user.save(update_fields=["password"])
        verified = any(
            bool(getattr(address, "verified", False))
            and (getattr(address, "email", "").lower() == (user.email or "").lower())
            for address in getattr(sociallogin, "email_addresses", [])
        )
        SignupRecord.objects.create(
            user=user,
            email=(user.email or "").strip().lower(),
            signup_method="google",
            role=role,
            email_verified=verified,
        )
        full_name = user.get_full_name().strip() or user.email
        Profile.objects.create(
            user=user,
            role=role,
            full_name=full_name[:100],
        )
        if role == "employer":
            Company.objects.create(
                owner=user,
                name=form.cleaned_data["company_name"].strip()[:200],
                is_approved=False,
                location="",
            )
        request.session.pop("talentbridge.social_signup_role", None)
        return user
