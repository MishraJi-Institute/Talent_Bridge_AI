import re
import tempfile
from decimal import Decimal
from datetime import timedelta
from io import StringIO
from urllib.parse import urlparse
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.files.base import ContentFile
from django.contrib.sites.models import Site
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client, RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from allauth.core.context import request_context
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialLogin, SocialToken

from config.urls import PAGES
from .adapters import TalentBridgeAccountAdapter
from .forms import TalentBridgeSocialSignupForm
from .google_oauth import sync_google_social_app
from .models import (
    Application,
    ApplicationStatusEvent,
    Company,
    ContactInquiry,
    Interview,
    Job,
    Notification,
    Profile,
    ResumeDraft,
    SavedJob,
    SignupRecord,
)

User = get_user_model()


class GoogleOAuthConfigHealthCheckTests(TestCase):
    @override_settings(
        GOOGLE_OAUTH_CLIENT_ID="health-check-client-id",
        GOOGLE_OAUTH_CLIENT_SECRET="health-check-client-secret",
    )
    def test_health_check_reports_presence_without_exposing_credentials(self):
        output = StringIO()

        call_command("check_google_oauth", stdout=output)

        result = output.getvalue()
        self.assertIn("Google OAuth Client ID loaded: yes", result)
        self.assertIn("Google OAuth Client Secret loaded: yes", result)
        self.assertIn("Google OAuth configuration is loaded by Django.", result)
        self.assertNotIn("health-check-client-id", result)
        self.assertNotIn("health-check-client-secret", result)

    @override_settings(
        GOOGLE_OAUTH_CLIENT_ID="",
        GOOGLE_OAUTH_CLIENT_SECRET="",
    )
    def test_health_check_fails_when_credentials_are_missing(self):
        output = StringIO()

        with self.assertRaises(CommandError):
            call_command("check_google_oauth", stdout=output)

        result = output.getvalue()
        self.assertIn("Google OAuth Client ID loaded: no", result)
        self.assertIn("Google OAuth Client Secret loaded: no", result)


class AdminTipBotTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="tip-bot-admin",
            password="test-password",
            is_staff=True,
            is_superuser=True,
        )

    def test_staff_admin_dashboard_renders_wellness_bot(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="admin-tip-bot"')
        self.assertContains(response, 'id="admin-tip-next"')
        self.assertContains(response, "jobs/admin-tip-bot.js")

    def test_admin_login_does_not_show_wellness_bot(self):
        response = self.client.get(reverse("admin:login"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id="admin-tip-bot"')
        self.assertNotContains(response, "jobs/admin-tip-bot.js")
        self.assertNotContains(response, '}") center/cover fixed;')
        self.assertContains(response, "jobs/admin-office-background.png")
        self.assertContains(response, "family=Inter")

    def test_superuser_can_log_in_and_open_admin(self):
        self.assertTrue(
            self.client.login(
                username=self.admin_user.username,
                password="test-password",
            )
        )

        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)

    def test_admin_control_center_and_user_workflows_render_with_shared_styles(self):
        self.client.force_login(self.admin_user)
        admin_pages = (
            reverse("admin:index"),
            reverse("admin:auth_user_changelist"),
            reverse("admin:auth_user_add"),
            reverse("admin:auth_user_change", args=[self.admin_user.pk]),
            reverse("admin:password_change"),
            reverse("admin:jobs_job_changelist"),
        )

        for url in admin_pages:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "jobs/admin.css?v=20261117-2")

        dashboard = self.client.get(reverse("admin:index"))
        self.assertContains(dashboard, 'id="recent-actions-module"')

        stylesheet_path = finders.find("jobs/admin.css")
        self.assertIsNotNone(stylesheet_path)
        with open(stylesheet_path, encoding="utf-8") as stylesheet:
            css = stylesheet.read()
        self.assertRegex(
            css,
            r"#content-related\s*\{\s*background:\s*transparent !important;",
        )
        self.assertRegex(
            css,
            r"\.module caption a,\s*\.module caption a:link,\s*\.module caption a:visited\s*\{\s*color:\s*var\(--tb-admin-heading\) !important;",
        )
        self.assertRegex(
            css,
            r"\.button:disabled,[\s\S]*?background:\s*#E2E8F0 !important;[\s\S]*?transition:\s*none;",
        )

    def test_admin_logout_clears_session_and_returns_to_login(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(reverse("admin:logout"))

        self.assertIn(response.status_code, (200, 302))
        self.assertNotIn("_auth_user_id", self.client.session)
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("admin:login"), response["Location"])


class DjangoDashboardAuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="dashboard-user@example.com",
            email="dashboard-user@example.com",
            password="SecurePass123!",
        )

    def test_dashboard_redirects_anonymous_user_to_django_login(self):
        response = self.client.get("/pages/dashboard/cdashboard.html")

        self.assertRedirects(
            response,
            "/login/?next=%2Fpages%2Fdashboard%2Fcdashboard.html",
            fetch_redirect_response=False,
        )

    def test_nested_dashboard_page_uses_its_directory_as_the_base_url(self):
        self.client.force_login(self.user)

        response = self.client.get("/pages/dashboard/jdashboard.html")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<base href="/pages/dashboard/">')

    def test_django_session_allows_dashboard_and_injects_account_identity(self):
        self.client.force_login(self.user)

        response = self.client.get("/pages/dashboard/cdashboard.html")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'data-auth-user-id="{self.user.pk}"')
        self.assertContains(response, 'data-auth-email="dashboard-user@example.com"')
        self.assertNotContains(response, "supabase-js")

    def test_dashboard_entry_redirects_anonymous_user_to_login(self):
        response = self.client.get(reverse("dashboard"))

        self.assertRedirects(
            response,
            "/login/?next=%2Fdashboard%2F",
            fetch_redirect_response=False,
        )

    def test_job_listing_navigation_uses_dashboard_action_for_signed_in_users(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("jobs"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="auth-btn auth-dashboard"')
        self.assertNotContains(response, 'class="auth-btn auth-signin"')
        self.assertNotContains(response, 'class="auth-btn auth-signup"')

    def test_login_uses_animated_page_and_preserves_safe_next_url(self):
        response = self.client.get(reverse("login"), {"next": "/pages/dashboard/jdashboard.html"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="login-visual"')
        self.assertContains(response, 'aria-label="Show password"')
        self.assertContains(
            response,
            '<input type="hidden" name="next" value="/pages/dashboard/jdashboard.html">',
        )
        self.assertContains(response, "../css/pages/login-motion.css")
        self.assertNotContains(response, "login-10sec.js")

    def test_invalid_login_displays_authentication_error(self):
        response = self.client.post(
            reverse("login"),
            {"email": "missing@example.com", "password": "incorrect"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email or password is incorrect.")

    def test_dashboard_entry_routes_job_seeker_to_job_seeker_workspace(self):
        Profile.objects.create(user=self.user, full_name="Jamie Candidate", role="job_seeker")
        self.client.force_login(self.user)

        response = self.client.get(reverse("dashboard"))

        self.assertRedirects(response, "/pages/dashboard/jdashboard.html", fetch_redirect_response=False)

    def test_dashboard_profile_save_persists_education_to_account(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("dashboard-profile-save"),
            {
                "full_name": "Jamie Candidate",
                "headline": "Product designer",
                "location": "Pune",
                "skills": "Research, prototyping",
                "experience": "Five years",
                "education": "B.Des, Interaction Design",
                "description": "Designing helpful products.",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            ResumeDraft.objects.get(user=self.user).content["education"],
            "B.Des, Interaction Design",
        )
        dashboard = self.client.get("/pages/dashboard/jdashboard.html")
        self.assertContains(dashboard, 'data-account-education="B.Des, Interaction Design"')

    def test_job_seeker_dashboard_personalizes_welcome_and_clarifies_demo_data(self):
        self.user.first_name = "Jamie"
        self.user.last_name = "Candidate"
        self.user.save(update_fields=("first_name", "last_name"))
        self.client.force_login(self.user)

        response = self.client.get("/pages/dashboard/jdashboard.html")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-auth-name="Jamie Candidate"')
        self.assertContains(response, 'aria-label="Dashboard account and demo data"')
        self.assertContains(response, 'data-profile-save-url="/dashboard/profile/save/"')
        self.assertContains(response, 'href="/jobs/"')
        self.assertContains(response, 'href="/applied-jobs/"')
        self.assertContains(
            response,
            '<a class="button ghost" href="/resume-management/">Upload Resume <span>→</span></a>',
        )
        self.assertContains(response, 'href="/resume-management/">Resume Library</a>')

    def test_dashboard_entry_routes_approved_employer_to_employer_workspace(self):
        Profile.objects.create(user=self.user, full_name="Jamie Employer", role="employer")
        Company.objects.create(owner=self.user, name="Bridge Works", is_approved=True)
        self.client.force_login(self.user)

        response = self.client.get(reverse("dashboard"))

        self.assertRedirects(response, "/pages/dashboard/cdashboard.html", fetch_redirect_response=False)

    def test_oauth_redirect_uses_dashboard_router_even_without_a_profile(self):
        request = RequestFactory().get("/")
        request.user = self.user

        redirect_url = TalentBridgeAccountAdapter()._get_account_redirect_url(request)

        self.assertEqual(redirect_url, reverse("dashboard"))

    def test_oauth_redirect_routes_existing_job_seeker_through_dashboard_router(self):
        Profile.objects.create(user=self.user, full_name="Jamie Candidate", role="job_seeker")
        request = RequestFactory().get("/")
        request.user = self.user

        redirect_url = TalentBridgeAccountAdapter()._get_account_redirect_url(request)

        self.assertEqual(redirect_url, reverse("dashboard"))

    def test_dashboard_entry_keeps_unapproved_employer_pending(self):
        Profile.objects.create(user=self.user, full_name="Jamie Employer", role="employer")
        Company.objects.create(owner=self.user, name="Bridge Works", is_approved=False)
        self.client.force_login(self.user)

        response = self.client.get(reverse("dashboard"))

        self.assertRedirects(response, reverse("employer_pending"), fetch_redirect_response=False)

    def test_pending_employer_page_resolves_assets_and_shows_company_status(self):
        company = Company.objects.create(owner=self.user, name="Bridge Works", is_approved=False)
        self.client.force_login(self.user)

        response = self.client.get(reverse("employer_pending"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<base href="/pages/">')
        self.assertContains(response, "Approval review in progress")
        self.assertContains(response, company.name)
        self.assertContains(response, "Employer workspace")
        self.assertNotContains(response, 'href="login.html"')
        self.assertNotContains(response, "Static site preview")
        self.assertEqual(
            self.client.get("/css/base/portal-pages.css").status_code,
            200,
        )
        self.assertEqual(
            self.client.get("/js/core/site-experience.js").status_code,
            200,
        )

    def test_approved_employer_is_redirected_out_of_pending_page(self):
        Profile.objects.create(user=self.user, full_name="Jamie Employer", role="employer")
        Company.objects.create(owner=self.user, name="Bridge Works", is_approved=True)
        self.client.force_login(self.user)

        response = self.client.get(reverse("employer_pending"))

        self.assertRedirects(
            response,
            "/dashboard/",
            fetch_redirect_response=False,
        )

    def test_legacy_employer_dashboard_redirects_to_canonical_dashboard(self):
        self.client.force_login(self.user)

        response = self.client.get("/pages/dashboard/dindex.html")

        self.assertRedirects(
            response,
            "/pages/dashboard/cdashboard.html",
            fetch_redirect_response=False,
        )

    def test_employer_dashboard_keeps_blue_theme_without_theme_controls(self):
        self.client.force_login(self.user)

        response = self.client.get("/pages/dashboard/cdashboard.html")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id="themeSelect"')
        self.assertNotContains(response, 'id="quickTheme"')
        self.assertNotContains(response, 'id="profileAccentInput"')
        self.assertNotContains(response, 'data-accent="#8255d9"')

    def test_employer_customization_page_has_no_theme_color_controls(self):
        self.client.force_login(self.user)

        response = self.client.get("/pages/dashboard/customize.html")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id="themeSelectPage"')
        self.assertNotContains(response, 'id="customAccentPage"')
        self.assertNotContains(response, "Accent color")

    def test_job_seeker_dashboard_has_no_cross_role_workspace_switch(self):
        self.client.force_login(self.user)

        response = self.client.get("/pages/dashboard/jdashboard.html")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Employer workspace")
        self.assertNotContains(response, 'id="customThemeBuilder"')
        self.assertNotContains(response, 'data-accent="violet"')

    def test_homepage_hides_both_role_specific_dashboard_buttons(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'class="auth-btn auth-dashboard"')
        self.assertNotContains(response, 'class="auth-btn auth-jdashboard"')


class JobSeekerSignupPageTests(TestCase):
    def test_authentication_navigation_uses_friendly_django_routes(self):
        pages = (
            (
                "/login/",
                (
                    'href="/forgot-password/"',
                    'href="/signup/job-seeker/"',
                    'href="/signup/employer/"',
                ),
            ),
            (
                "/signup/",
                (
                    'href="/signup/job-seeker/"',
                    'href="/signup/employer/"',
                    'href="/login/"',
                ),
            ),
            (
                "/signup/job-seeker/",
                ('href="/terms/"', 'href="/privacy/"', 'href="/login/"'),
            ),
            (
                "/signup/employer/",
                ('href="/terms/"', 'href="/privacy/"', 'href="/login/"'),
            ),
        )

        for path, expected_links in pages:
            with self.subTest(path=path):
                response = self.client.get(path)

                self.assertEqual(response.status_code, 200)
                for link in expected_links:
                    self.assertContains(response, link)

    def test_friendly_page_alias_resolves_relative_links_from_pages_directory(self):
        response = self.client.get(reverse("pricing"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<base href="/pages/">')
        self.assertEqual(self.client.get("/pages/login.html").status_code, 200)

    def test_top_level_page_uses_pages_root_as_its_base_url(self):
        response = self.client.get("/pages/login.html")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<base href="/pages/">')
        self.assertEqual(self.client.get("/css/pages/login.css").status_code, 200)

    def test_signup_page_renders_form_action(self):
        response = self.client.get(reverse("jobseeker_signup_page"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<form id="jobSeekerForm" action="/signup/job-seeker/" method="post">',
        )
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertNotContains(response, "{% csrf_token %}")

    def test_signup_password_requirements_render_without_encoding_errors(self):
        for route_name in ("jobseeker_signup_page", "employer_signup_page"):
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "A–Z")
                self.assertContains(response, "a–z")
                self.assertContains(response, "0–9")

    @override_settings(
        GOOGLE_OAUTH_CLIENT_ID="test-client-id",
        GOOGLE_OAUTH_CLIENT_SECRET="test-client-secret",
    )
    def test_social_signup_buttons_post_provider_and_account_role(self):
        pages = (
            ("login_page", "choose"),
            ("jobseeker_signup_page", "job_seeker"),
            ("employer_signup_page", "employer"),
        )
        for route_name, role in pages:
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'name="role" value="{}"'.format(role))
                expected_label = "Continue with Google" if route_name == "login_page" else "Google"
                self.assertContains(
                    response,
                    'class="social-name">{}</span>'.format(expected_label),
                )
                self.assertNotContains(response, "LinkedIn")
                self.assertNotContains(response, "Microsoft")
                self.assertContains(response, "talentbridge-mark.svg")
                self.assertContains(
                    response,
                    'data-oauth-provider="google" action="{}" method="post"'.format(
                        reverse("social-login-start", args=("google",)),
                    ),
                )
                self.assertContains(response, 'src="../js/authentication/google-oauth.js"')
                self.assertNotContains(response, 'disabled aria-describedby="google-oauth-notice"')
                self.assertNotContains(response, 'id="google-oauth-notice"')

    def test_social_sign_in_forms_preserve_requested_destination(self):
        pages = ("login_page", "jobseeker_signup_page", "employer_signup_page")
        for route_name in pages:
            with self.subTest(route_name=route_name):
                response = self.client.get(
                    reverse(route_name),
                    {"next": "/saved-jobs/"},
                )

                self.assertEqual(response.status_code, 200)
                self.assertContains(
                    response,
                    'name="next" value="/saved-jobs/"',
                )

    def test_password_validation_prevents_invalid_signup_submission(self):
        for route_name in ("jobseeker_signup_page", "employer_signup_page"):
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))

                self.assertContains(response, "event.preventDefault();")


class SocialAuthenticationTests(TestCase):
    @override_settings(
        SOCIALACCOUNT_PROVIDERS={
            "google": {
                "APPS": [
                    {
                        "name": "Google",
                        "client_id": "test-client-id",
                        "secret": "test-client-secret",
                    },
                ],
                "EMAIL_AUTHENTICATION": True,
                "EMAIL_AUTHENTICATION_AUTO_CONNECT": True,
                "SCOPE": ["openid", "email", "profile"],
            },
        },
    )
    def test_google_email_authentication_matches_only_verified_google_email(self):
        email = "existing-google@example.com"
        user = User.objects.create_user(
            username=email,
            email=email,
            password="SecurePass123!",
        )
        request = RequestFactory().get("/")

        with request_context(request):
            provider = get_adapter().get_provider(request, "google")
            verified_login = provider.sociallogin_from_response(
                request,
                {
                    "email": email,
                    "email_verified": True,
                    "given_name": "Taylor",
                    "sub": "verified-google-subject",
                },
            )
            unverified_login = provider.sociallogin_from_response(
                request,
                {
                    "email": email,
                    "email_verified": False,
                    "given_name": "Taylor",
                    "sub": "unverified-google-subject",
                },
            )
            matched_account = get_adapter().authenticate_by_email(verified_login)
            unmatched_account = get_adapter().authenticate_by_email(unverified_login)

        self.assertIsNotNone(matched_account)
        self.assertEqual(matched_account[0], user)
        self.assertEqual(matched_account[1], email)
        self.assertIsNone(unmatched_account)

    @override_settings(
        SOCIALACCOUNT_PROVIDERS={
            "google": {
                "APPS": [
                    {
                        "name": "Google",
                        "client_id": "test-client-id",
                        "secret": "test-client-secret",
                    },
                ],
                "SCOPE": ["openid", "email", "profile"],
            },
        },
    )
    def test_google_callback_cancellation_and_invalid_state_do_not_authenticate(self):
        start_response = self.client.post(
            reverse("social-login-start", args=("google",)),
            {"role": "choose"},
        )
        self.assertEqual(start_response.status_code, 302)

        states = self.client.session.get("socialaccount_states", {})
        self.assertTrue(states)
        state_id = next(iter(states))
        cancelled_response = self.client.get(
            reverse("google_callback"),
            {"error": "access_denied", "state": state_id},
        )

        self.assertRedirects(
            cancelled_response,
            reverse("socialaccount_login_cancelled"),
            fetch_redirect_response=False,
        )
        self.assertEqual(
            self.client.get(cancelled_response.url).status_code,
            200,
        )
        self.assertNotIn("_auth_user_id", self.client.session)

        invalid_state_response = self.client.get(
            reverse("google_callback"),
            {"code": "not-a-real-authorization-code", "state": "invalid-state"},
        )
        self.assertEqual(invalid_state_response.status_code, 401)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_social_signup_page_renders_account_setup_form(self):
        sociallogin = SocialLogin(
            account=SocialAccount(provider="google", uid="signup-page-subject"),
            user=User(email="setup@example.com"),
        )
        session = self.client.session
        session["talentbridge.social_signup_role"] = "employer"
        session.save()

        with patch(
            "allauth.socialaccount.views.flows.signup.get_pending_signup",
            return_value=sociallogin,
        ):
            response = self.client.get(reverse("socialaccount_signup"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Complete your account")
        self.assertContains(response, 'name="csrfmiddlewaretoken"', html=False)
        self.assertContains(response, 'name="company_name"')
        self.assertContains(response, 'name="role"', html=False)
        self.assertContains(response, 'action="/accounts/3rdparty/signup/"', html=False)
        self.assertContains(response, 'href="/"', html=False)
        self.assertNotContains(response, 'href="../../index.html"')
        self.assertNotContains(response, 'href="/accounts/index.html"')
        self.assertNotContains(response, "No new account is confirmed")

    def test_accounts_index_html_redirects_home(self):
        """Broken relative home links under /accounts/ must not 404."""
        response = self.client.get("/accounts/index.html")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "/")

    @override_settings(
        SOCIALACCOUNT_PROVIDERS={},
        GOOGLE_OAUTH_CLIENT_ID="",
        GOOGLE_OAUTH_CLIENT_SECRET="",
    )
    def test_unconfigured_google_returns_user_to_sign_in_with_notice(self):
        response = self.client.post(
            reverse("social-login-start", args=("google",)),
            {"role": "choose"},
        )

        self.assertRedirects(
            response,
            reverse("login"),
            fetch_redirect_response=False,
        )
        follow = self.client.get(response.url)
        self.assertContains(follow, "Google sign-in is not configured")
        self.assertContains(follow, "temporarily unavailable")
        self.assertContains(follow, 'disabled aria-describedby="google-oauth-notice"')
        self.assertNotContains(follow, "Google sign-in is not configured yet")


    @override_settings(
        GOOGLE_OAUTH_CLIENT_ID="only-client-id",
        GOOGLE_OAUTH_CLIENT_SECRET="",
        SOCIALACCOUNT_PROVIDERS={},
    )
    def test_partial_google_credentials_do_not_break_site_or_enable_google(self):
        response = self.client.get(reverse("jobseeker_signup_page"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "temporarily unavailable")
        self.assertContains(response, 'disabled aria-describedby="google-oauth-notice"')

    @override_settings(
        GOOGLE_OAUTH_CLIENT_ID="test-client-id",
        GOOGLE_OAUTH_CLIENT_SECRET="test-client-secret",
    )
    def test_direct_auth_pages_receive_google_enabled_context(self):
        for path in ("/pages/login.html", "/pages/jobseeker-signup.html", "/pages/company-signup.html"):
            with self.subTest(path=path):
                response = self.client.get(path)

                self.assertEqual(response.status_code, 200)
                self.assertNotContains(response, 'disabled aria-describedby="google-oauth-notice"')
                self.assertNotContains(response, 'id="google-oauth-notice"')

    @override_settings(
        GOOGLE_OAUTH_CLIENT_ID="test-client-id",
        GOOGLE_OAUTH_CLIENT_SECRET="test-client-secret",
        SOCIALACCOUNT_PROVIDERS={"google": {"SCOPE": ["openid", "email", "profile"]}},
    )
    def test_google_sign_in_syncs_one_site_associated_app_before_starting_oauth(self):
        response = self.client.post(
            reverse("social-login-start", args=("google",)),
            {"role": "choose"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response["Location"]).hostname, "accounts.google.com")
        app = SocialApp.objects.get(provider="google")
        self.assertEqual(app.client_id, "test-client-id")
        self.assertTrue(app.sites.filter(pk=settings.SITE_ID).exists())

    @override_settings(
        GOOGLE_OAUTH_CLIENT_ID="test-client-id",
        GOOGLE_OAUTH_CLIENT_SECRET="test-client-secret",
        SOCIALACCOUNT_PROVIDERS={"google": {"SCOPE": ["openid", "email", "profile"]}},
    )
    def test_google_oauth_bounces_alternate_local_port_to_site_domain(self):
        site = Site.objects.get(pk=settings.SITE_ID)
        original_domain = site.domain
        site.domain = "127.0.0.1:8000"
        site.save(update_fields=["domain"])
        Site.objects.clear_cache()
        try:
            response = self.client.post(
                reverse("social-login-start", args=("google",)),
                {"role": "job_seeker", "next": "/dashboard/"},
                HTTP_HOST="127.0.0.1:8001",
            )

            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response["Location"],
                "http://127.0.0.1:8000/auth/social/google/?role=job_seeker&next=%2Fdashboard%2F",
            )
        finally:
            site.domain = original_domain
            site.save(update_fields=["domain"])
            Site.objects.clear_cache()

    @override_settings(
        GOOGLE_OAUTH_CLIENT_ID="test-client-id",
        GOOGLE_OAUTH_CLIENT_SECRET="test-client-secret",
        SOCIALACCOUNT_PROVIDERS={"google": {"SCOPE": ["openid", "email", "profile"]}},
    )
    def test_google_callback_url_uses_local_site_domain(self):
        from jobs.google_oauth import (
            ensure_google_oauth_callback_patch,
            google_oauth_callback_url,
        )

        site = Site.objects.get(pk=settings.SITE_ID)
        original_domain = site.domain
        site.domain = "127.0.0.1:8000"
        site.save(update_fields=["domain"])
        Site.objects.clear_cache()
        try:
            ensure_google_oauth_callback_patch()
            self.assertEqual(
                google_oauth_callback_url(),
                "http://127.0.0.1:8000/accounts/google/login/callback/",
            )
        finally:
            site.domain = original_domain
            site.save(update_fields=["domain"])
            Site.objects.clear_cache()

    @override_settings(
        GOOGLE_OAUTH_CLIENT_ID="canonical-client-id",
        GOOGLE_OAUTH_CLIENT_SECRET="canonical-client-secret",
        SOCIALACCOUNT_PROVIDERS={"google": {"SCOPE": ["openid", "email", "profile"]}},
    )
    def test_google_app_sync_merges_duplicates_and_preserves_tokens_and_site_links(self):
        primary_site = Site.objects.get(pk=settings.SITE_ID)
        secondary_site = Site.objects.create(domain="other.example", name="Other Site")
        user = User.objects.create_user(
            username="oauth-token-owner@example.com",
            email="oauth-token-owner@example.com",
            password="SecurePass123!",
        )
        account = SocialAccount.objects.create(
            user=user,
            provider="google",
            uid="oauth-token-owner-subject",
        )
        duplicate = SocialApp.objects.create(
            provider="google", name="Old Google", client_id="old-client-id", secret="old-secret"
        )
        canonical = SocialApp.objects.create(
            provider="google",
            name="Google",
            client_id="canonical-client-id",
            secret="canonical-client-secret",
        )
        duplicate.sites.add(primary_site)
        canonical.sites.add(secondary_site)
        SocialToken.objects.create(app=duplicate, account=account, token="old-access-token")
        SocialToken.objects.create(app=canonical, account=account, token="current-access-token")

        result = sync_google_social_app()

        self.assertEqual(result["merged"], 1)
        self.assertEqual(SocialApp.objects.filter(provider="google").count(), 1)
        canonical.refresh_from_db()
        self.assertEqual(canonical.client_id, "canonical-client-id")
        self.assertSetEqual(
            set(canonical.sites.values_list("pk", flat=True)),
            {primary_site.pk, secondary_site.pk},
        )
        self.assertEqual(SocialToken.objects.count(), 2)
        self.assertEqual(SocialToken.objects.filter(app=canonical).count(), 1)
        self.assertEqual(SocialToken.objects.filter(app__isnull=True).count(), 1)
        repeated = sync_google_social_app()
        self.assertFalse(repeated["created"])
        self.assertEqual(repeated["merged"], 0)

    @override_settings(
        SOCIALACCOUNT_PROVIDERS={
            "google": {
                "APPS": [
                    {
                        "name": "Google",
                        "client_id": "test-client-id",
                        "secret": "test-client-secret",
                    },
                ],
            },
        },
    )
    def test_google_buttons_are_enabled_when_oauth_is_configured(self):
        for route_name in ("login_page", "jobseeker_signup_page", "employer_signup_page"):
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))

                self.assertEqual(response.status_code, 200)
                self.assertNotContains(response, 'disabled aria-describedby="google-oauth-notice"')
                self.assertNotContains(response, 'id="google-oauth-notice"')
                if route_name == "login_page":
                    self.assertContains(response, "Sign in securely with your Google account")

    def test_linkedin_and_microsoft_oauth_endpoints_are_disabled(self):
        for provider in ("linkedin", "microsoft"):
            for method in (self.client.get, self.client.post):
                with self.subTest(provider=provider, method=method.__name__):
                    response = method(
                        reverse("social-login-start", args=(provider,)),
                        {"role": "choose"},
                    )

                    self.assertEqual(response.status_code, 404)

    @override_settings(
        SOCIALACCOUNT_PROVIDERS={
            "google": {
                "APPS": [
                    {
                        "name": "Google",
                        "client_id": "test-client-id",
                        "secret": "test-client-secret",
                    },
                ],
                "SCOPE": ["openid", "email", "profile"],
            },
        },
    )
    def test_google_sign_in_starts_oauth_from_csrf_protected_post(self):
        client = Client(enforce_csrf_checks=True)
        page = client.get(reverse("login_page"))
        match = re.search(
            r'name="csrfmiddlewaretoken" value="([^"]+)"',
            page.content.decode(),
        )

        self.assertIsNotNone(match)
        response = client.post(
            reverse("social-login-start", args=("google",)),
            {"role": "choose", "csrfmiddlewaretoken": match.group(1)},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response["Location"]).hostname, "accounts.google.com")

    @override_settings(
        SOCIALACCOUNT_PROVIDERS={
            "google": {
                "APPS": [
                    {
                        "name": "Google",
                        "client_id": "test-client-id",
                        "secret": "test-client-secret",
                    },
                ],
                "SCOPE": ["openid", "email", "profile"],
            },
        },
    )
    def test_google_sign_in_restores_safe_requested_destination_after_oauth(self):
        response = self.client.post(
            reverse("social-login-start", args=("google",)),
            {"role": "choose", "next": "/saved-jobs/"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            self.client.session["talentbridge.social_login_next"],
            "/saved-jobs/",
        )

        request = RequestFactory().get("/accounts/google/login/callback/")
        request.user = User.objects.create_user(
            username="social-next@example.com",
            email="social-next@example.com",
            password="SecurePass123!",
        )
        request.session = self.client.session
        self.assertEqual(
            TalentBridgeAccountAdapter()._get_account_redirect_url(request),
            "/saved-jobs/",
        )
        self.assertNotIn("talentbridge.social_login_next", request.session)

    @override_settings(
        SOCIALACCOUNT_PROVIDERS={
            "google": {
                "APPS": [
                    {
                        "name": "Google",
                        "client_id": "test-client-id",
                        "secret": "test-client-secret",
                    },
                ],
                "SCOPE": ["openid", "email", "profile"],
            },
        },
    )
    def test_social_sign_in_does_not_store_external_next_destination(self):
        response = self.client.post(
            reverse("social-login-start", args=("google",)),
            {"role": "choose", "next": "https://example.invalid/"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertNotIn("talentbridge.social_login_next", self.client.session)

    @override_settings(
        SOCIALACCOUNT_PROVIDERS={
            "google": {
                "APPS": [
                    {
                        "name": "Google",
                        "client_id": "test-client-id",
                        "secret": "test-client-secret",
                    },
                ],
                "SCOPE": ["openid", "email", "profile"],
            },
        },
    )
    def test_google_sign_in_get_auto_posts_to_provider_with_csrf(self):
        client = Client(enforce_csrf_checks=True)
        response = client.get(
            reverse("social-login-start", args=("google",)),
            {"role": "choose"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f'action="{reverse("social-login-start", args=("google",))}"',
        )
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertContains(response, 'name="role" value="choose"')
        self.assertContains(response, 'document.getElementById("provider-login").submit()')

        csrf_match = re.search(
            r'name="csrfmiddlewaretoken" value="([^"]+)"',
            response.content.decode(),
        )
        self.assertIsNotNone(csrf_match)
        provider_response = client.post(
            reverse("social-login-start", args=("google",)),
            {
                "role": "choose",
                "csrfmiddlewaretoken": csrf_match.group(1),
            },
        )
        self.assertEqual(provider_response.status_code, 302)
        self.assertEqual(
            urlparse(provider_response["Location"]).hostname,
            "accounts.google.com",
        )

    @override_settings(
        SOCIALACCOUNT_PROVIDERS={
            "google": {
                "APPS": [
                    {
                        "name": "Google",
                        "client_id": "test-client-id",
                        "secret": "test-client-secret",
                    },
                ],
                "SCOPE": ["openid", "email", "profile"],
            },
        },
    )
    def test_google_get_auto_post_preserves_signup_role_and_safe_next(self):
        response = self.client.get(
            reverse("social-login-start", args=("google",)),
            {"role": "employer", "next": "/saved-jobs/"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="role" value="employer"')
        self.assertContains(response, 'name="next" value="/saved-jobs/"')

        unsafe_response = self.client.get(
            reverse("social-login-start", args=("google",)),
            {"role": "employer", "next": "https://example.invalid/"},
        )
        self.assertEqual(unsafe_response.status_code, 200)
        self.assertContains(unsafe_response, 'name="next" value=""')

    def test_social_signup_requires_employer_company_name(self):
        request = RequestFactory().get("/")
        request.session = {}
        sociallogin = SocialLogin(
            account=SocialAccount(provider="google", uid="test-subject"),
            user=User(email="employer@example.com"),
        )
        with request_context(request):
            form = TalentBridgeSocialSignupForm(
                data={
                    "email": "employer@example.com",
                    "password1": "SecurePass123!",
                    "password2": "SecurePass123!",
                    "role": "employer",
                    "company_name": "",
                },
                sociallogin=sociallogin,
            )

        self.assertFalse(form.is_valid())
        self.assertIn("company_name", form.errors)

    def test_social_signup_uses_session_role_instead_of_tampered_form_role(self):
        request = RequestFactory().get("/")
        request.session = {"talentbridge.social_signup_role": "job_seeker"}
        sociallogin = SocialLogin(
            account=SocialAccount(provider="google", uid="role-protected-subject"),
            user=User(email="role-protected@example.com"),
        )
        with request_context(request):
            form = TalentBridgeSocialSignupForm(
                data={
                    "email": "role-protected@example.com",
                    "password1": "SecurePass123!",
                    "password2": "SecurePass123!",
                    "role": "employer",
                    "company_name": "Unexpected Company",
                },
                sociallogin=sociallogin,
            )
            self.assertTrue(form.is_valid(), form.errors)
            user = form.save(request)

        self.assertEqual(Profile.objects.get(user=user).role, "job_seeker")
        self.assertFalse(Company.objects.filter(owner=user).exists())

    def test_social_signup_creates_employer_profile_and_pending_company(self):
        request = RequestFactory().get("/")
        request.session = {"talentbridge.social_signup_role": "employer"}
        sociallogin = SocialLogin(
            account=SocialAccount(provider="google", uid="new-employer-subject"),
            user=User(email="oauth-employer@example.com", first_name="Casey", last_name="Lee"),
        )
        with request_context(request):
            form = TalentBridgeSocialSignupForm(
                data={
                    "email": "oauth-employer@example.com",
                    "password1": "SecurePass123!",
                    "password2": "SecurePass123!",
                    "role": "employer",
                    "company_name": "Bridge Works",
                },
                sociallogin=sociallogin,
            )
            self.assertTrue(form.is_valid(), form.errors)
            user = form.save(request)

        profile = Profile.objects.get(user=user)
        company = Company.objects.get(owner=user)
        self.assertEqual(profile.role, "employer")
        self.assertEqual(company.name, "Bridge Works")
        self.assertFalse(company.is_approved)
        user.refresh_from_db()
        self.assertTrue(user.check_password("SecurePass123!"))
        audit = SignupRecord.objects.get(user=user)
        self.assertEqual(audit.signup_method, "google")
        self.assertEqual(audit.role, "employer")

    def test_signup_accepts_a_valid_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        response = client.get(reverse("jobseeker_signup_page"))
        match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.content.decode())

        self.assertIsNotNone(match)
        response = client.post(
            reverse("jobseeker_signup"),
            {
                "firstName": "Taylor",
                "lastName": "Morgan",
                "email": "taylor.morgan@example.com",
                "phone": "+1 555 123 4567",
                "password": "SecurePass123!",
                "confirmPassword": "SecurePass123!",
                "terms": "on",
                "csrfmiddlewaretoken": match.group(1),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email="taylor.morgan@example.com").exists())

    def test_email_signup_creates_admin_audit_record(self):
        response = self.client.post(
            reverse("jobseeker_signup"),
            {
                "firstName": "Audit", "lastName": "Candidate",
                "email": "audit.candidate@example.com", "phone": "+1 555 123 4567",
                "password": "SecurePass123!", "confirmPassword": "SecurePass123!",
                "terms": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        record = SignupRecord.objects.get(email="audit.candidate@example.com")
        self.assertEqual(record.signup_method, "email_password")
        self.assertEqual(record.role, "job_seeker")
        self.assertFalse(record.email_verified)
        self.assertTrue(User.objects.get(email="audit.candidate@example.com").is_active)
        self.assertEqual(len(mail.outbox), 0)

    def test_unverified_email_signup_can_sign_in_without_verification(self):
        user = User.objects.create_user(
            username="unverified@example.com",
            email="unverified@example.com",
            password="SecurePass123!",
            is_active=False,
        )
        SignupRecord.objects.create(
            user=user,
            email=user.email,
            signup_method="email_password",
            role="job_seeker",
            email_verified=False,
        )

        response = self.client.post(
            reverse("login"),
            {"email": user.email, "password": "SecurePass123!"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session["_auth_user_id"], str(user.pk))
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_resend_verification_does_not_change_account_or_send_email(self):
        user = User.objects.create_user(
            username="inactive@example.com",
            email="inactive@example.com",
            password="SecurePass123!",
            is_active=False,
        )

        response = self.client.post(
            reverse("resend-verification"),
            {"email": user.email},
        )

        self.assertRedirects(response, reverse("login"), fetch_redirect_response=False)
        user.refresh_from_db()
        self.assertFalse(user.is_active)
        self.assertEqual(len(mail.outbox), 0)

    def test_email_signup_rejects_an_email_already_used_by_existing_account(self):
        User.objects.create_user(
            username="already-used@example.com",
            email="already-used@example.com",
            password="SecurePass123!",
        )
        response = self.client.post(
            reverse("jobseeker_signup"),
            {
                "firstName": "Second", "lastName": "Attempt",
                "email": "ALREADY-USED@example.com", "phone": "+1 555 123 4567",
                "password": "SecurePass123!", "confirmPassword": "SecurePass123!",
                "terms": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.filter(email__iexact="already-used@example.com").count(), 1)
        self.assertFalse(SignupRecord.objects.filter(email="already-used@example.com").exists())

    def test_employer_signup_creates_pending_company_and_profile(self):
        response = self.client.post(
            reverse("employer_signup"),
            {
                "firstName": "Morgan",
                "lastName": "Shah",
                "companyName": "Northstar Labs",
                "email": "morgan.shah@example.com",
                "phone": "+1 555 123 4567",
                "password": "SecurePass123!",
                "confirmPassword": "SecurePass123!",
                "terms": "on",
            },
        )

        user = User.objects.get(email="morgan.shah@example.com")
        self.assertRedirects(
            response,
            reverse("employer_pending"),
            fetch_redirect_response=False,
        )
        self.assertEqual(Profile.objects.get(user=user).role, "employer")
        company = Company.objects.get(owner=user)
        self.assertEqual(company.name, "Northstar Labs")
        self.assertFalse(company.is_approved)

    def test_login_accepts_email_password_credentials(self):
        user = User.objects.create_user(
            username="candidate-login@example.com",
            email="candidate-login@example.com",
            password="SecurePass123!",
        )
        response = self.client.post(
            reverse("login"),
            {
                "email": "CANDIDATE-LOGIN@example.com",
                "password": "SecurePass123!",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session["_auth_user_id"], str(user.pk))

    def test_logout_requires_post_and_clears_the_authenticated_session(self):
        user = User.objects.create_user(
            username="logout@example.com",
            email="logout@example.com",
            password="SecurePass123!",
        )
        self.client.force_login(user)

        get_response = self.client.get(reverse("logout"))
        self.assertEqual(get_response.status_code, 405)

        post_response = self.client.post(reverse("logout"))
        self.assertRedirects(post_response, reverse("home"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_accounts_login_redirects_to_google_only_login_page(self):
        response = self.client.get("/accounts/login/?next=%2Fsaved-jobs%2F")

        self.assertRedirects(
            response,
            "/login/?next=%2Fsaved-jobs%2F",
            fetch_redirect_response=False,
        )

    @override_settings(
        GOOGLE_OAUTH_CLIENT_ID="",
        GOOGLE_OAUTH_CLIENT_SECRET="",
    )
    def test_login_page_offers_google_and_email_password_sign_in(self):
        response = self.client.get(reverse("login_page"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign in securely with your email and password.")
        self.assertContains(response, "Google sign-in becomes available after OAuth setup.")
        self.assertContains(response, "Continue with Google")
        self.assertContains(response, 'data-oauth-provider="google"')
        self.assertContains(response, 'src="../js/authentication/google-oauth.js"')
        self.assertContains(response, 'name="password"')
        self.assertContains(response, 'name="email"')
        self.assertContains(response, "Forgot Password?")
        self.assertNotContains(response, "Microsoft")
        self.assertNotContains(response, "LinkedIn")

    def test_login_and_employer_signup_render_csrf_tokens(self):
        for route_name in ("login_page", "employer_signup_page"):
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'name="csrfmiddlewaretoken"')
                self.assertNotContains(response, "{% csrf_token %}")


class LandingPageTests(TestCase):
    def test_homepage_renders_landing_page(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AI-POWERED WORKFORCE PLATFORM")
        self.assertContains(response, 'id="welcome-intro"')

    def test_homepage_shows_database_counts_without_demo_or_unapproved_records(self):
        approved_company = Company.objects.create(name="Approved Co", is_approved=True)
        Company.objects.create(name="Pending Co", is_approved=False)
        Job.objects.create(company=approved_company, title="Live role", description="Role")
        Job.objects.create(
            company=approved_company,
            title="Demo role",
            description="Sample",
            is_demo=True,
        )
        Job.objects.create(
            company=approved_company,
            title="Closed role",
            description="Role",
            is_active=False,
        )
        candidate = User.objects.create_user(username="homepage-candidate", password="test-password")
        Profile.objects.create(user=candidate, full_name="Candidate", role="job_seeker")

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["active_job_count"], 1)
        self.assertEqual(response.context["approved_company_count"], 1)
        self.assertEqual(response.context["candidate_count"], 1)
        self.assertContains(response, "Open jobs")
        self.assertContains(response, "Approved companies")

    @override_settings(DEBUG=False)
    def test_not_found_page_does_not_show_django_debug_instructions(self):
        response = self.client.get("/route-that-does-not-exist/")

        self.assertEqual(response.status_code, 404)
        self.assertNotIn(
            b"You're seeing this error because",
            response.content,
        )

    def test_logo_and_stylesheet_are_served_with_debug_disabled(self):
        with override_settings(DEBUG=False):
            logo_response = self.client.get("/images/talentbridge-mark.svg")
            stylesheet_response = self.client.get("/css/base/redesign.css")
            favicon_response = self.client.get("/favicon.ico")

        self.assertEqual(logo_response.status_code, 200)
        self.assertEqual(stylesheet_response.status_code, 200)
        self.assertEqual(favicon_response.status_code, 200)
        self.assertIn("svg", favicon_response["Content-Type"])

    def test_jobs_route_keeps_job_search_page(self):
        response = self.client.get(reverse("jobs"), {"keyword": "designer"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Find work that fits.")
        self.assertContains(response, 'value="designer"')
        self.assertContains(response, f'action="{reverse("jobs")}"')
        self.assertContains(response, 'href="/">TalentBridge AI</a>')
        self.assertNotContains(response, 'href="/index.html"')
        self.assertNotContains(response, 'class="auth-btn auth-dashboard"')


class PageRoutingTests(TestCase):
    def test_generated_static_homepage_path_redirects_to_django_homepage(self):
        response = self.client.get("/site/index.html")

        self.assertRedirects(response, "/")

    def test_about_help_and_faq_use_live_routes_and_accurate_workflow_guidance(self):
        about = self.client.get(reverse("about"))
        self.assertEqual(about.status_code, 200)
        self.assertContains(about, 'class="tb-brand" href="/"')
        self.assertContains(about, 'href="/jobs/">Browse opportunities</a>')
        self.assertNotContains(about, 'href="/index.html"')

        help_page = self.client.get(reverse("help"))
        self.assertEqual(help_page.status_code, 200)
        self.assertContains(help_page, "Applications to real job listings are associated with your signed-in account.")
        self.assertContains(help_page, 'href="/privacy-settings/">Manage privacy settings</a>')
        self.assertNotContains(help_page, "The forms are previews.")

        faq = self.client.get(reverse("faq"))
        self.assertEqual(faq.status_code, 200)
        self.assertContains(faq, "A submitted application to a real listing is saved to your account")
        self.assertContains(faq, "The contact form records a support inquiry for the team.")
        self.assertContains(faq, "Recommended Jobs uses profile skills and location")

    def test_public_trust_pages_describe_current_backend_capabilities(self):
        trust = self.client.get(reverse("trust-center"))
        self.assertEqual(trust.status_code, 200)
        self.assertContains(trust, "No independent security certification or public status feed is claimed")
        self.assertContains(trust, "The contact form records a support inquiry in the application database.")

        status = self.client.get(reverse("platform-status"))
        self.assertEqual(status.status_code, 200)
        self.assertContains(status, "Eligible live listings are shown separately from labeled development samples.")
        self.assertContains(status, "Applications, profiles, and resumes</td><td>Account-backed")

        ai_audit = self.client.get(reverse("ai-audit-center"))
        self.assertEqual(ai_audit.status_code, 200)
        self.assertContains(ai_audit, "No AI provider is connected")
        self.assertContains(ai_audit, "Recommended Jobs ranks eligible roles using profile skills and location")

        terms = self.client.get(reverse("terms"))
        self.assertEqual(terms.status_code, 200)
        self.assertContains(terms, "Account-backed profiles, applications, resume uploads")
        self.assertNotContains(terms, "Forms for profiles, applications, resumes, contact")

    def test_category_links_filter_live_jobs_and_pricing_discloses_limits(self):
        company = Company.objects.create(name="Category Test Co", is_approved=True)
        technology_job = Job.objects.create(
            company=company,
            title="Technology Platform Engineer",
            description="Build platform services.",
        )
        Job.objects.create(
            company=company,
            title="Visual Designer",
            description="Create visual systems.",
        )

        categories = self.client.get(reverse("categories"))
        self.assertEqual(categories.status_code, 200)
        self.assertContains(categories, 'href="/jobs/?keyword=technology"')

        results = self.client.get(reverse("jobs"), {"keyword": "technology"})
        self.assertEqual(results.status_code, 200)
        self.assertEqual(
            list(results.context["jobs"].values_list("pk", flat=True)),
            [technology_job.pk],
        )

        pricing = self.client.get(reverse("pricing"))
        self.assertEqual(pricing.status_code, 200)
        self.assertContains(pricing, "Illustrative plans only")
        self.assertContains(pricing, "There is no billing/subscription system")
        self.assertContains(pricing, "AI matching is not available in this deployment")
        self.assertContains(pricing, "feature-unavailable")
        self.assertContains(pricing, 'href="/contact/" class="plan-button primary-button"')
        self.assertNotContains(pricing, "data-plan-purchase")
        self.assertNotContains(pricing, "support@worksetu.com")

    def test_privacy_and_cookie_pages_explain_backend_and_browser_storage(self):
        privacy = self.client.get(reverse("privacy"))
        self.assertEqual(privacy.status_code, 200)
        self.assertContains(privacy, "local Django database")
        self.assertContains(privacy, "private media")
        self.assertContains(privacy, "No AI provider is connected.")
        self.assertContains(privacy, "does not delete database records or uploaded resumes")
        self.assertNotContains(privacy, "static preview does not save those form submissions")

        cookies = self.client.get(reverse("cookie-preferences"))
        self.assertEqual(cookies.status_code, 200)
        self.assertContains(cookies, "No consent manager is configured")
        self.assertContains(cookies, "session and CSRF cookies")
        self.assertContains(cookies, "does not delete your server-side profile")

    def test_public_information_pages_have_working_named_routes(self):
        pages = {
            "ai-audit-center": "AI Audit Center",
            "blog": "Blog &amp; Insights",
            "careers": "Careers",
            "cookie-preferences": "Cookie Preferences",
            "customer-stories": "Customer Stories",
            "jobseaker": "For Job Seekers",
            "platform-status": "Platform Status",
            "remote-work-guide": "Remote Work Guide",
            "salary-calculator": "Salary Calculator",
            "trust-center": "Trust Center",
        }
        for slug, title in pages.items():
            with self.subTest(page=slug):
                response = self.client.get(reverse(slug))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, '<base href="/pages/">')
                self.assertContains(response, f"<title>{title} | TalentBridge AI</title>")

    def test_salary_calculator_computes_gross_pay_periods(self):
        response = self.client.post(
            reverse("salary-calculator"),
            {
                "annual_salary": "120000",
                "hours_per_week": "40",
                "weeks_per_year": "52",
                "currency": "USD",
            },
        )

        self.assertEqual(response.status_code, 200)
        results = response.context["results"]
        self.assertEqual(results["monthly"], Decimal("10000"))
        self.assertEqual(
            results["biweekly"].quantize(Decimal("0.01")),
            Decimal("4615.38"),
        )
        self.assertEqual(
            results["hourly"].quantize(Decimal("0.01")),
            Decimal("57.69"),
        )
        self.assertContains(response, "Gross-pay estimates before taxes, benefits")
        self.assertContains(response, "USD")

    def test_salary_calculator_rejects_invalid_salary_and_work_schedule(self):
        invalid_inputs = (
            {"annual_salary": "-1", "hours_per_week": "40", "weeks_per_year": "52", "currency": "USD"},
            {"annual_salary": "50000", "hours_per_week": "0", "weeks_per_year": "52", "currency": "USD"},
            {"annual_salary": "50000", "hours_per_week": "40", "weeks_per_year": "53", "currency": "USD"},
        )
        for data in invalid_inputs:
            with self.subTest(data=data):
                response = self.client.post(reverse("salary-calculator"), data)
                self.assertEqual(response.status_code, 200)
                self.assertIsNone(response.context["results"])
                self.assertContains(response, "Use a salary from 0 to")

    def test_access_denied_route_renders_recovery_links_with_forbidden_status(self):
        for path in (reverse("access-denied"), "/pages/access-denied.html"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 403)
                self.assertContains(response, "You do not have permission", status_code=403)
                self.assertContains(response, 'href="/login/"', status_code=403)

    def test_all_named_pages_render(self):
        for slug in PAGES:
            with self.subTest(page=slug):
                response = self.client.get(reverse(slug))

                self.assertIn(response.status_code, (200, 302, 403))
                if response.status_code == 200:
                    self.assertContains(response, '<base href="/pages/">')

    def test_all_physical_html_pages_render_without_template_syntax(self):
        pages_root = Path(getattr(settings, "FRONTEND_ROOT", settings.PROJECT_ROOT)) / "pages"
        for page in sorted(pages_root.rglob("*.html")):
            path = page.relative_to(pages_root).as_posix()
            with self.subTest(page=path):
                response = self.client.get(f"/pages/{path}")
                self.assertIn(response.status_code, (200, 302, 403))
                if response.status_code in (200, 403):
                    content = response.content.decode(response.charset or "utf-8")
                    self.assertNotRegex(content, r"\{%|{{")

    def test_physical_account_pages_render_account_backed_views(self):
        employer = User.objects.create_user(
            username="physical-page-employer",
            password="SecurePass123!",
        )
        seeker = User.objects.create_user(
            username="physical-page-seeker",
            password="SecurePass123!",
            first_name="Page",
            last_name="Candidate",
        )
        staff_user = User.objects.create_user(
            username="physical-page-admin",
            password="SecurePass123!",
            is_staff=True,
        )
        company = Company.objects.create(
            owner=employer,
            name="Physical Page Test Company",
            is_approved=True,
        )
        job = Job.objects.create(
            company=company,
            title="Account-backed test role",
            description="A test role used to verify account-backed page routing.",
        )
        application = Application.objects.create(job=job, applicant=seeker)
        SavedJob.objects.create(user=seeker, job=job)
        Notification.objects.create(
            user=seeker,
            title="Account-backed test notification",
            message="This notification belongs to the signed-in test account.",
        )
        Interview.objects.create(
            application=application,
            scheduled_at=timezone.now(),
            created_by=employer,
        )

        self.client.force_login(seeker)
        saved_jobs_response = self.client.get("/pages/saved-jobs.html")
        notifications_response = self.client.get("/pages/notifications.html")

        self.assertContains(saved_jobs_response, "Account-backed test role")
        self.assertContains(
            notifications_response,
            "Account-backed test notification",
        )

        self.client.force_login(employer)
        interviews_response = self.client.get("/pages/interviews.html")
        candidate_response = self.client.get(
            "/pages/candidate-details.html",
            {"application_id": application.pk},
        )

        self.assertContains(interviews_response, "Account-backed test role")
        self.assertContains(candidate_response, "Page Candidate")

        self.client.force_login(staff_user)
        admin_response = self.client.get("/pages/admin-dashboard.html")

        self.assertEqual(admin_response.status_code, 200)
        self.assertEqual(admin_response.context["user_count"], 3)

    @override_settings(DEBUG=True)
    def test_empty_job_listing_shows_filterable_demo_roles(self):
        response = self.client.get(reverse("jobs"))
        filtered = self.client.get(reverse("jobs"), {"keyword": "designer"})

        self.assertContains(response, "Illustrative example")
        self.assertContains(response, "Frontend Developer")
        self.assertContains(filtered, "UI/UX Designer")
        self.assertNotContains(filtered, "Frontend Developer")

    def test_sample_application_preview_renders_without_saving(self):
        response = self.client.get(
            "/pages/application-form.html",
            {"role": "frontend-developer"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sample application preview")
        self.assertContains(response, "This preview does not save or send your information.")
        self.assertContains(response, 'action="#"')

        submitted = self.client.post(
            "/pages/application-form.html?role=frontend-developer",
            {"confirm": "yes", "cover_note": "Sample preview only."},
        )

        self.assertEqual(submitted.status_code, 200)
        self.assertContains(submitted, "No application was sent or saved.")


class AccountSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="security@example.com",
            email="security@example.com",
            password="SecurePass123!",
        )

    def test_password_change_page_requires_authentication(self):
        response = self.client.get(reverse("account-security"))

        self.assertRedirects(
            response,
            "/login/?next=%2Faccount-security%2F",
            fetch_redirect_response=False,
        )

    def test_password_change_rejects_an_incorrect_current_password(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("account-security"),
            {
                "old_password": "IncorrectPassword123!",
                "new_password1": "AnotherSecurePass456!",
                "new_password2": "AnotherSecurePass456!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("old_password", response.context["form"].errors)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("SecurePass123!"))

    def test_password_change_updates_password_and_keeps_session_signed_in(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("account-security"),
            {
                "old_password": "SecurePass123!",
                "new_password1": "AnotherSecurePass456!",
                "new_password2": "AnotherSecurePass456!",
            },
        )

        self.assertRedirects(response, reverse("account-security"), fetch_redirect_response=False)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("AnotherSecurePass456!"))
        security_page = self.client.get(reverse("account-security"))
        self.assertEqual(security_page.status_code, 200)
        self.assertContains(security_page, "Your password has been updated.")


class JobWorkflowTests(TestCase):
    def setUp(self):
        self.employer = User.objects.create_user(
            username="employer@example.com",
            email="employer@example.com",
            password="SecurePass123!",
        )
        self.company = Company.objects.create(
            owner=self.employer,
            name="Bridge Labs",
            is_approved=True,
        )
        self.job = Job.objects.create(
            company=self.company,
            title="Product Designer",
            description="Design accessible product experiences for our customers.",
            location="Remote",
        )

    def test_candidate_search_finds_only_applicants_for_owned_live_jobs(self):
        matching_candidate = User.objects.create_user(
            username="candidate@example.com",
            email="candidate@example.com",
            password="SecurePass123!",
            first_name="Casey",
        )
        Profile.objects.create(
            user=matching_candidate,
            full_name="Casey Candidate",
            headline="Product designer",
            skills="Figma, Research",
            location="Bhopal",
        )
        Application.objects.create(job=self.job, applicant=matching_candidate)
        demo_job = Job.objects.create(
            company=self.company,
            title="Demo role",
            description="A clearly marked development sample.",
            is_demo=True,
        )
        demo_candidate = User.objects.create_user(
            username="demo-candidate@example.com",
            email="demo-candidate@example.com",
            password="SecurePass123!",
        )
        Application.objects.create(job=demo_job, applicant=demo_candidate)

        other_employer = User.objects.create_user(
            username="other-employer@example.com",
            email="other-employer@example.com",
            password="SecurePass123!",
        )
        other_company = Company.objects.create(
            owner=other_employer,
            name="Other Company",
            is_approved=True,
        )
        other_job = Job.objects.create(
            company=other_company,
            title="Other role",
            description="A role owned by another employer.",
        )
        other_candidate = User.objects.create_user(
            username="other-candidate@example.com",
            email="other-candidate@example.com",
            password="SecurePass123!",
        )
        Application.objects.create(job=other_job, applicant=other_candidate)

        self.client.force_login(self.employer)
        response = self.client.get(reverse("candidate-search"), {"q": "Research"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Casey Candidate")
        self.assertNotContains(response, "demo-candidate@example.com")
        self.assertNotContains(response, "other-candidate@example.com")
        self.assertEqual(response.context["page_obj"].paginator.count, 1)

    def test_profile_discovery_is_opt_in_and_never_exposes_contact_or_resume(self):
        seeker = User.objects.create_user(
            username="visible-candidate@example.com",
            email="visible-candidate@example.com",
            password="SecurePass123!",
        )
        visible_profile = Profile.objects.create(
            user=seeker,
            full_name="Jordan Discoverable",
            headline="Product researcher",
            skills="Research, Figma",
            experience="Five years",
            location="Bhopal",
            bio="Builds accessible product experiences.",
            phone="555-0104",
            resume="resumes/private-profile.pdf",
        )
        private_user = User.objects.create_user(
            username="private-candidate@example.com",
            email="private-candidate@example.com",
            password="SecurePass123!",
        )
        Profile.objects.create(
            user=private_user,
            full_name="Taylor Private",
            skills="Research",
        )

        self.assertFalse(visible_profile.is_discoverable)
        self.client.force_login(seeker)
        settings_response = self.client.get(reverse("privacy-settings"))
        self.assertEqual(settings_response.status_code, 200)
        self.assertContains(settings_response, "Allow approved employers to discover my profile")
        self.client.post(
            reverse("privacy-settings"),
            {"is_discoverable": "true"},
        )
        visible_profile.refresh_from_db()
        self.assertTrue(visible_profile.is_discoverable)

        self.client.force_login(self.employer)
        search_response = self.client.get(
            reverse("candidate-search"),
            {"q": "Research"},
        )
        self.assertContains(search_response, "Jordan Discoverable")
        self.assertContains(search_response, "Product researcher")
        self.assertNotContains(search_response, "Taylor Private")
        self.assertNotContains(search_response, "visible-candidate@example.com")
        self.assertNotContains(search_response, "555-0104")
        self.assertNotContains(search_response, "private-profile.pdf")

        self.client.force_login(seeker)
        self.client.post(reverse("privacy-settings"), {})
        visible_profile.refresh_from_db()
        self.assertFalse(visible_profile.is_discoverable)
        self.client.force_login(self.employer)
        search_response = self.client.get(reverse("candidate-search"))
        self.assertNotContains(search_response, "Jordan Discoverable")

    def test_profile_discovery_settings_are_job_seeker_only_and_authenticated(self):
        anonymous_response = self.client.get(reverse("privacy-settings"))
        self.assertRedirects(
            anonymous_response,
            "/login/?next=%2Fprivacy-settings%2F",
            fetch_redirect_response=False,
        )

        self.client.force_login(self.employer)
        for path in (reverse("privacy-settings"), reverse("get-discovered"), "/pages/privacy-settings.html"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertRedirects(
                    response,
                    reverse("dashboard"),
                    fetch_redirect_response=False,
                )

    def test_candidate_search_requires_an_approved_employer_and_supports_physical_route(self):
        self.client.force_login(self.employer)
        self.assertEqual(self.client.get("/pages/candidate-search.html").status_code, 200)

        unapproved = User.objects.create_user(
            username="pending-employer@example.com",
            email="pending-employer@example.com",
            password="SecurePass123!",
        )
        Company.objects.create(
            owner=unapproved,
            name="Pending Company",
            is_approved=False,
        )
        self.client.force_login(unapproved)
        self.assertEqual(self.client.get(reverse("candidate-search")).status_code, 404)

        seeker = User.objects.create_user(
            username="seeker@example.com",
            email="seeker@example.com",
            password="SecurePass123!",
        )
        self.client.force_login(seeker)
        self.assertEqual(self.client.get(reverse("candidate-search")).status_code, 404)

        self.client.logout()
        response = self.client.get(reverse("candidate-search"))
        self.assertRedirects(
            response,
            "/login/?next=%2Fcandidate-search%2F",
            fetch_redirect_response=False,
        )

    @override_settings(DEBUG=True)
    def test_remote_and_startup_job_pages_filter_real_jobs_and_label_demo_fallbacks(self):
        remote_samples = self.client.get(reverse("remote-jobs"))
        startup_samples = self.client.get(reverse("startup-jobs"))

        self.assertContains(remote_samples, "Remote jobs")
        self.assertContains(remote_samples, "Frontend Developer")
        self.assertNotContains(remote_samples, "UI/UX Designer")
        self.assertContains(startup_samples, "Startup jobs")
        self.assertContains(startup_samples, "Software Engineer Intern")
        self.assertNotContains(startup_samples, "Product Designer")
        self.assertContains(startup_samples, "Illustrative example")

        remote_job = Job.objects.create(
            company=self.company,
            title="Remote Support Engineer",
            description="Support a distributed product team across regions.",
            work_mode="Remote",
        )
        startup_company = Company.objects.create(
            owner=User.objects.create_user(
                username="startup@example.com",
                email="startup@example.com",
                password="SecurePass123!",
            ),
            name="Acorn Labs",
            industry="Technology startup",
            is_approved=True,
        )
        startup_job = Job.objects.create(
            company=startup_company,
            title="Startup Operations Analyst",
            description="Help a growing early-stage company improve its processes.",
        )

        remote_live = self.client.get(reverse("remote-jobs"))
        startup_live = self.client.get(reverse("startup-jobs"))

        self.assertContains(remote_live, remote_job.title)
        self.assertNotContains(remote_live, self.job.title)
        self.assertNotContains(remote_live, "Illustrative example")
        self.assertContains(startup_live, startup_job.title)
        self.assertNotContains(startup_live, self.job.title)
        self.assertNotContains(startup_live, "Illustrative example")

    def test_job_listing_and_detail_use_database_records(self):
        listing = self.client.get(reverse("jobs"), {"keyword": "Designer"})
        detail = self.client.get(reverse("job_detail", args=(self.job.pk,)))

        self.assertContains(listing, "Product Designer")
        self.assertContains(detail, "Bridge Labs")
        self.assertContains(detail, reverse("apply_job", args=(self.job.pk,)))

    def test_job_search_applies_all_filters_and_relevance_order(self):
        exact = Job.objects.create(
            company=self.company,
            title="Data",
            description="Build data products for customers.",
            location="Remote",
            skills="Python, SQL",
            experience="3+ years",
            job_type="Contract",
            work_mode="Hybrid",
        )
        partial = Job.objects.create(
            company=self.company,
            title="Data Analyst",
            description="Analyze product data.",
            location="Remote",
            skills="Python",
            experience="3+ years",
            job_type="Contract",
            work_mode="Hybrid",
        )

        response = self.client.get(
            reverse("jobs"),
            {
                "title": "Data",
                "company": "Bridge Labs",
                "location": "Remote",
                "skills": "Python",
                "experience": "3+",
                "job_type": "Contract",
                "work_mode": "Hybrid",
                "sort": "relevant",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].paginator.count, 2)
        self.assertEqual(list(response.context["jobs"]), [exact, partial])
        self.assertContains(response, 'name="job_type"')
        self.assertContains(response, "Clear filters")

    def test_job_search_paginates_and_preserves_filters(self):
        for index in range(13):
            Job.objects.create(
                company=self.company,
                title=f"Engineer {index}",
                description="Build reliable software for customer teams.",
            )

        response = self.client.get(
            reverse("jobs"),
            {"title": "Engineer", "company": "Bridge", "page": "2"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].paginator.count, 13)
        self.assertEqual(len(response.context["jobs"]), 1)
        self.assertIn("title=Engineer", response.context["previous_page_url"])
        self.assertContains(response, "Page 2 of 2")

    def test_employer_can_edit_own_job(self):
        self.client.force_login(self.employer)

        page = self.client.get(f"/jobs/{self.job.pk}/edit/")
        response = self.client.post(
            f"/jobs/{self.job.pk}/edit/",
            {
                "jobTitle": "Updated Product Designer",
                "description": "Design accessible product experiences with customer research.",
                "location": "Hybrid Bhopal",
                "skills": "Figma, Research",
                "employmentType": "Contract",
                "workMode": "Hybrid",
                "salary": "₹6–9 LPA",
                "experience": "3+ years",
            },
        )

        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Edit job posting")
        self.assertRedirects(response, reverse("manage-jobs"), fetch_redirect_response=False)
        self.job.refresh_from_db()
        self.assertEqual(self.job.title, "Updated Product Designer")
        self.assertEqual(self.job.job_type, "Contract")
        self.assertEqual(self.job.skills, "Figma, Research")
        self.assertEqual(self.job.requirements, "Figma, Research")

    def test_employer_cannot_edit_another_company_or_demo_job(self):
        other_employer = User.objects.create_user(
            username="other-employer@example.com",
            email="other-employer@example.com",
            password="SecurePass123!",
        )
        other_company = Company.objects.create(
            owner=other_employer,
            name="Other Company",
            is_approved=True,
        )
        other_job = Job.objects.create(
            company=other_company,
            title="Other employer role",
            description="A role owned by a different employer.",
        )
        demo_job = Job.objects.create(
            company=self.company,
            title="Sample role",
            description="A demo role cannot be edited as a real vacancy.",
            is_demo=True,
        )
        self.client.force_login(self.employer)

        self.assertEqual(self.client.get(f"/jobs/{other_job.pk}/edit/").status_code, 404)
        self.assertEqual(self.client.get(f"/jobs/{demo_job.pk}/edit/").status_code, 404)

    def test_invalid_job_edit_keeps_saved_values_and_shows_errors(self):
        self.client.force_login(self.employer)

        response = self.client.post(
            f"/jobs/{self.job.pk}/edit/",
            {
                "jobTitle": "Changed title",
                "description": "Too short",
                "location": "Remote",
                "skills": "Python",
                "employmentType": "Full-time",
                "workMode": "Remote",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "at least 30 characters")
        self.job.refresh_from_db()
        self.assertEqual(self.job.title, "Product Designer")

    def test_recommended_jobs_requires_login(self):
        response = self.client.get("/recommended-jobs/")

        self.assertRedirects(
            response,
            "/login/?next=%2Frecommended-jobs%2F",
            fetch_redirect_response=False,
        )

    def test_recommended_jobs_rank_profile_matches_and_exclude_applied_jobs(self):
        applicant = User.objects.create_user(
            username="recommendations@example.com",
            email="recommendations@example.com",
            password="SecurePass123!",
        )
        Profile.objects.create(
            user=applicant,
            full_name="Recommended Candidate",
            skills="Python, APIs",
            location="Remote",
        )
        matching_job = Job.objects.create(
            company=self.company,
            title="Python API Engineer",
            description="Build remote APIs with Python.",
            skills="Python, APIs",
            location="Remote",
        )
        skill_match = Job.objects.create(
            company=self.company,
            title="Python Analyst",
            description="Analyze product data.",
            skills="Python",
            location="Bhopal",
        )
        applied_job = Job.objects.create(
            company=self.company,
            title="Applied Python Role",
            description="A role already applied to.",
            skills="Python, APIs",
            location="Remote",
        )
        demo_job = Job.objects.create(
            company=self.company,
            title="Demo Python Role",
            description="A sample listing, not a live vacancy.",
            skills="Python",
            is_demo=True,
        )
        Application.objects.create(job=applied_job, applicant=applicant)
        self.client.force_login(applicant)

        response = self.client.get("/recommended-jobs/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["job"].pk for item in response.context["recommendations"]],
            [matching_job.pk, skill_match.pk, self.job.pk],
        )
        self.assertNotContains(response, "Applied Python Role")
        self.assertNotContains(response, demo_job.title)

    def test_recommendations_explain_profile_matches_and_filter_preferences(self):
        applicant = User.objects.create_user(
            username="match-explanation@example.com",
            email="match-explanation@example.com",
            password="SecurePass123!",
        )
        Profile.objects.create(
            user=applicant,
            full_name="Match Candidate",
            skills="Python, SQL",
            location="Remote",
            experience="4 years",
        )
        matching_job = Job.objects.create(
            company=self.company,
            title="Python Data Engineer",
            description="Build data services with Python and SQL.",
            skills="Python, SQL",
            requirements="Python, SQL",
            experience="3-5 years",
            location="Remote",
            job_type="Contract",
            work_mode="Remote",
        )
        other_mode = Job.objects.create(
            company=self.company,
            title="Python Data Analyst",
            description="Analyze Python data.",
            skills="Python",
            experience="3+ years",
            location="Remote",
            job_type="Full-time",
            work_mode="Hybrid",
        )
        self.client.force_login(applicant)

        response = self.client.get(
            reverse("recommended-jobs"),
            {"job_type": "Contract", "work_mode": "Remote"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["job"].pk for item in response.context["recommendations"]],
            [matching_job.pk],
        )
        item = response.context["recommendations"][0]
        self.assertEqual(item["matched_skills"], ["Python", "SQL"])
        self.assertTrue(item["experience_match"])
        self.assertIn("Your listed experience fits the stated requirement", item["reasons"])
        self.assertContains(response, "transparent rule-based match")
        self.assertNotContains(response, other_mode.title)

    @override_settings(DEBUG=True)
    def test_empty_recommendations_show_labelled_samples_without_saving_jobs(self):
        applicant = User.objects.create_user(
            username="sample-recommendations@example.com",
            email="sample-recommendations@example.com",
            password="SecurePass123!",
        )
        Profile.objects.create(
            user=applicant,
            full_name="Sample Candidate",
            skills="Python",
            location="Remote",
        )
        self.job.is_active = False
        self.job.save(update_fields=("is_active",))
        self.client.force_login(applicant)

        response = self.client.get("/recommended-jobs/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Illustrative example")
        self.assertContains(response, "Software Engineer Intern")
        self.assertFalse(Job.objects.filter(title="Software Engineer Intern").exists())

    @override_settings(DEBUG=True)
    def test_demo_job_is_labeled_and_cannot_accept_applications(self):
        demo_job = Job.objects.create(
            company=self.company,
            title="Demo Data Analyst",
            description="A sample listing used to demonstrate the job workflow.",
            is_demo=True,
        )
        listing = self.client.get(reverse("jobs"), {"keyword": "Demo Data Analyst"})
        detail = self.client.get(reverse("job_detail", args=(demo_job.pk,)))
        applicant = User.objects.create_user(
            username="demo-test-candidate@example.com",
            email="demo-test-candidate@example.com",
            password="test-password-123",
        )
        self.client.force_login(applicant)
        application_response = self.client.post(
            reverse("apply_job", args=(demo_job.pk,)),
            {"confirm": "yes", "cover_note": "Should not be saved."},
        )

        self.assertContains(listing, "Illustrative example")
        self.assertContains(detail, "Applications are disabled")
        self.assertNotContains(detail, reverse("apply_job", args=(demo_job.pk,)))
        self.assertEqual(application_response.status_code, 404)
        self.assertFalse(Application.objects.filter(job=demo_job, applicant=applicant).exists())

    def test_job_application_is_saved_once_for_signed_in_applicant(self):
        applicant = User.objects.create_user(
            username="candidate@example.com",
            email="candidate@example.com",
            password="SecurePass123!",
        )
        self.client.force_login(applicant)
        form_url = reverse("apply_job", args=(self.job.pk,))

        self.assertEqual(self.client.get(form_url).status_code, 200)
        response = self.client.post(form_url, {"confirm": "yes", "cover_note": "I am interested."})
        duplicate = self.client.post(form_url, {"confirm": "yes", "cover_note": "Another note."})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(duplicate.status_code, 302)
        self.assertEqual(Application.objects.filter(job=self.job, applicant=applicant).count(), 1)
        self.assertEqual(
            Notification.objects.filter(user=self.employer, title="New job application").count(),
            1,
        )
        self.assertEqual(
            Application.objects.get(job=self.job, applicant=applicant).status,
            "applied",
        )

    def test_profile_changes_are_saved_to_the_signed_in_account(self):
        self.client.force_login(self.employer)

        response = self.client.post(
            reverse("edit-profile"),
            {
                "full_name": "Jordan Lee",
                "email": "jordan@example.com",
                "location": "Pune",
                "headline": "Product designer",
                "experience": "5 years",
                "skills": "Research, prototyping",
                "education": "B.Des, Interaction Design",
                "description": "Designing helpful products.",
            },
        )

        self.assertRedirects(response, reverse("profile"), fetch_redirect_response=False)
        self.employer.refresh_from_db()
        self.assertEqual(self.employer.email, "jordan@example.com")
        profile = Profile.objects.get(user=self.employer)
        self.assertEqual(profile.headline, "Product designer")
        self.assertEqual(
            ResumeDraft.objects.get(user=self.employer).content["education"],
            "B.Des, Interaction Design",
        )
        profile_page = self.client.get(reverse("profile"))
        self.assertContains(profile_page, "B.Des, Interaction Design")

    def test_only_approved_employers_can_publish_jobs(self):
        self.company.is_approved = False
        self.company.save(update_fields=("is_approved",))
        self.client.force_login(self.employer)

        response = self.client.post(
            reverse("create_job"),
            {
                "jobTitle": "Backend Engineer",
                "description": "Build and maintain reliable server-side product features.",
                "location": "Bengaluru",
                "employmentType": "Full-time",
                "workMode": "Hybrid",
            },
        )

        self.assertRedirects(response, reverse("employer_pending"), fetch_redirect_response=False)
        self.assertFalse(Job.objects.filter(title="Backend Engineer").exists())


class ResumeWorkflowTests(TestCase):
    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.media_dir.cleanup)
        media_settings = override_settings(MEDIA_ROOT=self.media_dir.name)
        media_settings.enable()
        self.addCleanup(media_settings.disable)
        self.candidate = User.objects.create_user(
            username="resume-candidate@example.com",
            email="resume-candidate@example.com",
            password="SecurePass123!",
        )
        self.profile = Profile.objects.create(
            user=self.candidate,
            full_name="Resume Candidate",
            role="job_seeker",
        )

    def test_resume_upload_replaces_previous_file_and_rejects_mismatched_contents(self):
        self.client.force_login(self.candidate)
        first_upload = SimpleUploadedFile(
            "resume.pdf",
            b"%PDF-1.4\nfirst resume",
            content_type="application/pdf",
        )
        first_response = self.client.post(
            reverse("resume-management"),
            {"resume": first_upload},
            follow=True,
        )
        self.assertEqual(first_response.status_code, 200)
        self.profile.refresh_from_db()
        first_name = self.profile.resume.name
        first_path = self.profile.resume.path
        self.assertTrue(Path(first_path).is_file())

        replacement = SimpleUploadedFile(
            "resume.pdf",
            b"%PDF-1.4\nreplacement resume",
            content_type="application/pdf",
        )
        replacement_response = self.client.post(
            reverse("resume-management"),
            {"resume": replacement},
            follow=True,
        )
        self.assertEqual(replacement_response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertNotEqual(self.profile.resume.name, first_name)
        self.assertFalse(Path(first_path).exists())
        self.assertTrue(Path(self.profile.resume.path).is_file())
        replacement_path = self.profile.resume.path

        invalid_upload = SimpleUploadedFile(
            "invalid.pdf",
            b"not a PDF document",
            content_type="application/pdf",
        )
        invalid_response = self.client.post(
            reverse("resume-management"),
            {"resume": invalid_upload},
        )
        self.assertEqual(invalid_response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertTrue(Path(self.profile.resume.path).is_file())

        deleted = self.client.post(reverse("resume_delete"))
        self.assertEqual(deleted.status_code, 302)
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.resume)
        self.assertFalse(Path(replacement_path).exists())

    def test_resume_download_is_limited_to_owner_or_applicant_employer(self):
        self.profile.resume.save(
            "private-resume.pdf",
            ContentFile(b"%PDF-1.4\nprivate resume"),
            save=True,
        )
        self.client.force_login(self.candidate)
        own_download = self.client.get(reverse("resume_download"))
        self.assertEqual(own_download.status_code, 200)
        self.assertEqual(b"".join(own_download.streaming_content), b"%PDF-1.4\nprivate resume")

        unrelated_user = User.objects.create_user(
            username="unrelated-resume-user@example.com",
            email="unrelated-resume-user@example.com",
            password="SecurePass123!",
        )
        self.client.force_login(unrelated_user)
        self.assertEqual(self.client.get(reverse("resume_download")).status_code, 404)
        self.assertEqual(self.client.get(f"/media/{self.profile.resume.name}").status_code, 404)

        employer = User.objects.create_user(
            username="resume-employer@example.com",
            email="resume-employer@example.com",
            password="SecurePass123!",
        )
        company = Company.objects.create(
            owner=employer,
            name="Resume Review Company",
            is_approved=True,
        )
        job = Job.objects.create(
            company=company,
            title="Resume Reviewer",
            description="A role with an applicant-owned resume.",
        )
        application = Application.objects.create(job=job, applicant=self.candidate)
        self.client.force_login(employer)
        employer_download = self.client.get(
            reverse("resume_download"),
            {"application_id": application.pk},
        )
        self.assertEqual(employer_download.status_code, 200)
        self.assertEqual(
            b"".join(employer_download.streaming_content),
            b"%PDF-1.4\nprivate resume",
        )

        other_employer = User.objects.create_user(
            username="other-resume-employer@example.com",
            email="other-resume-employer@example.com",
            password="SecurePass123!",
        )
        self.client.force_login(other_employer)
        unauthorized = self.client.get(
            reverse("resume_download"),
            {"application_id": application.pk},
        )
        self.assertEqual(unauthorized.status_code, 404)


class ContactWorkflowTests(TestCase):
    def test_contact_form_records_valid_message(self):
        response = self.client.post(
            reverse("contact_submit"),
            {
                "name": "Taylor",
                "email": "taylor@example.com",
                "topic": "General question",
                "message": "I would like to know more about the platform.",
            },
        )

        self.assertRedirects(response, reverse("contact"), fetch_redirect_response=False)
        self.assertEqual(ContactInquiry.objects.count(), 1)

    def test_contact_page_posts_to_the_recording_endpoint(self):
        response = self.client.get(reverse("contact"))

        self.assertContains(response, f'action="{reverse("contact_submit")}"')
        self.assertNotContains(response, "does not transmit or store")


class DemoDataCommandTests(TestCase):
    def test_seed_command_creates_five_idempotent_rows_per_domain_table(self):
        existing = User.objects.create_user(
            username="existing-account",
            email="existing-account@example.com",
            password="test-password-123",
        )
        output = StringIO()

        call_command("seed_demo_data", stdout=output)
        call_command("seed_demo_data", stdout=output)

        self.assertEqual(User.objects.filter(username__startswith="demo-user-").count(), 5)
        self.assertEqual(Profile.objects.filter(full_name__startswith="Demo User ").count(), 5)
        self.assertEqual(Company.objects.filter(name__startswith="Demo ").count(), 5)
        self.assertEqual(Job.objects.filter(is_demo=True).count(), 5)
        self.assertEqual(Application.objects.filter(job__is_demo=True).count(), 5)
        self.assertEqual(ContactInquiry.objects.filter(email__startswith="demo-contact-").count(), 5)
        self.assertEqual(SavedJob.objects.filter(job__is_demo=True).count(), 5)
        self.assertEqual(Notification.objects.filter(title__startswith="[DEMO]").count(), 5)
        self.assertEqual(Interview.objects.filter(application__job__is_demo=True).count(), 5)
        self.assertFalse(
            User.objects.filter(username__startswith="demo-user-").filter(is_active=True).exists()
        )
        self.assertFalse(
            any(user.has_usable_password() for user in User.objects.filter(username__startswith="demo-user-"))
        )
        self.assertTrue(User.objects.filter(pk=existing.pk).exists())
        self.assertIn("interviews=5", output.getvalue())


class PasswordResetWorkflowTests(TestCase):
    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    )
    def test_password_reset_sends_signed_reset_link(self):
        user = User.objects.create_user(
            username="reset@example.com",
            email="reset@example.com",
            password="SecurePass123!",
        )

        response = self.client.post(
            reverse("forgot-password"),
            {"email": "reset@example.com"},
        )

        self.assertRedirects(response, reverse("password-reset"), fetch_redirect_response=False)
        self.assertEqual(len(mail.outbox), 1)
        reset_path = re.search(
            r"/password-reset/[^/\s]+/[^/\s]+/",
            mail.outbox[0].body,
        ).group(0)

        reset_page = self.client.get(reset_path, follow=True)
        self.assertEqual(reset_page.status_code, 200)
        self.assertContains(reset_page, "Choose a new password")
        self.assertContains(reset_page, "name=\"new_password1\"")
        confirm_path = reset_page.request["PATH_INFO"]

        completed = self.client.post(
            confirm_path,
            {
                "new_password1": "NewSecurePass123!",
                "new_password2": "NewSecurePass123!",
            },
        )
        self.assertRedirects(
            completed,
            reverse("password-reset-complete"),
            fetch_redirect_response=False,
        )
        user.refresh_from_db()
        self.assertTrue(user.check_password("NewSecurePass123!"))

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    )
    def test_password_reset_does_not_disclose_unknown_email(self):
        response = self.client.post(
            reverse("forgot-password"),
            {"email": "unknown@example.com"},
        )

        self.assertRedirects(response, reverse("password-reset"), fetch_redirect_response=False)
        self.assertEqual(len(mail.outbox), 0)


class ConnectedDatabaseFeatureTests(TestCase):
    def setUp(self):
        self.employer = User.objects.create_user(
            username="employer@example.com", email="employer@example.com",
            password="SecurePass123!", first_name="Eli",
        )
        Profile.objects.create(user=self.employer, full_name="Eli Employer", role="employer")
        self.company = Company.objects.create(
            owner=self.employer, name="Example Company", is_approved=True
        )
        self.job = Job.objects.create(
            company=self.company, title="Python Developer",
            description="Build and maintain reliable web applications.",
            location="Remote", skills="Python, Django",
        )
        self.candidate = User.objects.create_user(
            username="candidate@example.com", email="candidate@example.com",
            password="SecurePass123!", first_name="Casey",
        )
        Profile.objects.create(user=self.candidate, full_name="Casey Candidate", role="job_seeker")
        self.application = Application.objects.create(job=self.job, applicant=self.candidate)

    def test_saved_job_page_and_toggle_persist(self):
        self.client.force_login(self.candidate)
        response = self.client.post(
            reverse("toggle-saved-job", args=(self.job.pk,)),
            {"next": reverse("saved-jobs")},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SavedJob.objects.filter(user=self.candidate, job=self.job).exists())
        response = self.client.get(reverse("saved-jobs"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Developer")
        self.assertNotContains(response, "Frontend Developer")
        self.assertContains(response, 'href="/dashboard/"')

    def test_demo_jobs_never_enter_account_saved_jobs(self):
        demo_job = Job.objects.create(
            company=self.company,
            title="Demo-only saved role",
            description="This sample must stay separate from account records.",
            is_demo=True,
        )
        self.client.force_login(self.candidate)

        rejected = self.client.post(
            reverse("toggle-saved-job", args=(demo_job.pk,)),
        )
        self.assertEqual(rejected.status_code, 404)
        self.assertFalse(
            SavedJob.objects.filter(user=self.candidate, job=demo_job).exists()
        )

        SavedJob.objects.create(user=self.candidate, job=demo_job)
        response = self.client.get(reverse("saved-jobs"))
        self.assertNotContains(response, "Demo-only saved role")

    def test_employer_can_update_only_own_application(self):
        self.client.force_login(self.employer)
        response = self.client.post(
            reverse("update-application-status", args=(self.application.pk,)),
            {"status": "under_review"},
        )
        self.assertEqual(response.status_code, 302)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, "under_review")
        status_notifications = Notification.objects.filter(
            user=self.candidate,
            title="Application status updated",
        )
        self.assertEqual(status_notifications.count(), 1)
        self.assertIn(f"application_id={self.application.pk}", status_notifications.first().target_url)

        self.client.post(
            reverse("update-application-status", args=(self.application.pk,)),
            {"status": "under_review"},
        )
        self.assertEqual(status_notifications.count(), 1)

        self.client.post(
            reverse("update-application-status", args=(self.application.pk,)),
            {"status": "shortlisted"},
        )
        self.assertEqual(status_notifications.count(), 2)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, "shortlisted")
        events = ApplicationStatusEvent.objects.filter(application=self.application).order_by("created_at")
        self.assertEqual(list(events.values_list("to_status", flat=True)), ["under_review", "shortlisted"])
        self.assertEqual(events.first().changed_by_id, self.employer.id)

        self.client.force_login(self.candidate)
        history = self.client.get(reverse("notifications"))
        self.assertContains(history, "Under Review")
        self.assertContains(history, "Shortlisted")
        self.assertContains(history, "Your notifications")
        self.assertContains(history, "Application status updated")
        # Labelled sample feed may still appear above the live panel; do not treat it as failure.
        unread_filter = self.client.get(reverse("notifications"), {"unread": "1"})
        self.assertEqual(unread_filter.status_code, 200)
        category_filter = self.client.get(reverse("notifications"), {"category": "application"})
        self.assertContains(category_filter, "Application status updated")
        application_history = self.client.get(
            reverse("applied-jobs"),
            {"application_id": self.application.pk},
        )
        self.assertContains(application_history, "Shortlisted")
        self.assertContains(application_history, "Your job applications")
        # Labelled example tracker may remain above the live applications panel.

    def test_application_history_remains_visible_after_job_is_closed(self):
        self.application.job.is_active = False
        self.application.job.save(update_fields=("is_active",))
        self.client.force_login(self.candidate)

        response = self.client.get(reverse("applied-jobs"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.job.title)

    def test_candidate_education_is_visible_only_to_the_applicant_employer(self):
        ResumeDraft.objects.create(
            user=self.candidate,
            content={"education": "B.Des, Interaction Design"},
        )
        self.client.force_login(self.employer)

        authorized = self.client.get(
            reverse("candidate-details"),
            {"application_id": self.application.pk},
        )

        self.assertEqual(authorized.status_code, 200)
        self.assertContains(authorized, "B.Des, Interaction Design")
        self.assertContains(authorized, "Authorized application details")

        other_employer = User.objects.create_user(
            username="other-education-employer@example.com",
            email="other-education-employer@example.com",
            password="SecurePass123!",
        )
        self.client.force_login(other_employer)
        unauthorized = self.client.get(
            reverse("candidate-details"),
            {"application_id": self.application.pk},
        )
        self.assertEqual(unauthorized.status_code, 404)

    def test_invalid_notification_id_does_not_mark_everything_read(self):
        notification = Notification.objects.create(
            user=self.candidate,
            title="Keep unread",
            message="This should remain unread.",
        )
        self.client.force_login(self.candidate)

        response = self.client.post(
            reverse("notifications"),
            {"notification_id": "not-a-number"},
        )

        self.assertEqual(response.status_code, 302)
        notification.refresh_from_db()
        self.assertFalse(notification.is_read)

    def test_non_staff_cannot_access_admin_dashboard(self):
        self.client.force_login(self.candidate)
        response = self.client.get(reverse("admin-dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(username="unrelated-admin").exists())

    def test_staff_admin_dashboard_uses_live_counts_and_admin_routes(self):
        staff_user = User.objects.create_superuser(
            username="platform-admin@example.com",
            email="platform-admin@example.com",
            password="SecurePass123!",
        )
        pending_company = Company.objects.create(
            name="Pending Review Labs",
            is_approved=False,
        )
        Job.objects.create(
            company=self.company,
            title="Demo-only posting",
            description="This sample must not be counted as a live job.",
            is_demo=True,
        )
        inquiry = ContactInquiry.objects.create(
            name="Support Requester",
            email="support@example.com",
            topic="General question",
            message="Please review this account support question.",
        )
        self.client.force_login(staff_user)

        response = self.client.get(reverse("admin-dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["user_count"], 3)
        self.assertEqual(response.context["company_count"], 2)
        self.assertEqual(response.context["pending_company_count"], 1)
        self.assertEqual(response.context["job_count"], 1)
        self.assertEqual(response.context["demo_job_count"], 1)
        self.assertEqual(response.context["application_count"], 1)
        self.assertEqual(response.context["contact_inquiries"][0], inquiry)
        self.assertContains(response, pending_company.name)
        self.assertContains(response, reverse("admin:auth_user_changelist"))
        self.assertContains(response, reverse("admin:jobs_company_changelist"))
        self.assertContains(response, reverse("admin:jobs_job_changelist"))
        self.assertContains(response, reverse("admin:jobs_profile_changelist"))
        self.assertContains(response, reverse("admin:jobs_application_changelist"))
        self.assertContains(response, reverse("admin:jobs_savedjob_changelist"))
        self.assertContains(response, reverse("admin:jobs_notification_changelist"))
        self.assertContains(response, reverse("admin:jobs_interview_changelist"))
        self.assertContains(response, reverse("admin:jobs_contactinquiry_changelist"))
        self.assertNotContains(response, "Fictional reviews pending")
        for route_name in (
            "admin:auth_user_changelist",
            "admin:jobs_profile_changelist",
            "admin:jobs_company_changelist",
            "admin:jobs_job_changelist",
            "admin:jobs_application_changelist",
            "admin:jobs_savedjob_changelist",
            "admin:jobs_notification_changelist",
            "admin:jobs_interview_changelist",
            "admin:jobs_contactinquiry_changelist",
        ):
            with self.subTest(route_name=route_name):
                self.assertEqual(self.client.get(reverse(route_name)).status_code, 200)

    def test_staff_without_company_change_permission_cannot_approve_employer(self):
        staff_user = User.objects.create_user(
            username="limited-staff@example.com",
            password="SecurePass123!",
            is_staff=True,
        )
        pending_company = Company.objects.create(
            name="Permission Review Labs",
            is_approved=False,
        )
        self.client.force_login(staff_user)

        dashboard = self.client.get(reverse("admin-dashboard"))
        self.assertEqual(dashboard.status_code, 200)
        self.assertNotContains(dashboard, pending_company.name)
        self.assertNotContains(dashboard, "Approve employer")

        approval = self.client.post(
            reverse("approve-company", args=(pending_company.pk,)),
        )
        self.assertEqual(approval.status_code, 403)
        pending_company.refresh_from_db()
        self.assertFalse(pending_company.is_approved)

    def test_employer_can_schedule_interview_for_own_application(self):
        self.client.force_login(self.employer)
        from django.utils import timezone
        from datetime import timedelta
        future = (timezone.now() + timedelta(days=2)).replace(microsecond=0).isoformat()
        response = self.client.post(
            reverse("interviews"),
            {
                "application_id": str(self.application.pk),
                "scheduled_at": future,
                "location_or_link": "https://meet.example.com/interview",
                "notes": "Technical discussion",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Interview.objects.filter(application=self.application).exists())
        self.assertEqual(
            Notification.objects.filter(user=self.candidate, title="Interview scheduled").count(),
            1,
        )
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, "interview_scheduled")

        self.client.post(
            reverse("interviews"),
            {
                "application_id": str(self.application.pk),
                "scheduled_at": future,
                "location_or_link": "https://meet.example.com/interview",
                "notes": "Technical discussion",
            },
        )
        self.assertEqual(Interview.objects.filter(application=self.application).count(), 1)
        self.assertEqual(
            Notification.objects.filter(user=self.candidate, title="Interview scheduled").count(),
            1,
        )

        interview = Interview.objects.get(application=self.application)
        updated = self.client.post(
            reverse("update-interview-status", args=(interview.pk,)),
            {"status": "completed"},
        )
        self.assertEqual(
            Notification.objects.filter(
                user=self.candidate,
                title="Interview status updated",
            ).count(),
            1,
        )
        self.assertEqual(updated.status_code, 302)
        interview.refresh_from_db()
        self.assertEqual(interview.status, "completed")
        self.client.post(
            reverse("update-interview-status", args=(interview.pk,)),
            {"status": "completed"},
        )
        self.assertEqual(
            Notification.objects.filter(
                user=self.candidate,
                title="Interview status updated",
            ).count(),
            1,
        )

    def test_interview_status_update_is_limited_to_own_company(self):
        interview = Interview.objects.create(
            application=self.application,
            scheduled_at=timezone.now() + timedelta(days=2),
            created_by=self.employer,
        )
        other_employer = User.objects.create_user(
            username="other-interview-employer@example.com",
            email="other-interview-employer@example.com",
            password="SecurePass123!",
        )
        self.client.force_login(other_employer)

        response = self.client.post(
            reverse("update-interview-status", args=(interview.pk,)),
            {"status": "cancelled"},
        )

        self.assertEqual(response.status_code, 404)
        interview.refresh_from_db()
        self.assertEqual(interview.status, "scheduled")


class ApprovedCompanyDirectoryTests(TestCase):
    def test_directory_is_empty_without_approved_employers(self):
        response = self.client.get(reverse("companies"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No approved companies yet")
        self.assertContains(response, 'href="/"')
        self.assertContains(response, 'src="/images/talentbridge-mark.svg"')

    def test_only_approved_companies_are_public(self):
        owner = User.objects.create_user(username="directory-employer@example.com", password="SecurePass123!")
        hidden = Company.objects.create(owner=owner, name="Hidden Workshop", is_approved=False)
        visible = Company.objects.create(name="Northwind Labs", is_approved=True, location="Pune", industry="Software")
        Job.objects.create(
            company=visible,
            title="Backend Engineer",
            description="Build reliable services for hiring teams and candidates.",
            location="Pune",
            is_active=True,
        )

        listing = self.client.get(reverse("companies"))
        self.assertContains(listing, "Northwind Labs")
        self.assertNotContains(listing, "Hidden Workshop")

        hidden_page = self.client.get(reverse("company-detail", args=[hidden.pk]))
        self.assertEqual(hidden_page.status_code, 404)

        detail = self.client.get(reverse("company-detail", args=[visible.pk]))
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, "Backend Engineer")
        self.assertContains(detail, 'src="/images/talentbridge-mark.svg"')


class DashboardAccountCountTests(TestCase):
    def test_dashboards_show_account_counts(self):
        employer = User.objects.create_user(username="dash-employer@example.com", password="SecurePass123!")
        Profile.objects.create(user=employer, full_name="Dash Employer", role="employer")
        company = Company.objects.create(
            owner=employer,
            name="Count Labs",
            industry="Engineering",
            location="Remote",
            website="https://count.example",
            description="A test employer account.",
            is_approved=True,
        )
        job = Job.objects.create(
            company=company,
            title="Count Engineer",
            description="Build the hiring workflow that this dashboard count represents.",
            location="Remote",
        )
        seeker = User.objects.create_user(username="dash-seeker@example.com", password="SecurePass123!")
        Profile.objects.create(user=seeker, full_name="Dash Seeker", role="job_seeker")
        Application.objects.create(job=job, applicant=seeker, status="reviewed")
        second_seeker = User.objects.create_user(
            username="dash-seeker-2@example.com",
            password="SecurePass123!",
        )
        Application.objects.create(job=job, applicant=second_seeker, status="rejected")
        shortlisted_seeker = User.objects.create_user(
            username="dash-seeker-3@example.com",
            password="SecurePass123!",
        )
        shortlisted_application = Application.objects.create(
            job=job,
            applicant=shortlisted_seeker,
            status="shortlisted",
        )
        pending_seeker = User.objects.create_user(
            username="dash-seeker-4@example.com",
            password="SecurePass123!",
        )
        Application.objects.create(job=job, applicant=pending_seeker)
        Job.objects.create(
            company=company,
            title="Closed Engineer",
            description="A closed posting used to verify account statistics.",
            is_active=False,
        )
        Interview.objects.create(
            application=shortlisted_application,
            scheduled_at=timezone.now() + timedelta(days=2),
            created_by=employer,
        )
        demo_job = Job.objects.create(
            company=company,
            title="Demo-only Engineer",
            description="A synthetic listing excluded from account analytics.",
            is_demo=True,
        )
        Application.objects.create(job=demo_job, applicant=seeker)
        SavedJob.objects.create(user=seeker, job=job)

        self.client.force_login(seeker)
        seeker_page = self.client.get("/pages/dashboard/jdashboard.html")
        self.assertContains(seeker_page, 'data-account-applications="1"')
        self.assertContains(seeker_page, 'data-account-saved="1"')
        self.assertContains(seeker_page, "Count Engineer")
        self.assertContains(seeker_page, "Count Labs")
        self.assertNotContains(seeker_page, "Demo applications are saved in this browser.")

        self.client.force_login(employer)
        employer_page = self.client.get("/pages/dashboard/cdashboard.html")
        self.assertContains(employer_page, 'data-account-jobs="1"')
        self.assertContains(employer_page, 'data-account-closed-jobs="1"')
        self.assertContains(employer_page, 'data-account-applicants="4"')
        self.assertContains(employer_page, 'data-account-pending="1"')
        self.assertContains(employer_page, 'data-account-reviewed="1"')
        self.assertContains(employer_page, 'data-account-rejected="1"')
        self.assertContains(employer_page, 'data-account-shortlisted="1"')
        self.assertContains(employer_page, 'data-account-interviews="1"')
        self.assertContains(employer_page, 'id="closedJobsValue">1</strong>')
        self.assertContains(employer_page, 'id="pendingValue">1</strong>')
        self.assertContains(employer_page, 'id="shortlistedValue">1</strong>')
        self.assertContains(employer_page, 'id="interviewsValue">1</strong>')
        self.assertContains(employer_page, "Count Engineer")
        self.assertContains(employer_page, "dash-seeker@example.com")
        self.assertContains(employer_page, 'class="status-pill status-review">Reviewed</span>')
        self.assertContains(employer_page, 'class="status-pill status-rejected">Rejected</span>')
        self.assertContains(employer_page, 'id="sidebarCompanyName">Count Labs</strong>')
        self.assertContains(employer_page, 'id="profileIndustry">Engineering</span>')
        self.assertContains(employer_page, 'id="profileLocation">Remote</span>')
        self.assertContains(employer_page, '<p id="bannerDescription">A test employer account.</p>')
        self.assertContains(employer_page, "account-application-history")
        self.assertContains(employer_page, '"count": 4')
        self.assertNotContains(employer_page, "Demo-only Engineer")
        self.assertNotContains(employer_page, "TechSphere Solutions")
        self.assertNotContains(employer_page, "128")
        self.assertNotContains(employer_page, "Aarav Sharma")
        self.assertNotContains(employer_page, "Frontend Developer")



class SuppliedReferenceImageIntegrationTests(TestCase):
    def test_homepage_renders_supplied_candidate_and_office_assets(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        # Homepage hero/smart-card assets currently in use (kept labelled DEMO where applicable).
        self.assertContains(response, "/images/tb-hero-candidate.jpg")
        self.assertContains(response, "/images/rahul-sharma.jpg")
        self.assertContains(response, "/images/talentbridge-mark.svg")

    def test_login_renders_local_office_visual_and_real_django_form(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'action="/login/" method="post"')
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'name="password"')
        self.assertContains(response, "/images/Airy%20Futuristic%20Office%20with%20City%20Views(1).png")

    def test_about_page_renders_supplied_skyline_image(self):
        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/images/Manhattan%20Skyline%20at%20Dusk.png")

    def test_supplied_image_assets_are_served_by_django(self):
        for path in (
            "/images/avatar_rahul.svg",
            "/images/Airy%20Futuristic%20Office%20with%20City%20Views(1).png",
            "/images/Manhattan%20Skyline%20at%20Dusk.png",
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                body = b"".join(response.streaming_content) if getattr(response, "streaming", False) else response.content
                self.assertGreater(len(body), 100)
