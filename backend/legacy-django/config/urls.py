"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from pathlib import Path

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path, reverse_lazy
from django.views.generic import RedirectView
from django.views.static import serve
from jobs import dev_preview_views
from jobs import views


# Old flat asset paths → organized subfolders (keeps bookmarks / stale HTML working).
_CSS_ALIASES = {
    "style.css": "base/style.css",
    "tb-foundation.css": "base/tb-foundation.css",
    "tb-premium-system.css": "base/tb-premium-system.css",
    "portal-pages.css": "base/portal-pages.css",
    "redesign.css": "base/redesign.css",
    "pro-upgrade.css": "base/pro-upgrade.css",
    "site-header.css": "components/site-header.css",
    "site-experience.css": "components/site-experience.css",
    "motion.css": "components/motion.css",
    "dark-mode.css": "components/dark-mode.css",
    "landing-intro.css": "components/landing-intro.css",
    "auth-enhancements.css": "components/auth-enhancements.css",
    "auth-provider.css": "components/auth-provider.css",
    "reference-image-integration.css": "components/reference-image-integration.css",
    "admin.css": "components/admin.css",
    "dev-preview.css": "components/dev-preview.css",
    "login.css": "pages/login.css",
    "login-10sec.css": "pages/login-10sec.css",
    "login-motion.css": "pages/login-motion.css",
    "signup-role.css": "pages/signup-role.css",
    "jobseeker-signup.css": "pages/jobseeker-signup.css",
    "company-signup.css": "pages/company-signup.css",
    "forgot-password.css": "pages/forgot-password.css",
    "job-listings.css": "pages/job-listings.css",
    "jobseaker.css": "pages/jobseaker.css",
    "posting-job.css": "pages/posting-job.css",
    "pricing.css": "pages/pricing.css",
    "resume-builder.css": "pages/resume-builder.css",
    "tb-homepage.css": "pages/tb-homepage.css",
    "tb-homepage-attract.css": "pages/tb-homepage-attract.css",
    "tb-homepage-premium.css": "pages/tb-homepage-premium.css",
    "tb-homepage-elevate.css": "pages/tb-homepage-elevate.css",
    "responsive-all.css": "responsive/responsive-all.css",
    "responsive-fixes.css": "responsive/responsive-fixes.css",
}
_JS_ALIASES = {
    "script.js": "core/script.js",
    "site-experience.js": "core/site-experience.js",
    "motion.js": "core/motion.js",
    "dark-mode.js": "core/dark-mode.js",
    "demo-forms.js": "core/demo-forms.js",
    "remove-static-preview-notice.js": "core/remove-static-preview-notice.js",
    "landing-intro.js": "core/landing-intro.js",
    "pro-upgrade.js": "core/pro-upgrade.js",
    "dev-preview.js": "core/dev-preview.js",
    "tb-hero-network.js": "core/tb-hero-network.js",
    "google-oauth.js": "authentication/google-oauth.js",
    "login-10sec.js": "authentication/login-10sec.js",
    "company-signup.js": "authentication/company-signup.js",
    "dashboard-guard.js": "authentication/dashboard-guard.js",
    "job-listings.js": "jobs/job-listings.js",
    "job-preview.js": "jobs/job-preview.js",
    "posting-job.js": "jobs/posting-job.js",
    "jobseaker.js": "jobs/jobseaker.js",
    "resume-builder.js": "jobs/resume-builder.js",
}


def dev_static(request, path, document_root):
    """Serve a project asset and keep development copies from sticking in the browser."""
    root = Path(document_root)
    candidate = root / path
    if not candidate.exists():
        aliases = _JS_ALIASES if root.name == "js" else _CSS_ALIASES if root.name == "css" else {}
        # Exact filename alias (e.g. site-experience.js → core/site-experience.js)
        name = Path(path).name
        mapped = aliases.get(path) or aliases.get(name)
        if mapped and (root / mapped).exists():
            path = mapped
        # Truncated/bad URL like /js/site/ → try site-experience.js
        elif root.name == "js" and path.rstrip("/") in {"site", "site/"}:
            mapped = "core/site-experience.js"
            if (root / mapped).exists():
                path = mapped
    response = serve(request, path, document_root=document_root)
    if settings.DEBUG:
        response.headers["Cache-Control"] = "no-store"
    return response

BASE_DIR = Path(__file__).resolve().parent.parent


def _resolve_repo_root(django_base: Path) -> Path:
    for candidate in (django_base.parent, django_base.parent.parent):
        if (candidate / "database").is_dir() and (
            (candidate / ".env.example").exists() or (candidate / "README.md").exists()
        ):
            return candidate
    return django_base.parent


PROJECT_ROOT = _resolve_repo_root(BASE_DIR)
FRONTEND_ROOT = PROJECT_ROOT / "frontend"
PAGES = {
    'signup': 'signup-role.html',
    'company-signup': 'company-signup.html',
    'jobseeker-signup': 'jobseeker-signup.html',
    'employer': 'employer.html',
    'employee': 'employee.html',
    'jobseaker': 'jobseaker.html',
    'login': 'login.html',
    'pricing': 'pricing.html',
    'salary-calculator': 'salary-calculator.html',
    'platform-status': 'platform-status.html',
    'posting-job': 'posting-job.html',
    'terms': 'terms.html',
    'trust-center': 'trust-center.html',
    'privacy': 'privacy.html',
    'about': 'about.html',
    'ai-audit-center': 'ai-audit-center.html',
    'blog': 'blog.html',
    'careers': 'careers.html',
    'contact': 'contact.html',
    'cookie-preferences': 'cookie-preferences.html',
    'customer-stories': 'customer-stories.html',
    'help': 'help.html',
    'faq': 'faq.html',
    'categories': 'categories.html',
    'jobs': 'job-listings.html',
    'remote-work-guide': 'remote-work-guide.html',
    'recommended-jobs': 'recommended-jobs.html',
    'job-search': 'job-search.html',
    'job-detail': 'job-detail.html',
    'saved-jobs': 'saved-jobs.html',
    'applied-jobs': 'applied-jobs.html',
    'application-form': 'application-form.html',
    'resume-management': 'resume-management.html',
    'privacy-settings': 'privacy-settings.html',
    'get-discovered': 'privacy-settings.html',
    'profile': 'profile.html',
    'edit-profile': 'edit-profile.html',
    'account-security': 'account-security.html',
    'employer-profile': 'employer-profile.html',
    'company-details': 'company-details.html',
    'manage-jobs': 'manage-jobs.html',
    'manage-applications': 'manage-applications.html',
    'candidate-search': 'candidate-search.html',
    'candidate-details': 'candidate-details.html',
    'notifications': 'notifications.html',
    'interviews': 'interviews.html',
    'admin-dashboard': 'admin-dashboard.html',
    'application-success': 'application-success.html',
    'access-denied': 'access-denied.html',
    '404': '404.html',
}

urlpatterns = [
    path("__deploy__/health/", views.deploy_health, name="deploy-health"),
    path('__dev__/', dev_preview_views.dev_preview_dashboard, name='dev-preview-dashboard'),
    path('__dev__/state/', dev_preview_views.dev_preview_state, name='dev-preview-state'),
    path('admin/', admin.site.urls),
    path('favicon.ico', serve, {'document_root': (FRONTEND_ROOT / 'assets' / 'images') if (FRONTEND_ROOT / 'assets' / 'images').is_dir() else (PROJECT_ROOT / 'images'), 'path': 'talentbridge-mark.svg'}),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    path('dashboard/profile/save/', views.dashboard_profile_save, name='dashboard-profile-save'),
    path('jobs/', views.job_list, name='jobs'),
    path('remote-jobs/', views.remote_jobs, name='remote-jobs'),
    path('startup-jobs/', views.startup_jobs, name='startup-jobs'),
    path('companies/', views.company_directory, name='companies'),
    path('companies/<int:company_id>/', views.public_company_detail, name='company-detail'),
    # Friendly aliases for common mistyped / legacy paths (Day 2 audit).
    path('faqs/', RedirectView.as_view(url='/faq/', permanent=False)),
    path('trust/', RedirectView.as_view(url='/trust-center/', permanent=False)),
    path('status/', RedirectView.as_view(url='/platform-status/', permanent=False)),
    path('ai-audit/', RedirectView.as_view(url='/ai-audit-center/', permanent=False)),
    path('cookies/', RedirectView.as_view(url='/cookie-preferences/', permanent=False)),
    path('search/', RedirectView.as_view(url='/job-search/', permanent=False)),
    path('applications/', RedirectView.as_view(url='/applied-jobs/', permanent=False)),
    path('for-employers/', RedirectView.as_view(url='/employer/', permanent=False)),
    path('employers/', RedirectView.as_view(url='/employer/', permanent=False)),
    path('for-job-seekers/', RedirectView.as_view(url='/jobseaker/', permanent=False)),
    path('job-seekers/', RedirectView.as_view(url='/jobseaker/', permanent=False)),
    path('resources/', RedirectView.as_view(url='/careers/', permanent=False)),
    path('jobs/create/', views.create_job, name='create_job'),
    path('jobs/<int:job_id>/edit/', views.edit_job, name='edit-job'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('contact/submit/', views.contact_page, name='contact_submit'),
    path('resume/download/', views.resume_download, name='resume_download'),
    path('resume/preview/', views.resume_preview, name='resume_preview'),
    path('resume/delete/', views.resume_delete, name='resume_delete'),
    path('resume-builder/', views.resume_builder, name='resume-builder'),
    path('saved-jobs/', views.saved_jobs_view, name='saved-jobs'),
    path('job-alerts/', views.job_alerts_view, name='job-alerts'),
    path('jobs/<int:job_id>/save/', views.toggle_saved_job, name='toggle-saved-job'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('interviews/', views.interviews_view, name='interviews'),
    path('interviews/<int:interview_id>/status/', views.update_interview_status, name='update-interview-status'),
    path('applications/<int:application_id>/status/', views.update_application_status, name='update-application-status'),
    path('manage-jobs/<int:job_id>/toggle/', views.toggle_job_active, name='toggle-job-active'),
    path('candidate-details/', views.candidate_details, name='candidate-details'),
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('admin-dashboard/companies/<int:company_id>/approve/', views.approve_company, name='approve-company'),

    path('signup/job-seeker/', views.jobseeker_signup, name='jobseeker_signup'),
    path('signup/employer/', views.employer_signup, name='employer_signup'),
    path('login/', views.login_view, name='login'),
    path("verify-email/<uidb64>/<token>/", views.verify_email, name="verify-email"),
    path("resend-verification/", views.resend_verification, name="resend-verification"),
    path('auth/social/<str:provider>/', views.social_login_start, name='social-login-start'),
    path('logout/', views.logout_view, name='logout'),
    path(
        'accounts/login/',
        RedirectView.as_view(url='/login/', query_string=True),
        name='accounts-login-redirect',
    ),
    # Relative href="../../index.html" on /accounts/3rdparty/signup/ resolves here.
    path(
        'accounts/index.html',
        RedirectView.as_view(url='/', permanent=True),
        name='accounts-index-redirect',
    ),
    path('accounts/', include('allauth.urls')),
    path('employer/pending/', views.employer_pending, name='employer_pending'),
    path(
        'forgot-password/',
        auth_views.PasswordResetView.as_view(
            template_name='forgot-password.html',
            email_template_name='registration/password_reset_email.txt',
            subject_template_name='registration/password_reset_subject.txt',
            success_url=reverse_lazy('password-reset'),
        ),
        name='forgot-password',
    ),
    path(
        'password-reset/',
        auth_views.PasswordResetDoneView.as_view(template_name='password-reset.html'),
        name='password-reset',
    ),
    path(
        'password-reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='password-reset-confirm.html',
            success_url=reverse_lazy('password-reset-complete'),
        ),
        name='password-reset-confirm',
    ),
    path(
        'password-reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name='password-reset-complete.html'),
        name='password-reset-complete',
    ),
    path('pages/jobseeker-signup.html', views.jobseeker_signup, name='jobseeker_signup_page'),
    path('pages/company-signup.html', views.employer_signup, name='employer_signup_page'),
    path('pages/login.html', views.login_view, name='login_page'),
    path('index.html', serve, {'document_root': FRONTEND_ROOT, 'path': 'index.html'}),
    path('site/index.html', RedirectView.as_view(url='/', permanent=False), name='static-home-redirect'),
]

urlpatterns += [
    path(f'{slug}/', views.page_view, {'filename': filename}, name=slug)
    for slug, filename in PAGES.items()
]

_CSS_ROOT = FRONTEND_ROOT / 'css' if (FRONTEND_ROOT / 'css').is_dir() else PROJECT_ROOT / 'css'
_JS_ROOT = FRONTEND_ROOT / 'js' if (FRONTEND_ROOT / 'js').is_dir() else PROJECT_ROOT / 'js'
_IMAGES_ROOT = (
    FRONTEND_ROOT / 'assets' / 'images'
    if (FRONTEND_ROOT / 'assets' / 'images').is_dir()
    else PROJECT_ROOT / 'images'
)

urlpatterns += [
    re_path(r'^pages/(?P<path>.*)$', views.page_file),
    re_path(r'^css/(?P<path>.*)$', dev_static, {'document_root': _CSS_ROOT}),
    re_path(r'^js/(?P<path>.*)$', dev_static, {'document_root': _JS_ROOT}),
    re_path(r'^images/(?P<path>.*)$', serve, {'document_root': _IMAGES_ROOT}),
]

handler403 = views.access_denied_view
