import re
import zipfile
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.mail import send_mail
from django.core import signing
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.db.models import Case, Count, IntegerField, Q, Value, When
from django.db.models.functions import TruncDate
from django.shortcuts import render as django_render, redirect, get_object_or_404
from django.urls import reverse
from django.http import FileResponse, Http404, JsonResponse
from pathlib import Path
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.views.decorators.http import require_POST, require_http_methods
from .forms import JobAlertPreferenceForm, ResumeBuilderForm
from .google_oauth import (
    google_oauth_configured,
    google_oauth_public_origin,
    google_oauth_request_matches_public_host,
    sync_google_social_app,
)
from .models import (
    Application,
    ApplicationStatusEvent,
    ContactInquiry,
    Job,
    Company,
    Profile,
    ResumeDraft,
    SavedJob,
    Notification,
    Interview,
    SignupRecord,
    JobAlert,
    JobAlertPreference,
)

User = get_user_model()
DEMO_JOB_ROLES = (
    {
        "slug": "frontend-developer",
        "title": "Frontend Developer",
        "company": "Google",
        "location": "Remote",
        "work_mode": "Remote",
        "job_type": "Full-time",
        "salary": "₹8–14 LPA",
        "experience": "2+ years",
        "skills": "JavaScript, React, CSS",
        "description": "Build accessible, responsive product interfaces with a collaborative design and engineering team.",
    },
    {
        "slug": "ui-ux-designer",
        "title": "UI/UX Designer",
        "company": "Northstar Studio",
        "location": "Bhopal",
        "work_mode": "Hybrid",
        "job_type": "Full-time",
        "salary": "₹6–10 LPA",
        "experience": "1–3 years",
        "skills": "Figma, UI/UX, Design research",
        "description": "Shape thoughtful product journeys from early research through high-fidelity design.",
    },
    {
        "slug": "software-engineer-intern",
        "title": "Software Engineer Intern",
        "company": "Orbit Systems",
        "location": "Remote",
        "work_mode": "Remote",
        "job_type": "Internship",
        "salary": "₹20,000–30,000/month",
        "experience": "Entry level",
        "skills": "Python, APIs, Git",
        "description": "Learn by contributing to product engineering tasks with support from experienced engineers.",
        "is_startup": True,
    },
    {
        "slug": "junior-web-developer",
        "title": "Junior Web Developer",
        "company": "Nova Digital",
        "location": "Bhopal",
        "work_mode": "On-site",
        "job_type": "Full-time",
        "salary": "₹4–6 LPA",
        "experience": "0–2 years",
        "skills": "HTML, CSS, JavaScript",
        "description": "Implement responsive layouts, test across screen sizes, and help maintain shared components.",
        "is_startup": True,
    },
    {
        "slug": "business-analyst",
        "title": "Business Analyst",
        "company": "ClearPath Consulting",
        "location": "Mumbai",
        "work_mode": "Hybrid",
        "job_type": "Full-time",
        "salary": "₹7–11 LPA",
        "experience": "2–4 years",
        "skills": "Analysis, Reporting, Communication",
        "description": "Gather requirements, analyze business information, and prepare clear recommendations.",
    },
    {
        "slug": "product-designer",
        "title": "Product Designer",
        "company": "Pixel & Co.",
        "location": "Indore",
        "work_mode": "On-site",
        "job_type": "Full-time",
        "salary": "₹7–12 LPA",
        "experience": "3+ years",
        "skills": "Product design, Research, Figma",
        "description": "Turn user needs into clear product workflows and reusable design patterns.",
    },
    {
        "slug": "growth-marketing-specialist",
        "title": "Growth Marketing Specialist",
        "company": "BrightPath Digital",
        "location": "Remote",
        "work_mode": "Remote",
        "job_type": "Full-time",
        "salary": "₹6–10 LPA",
        "experience": "2+ years",
        "skills": "Marketing, Analytics, Content",
        "description": "Plan audience-focused campaigns and use performance insights to improve results.",
    },
    {
        "slug": "people-operations-coordinator",
        "title": "People Operations Coordinator",
        "company": "PeopleFirst",
        "location": "Pune",
        "work_mode": "Hybrid",
        "job_type": "Full-time",
        "salary": "₹4–7 LPA",
        "experience": "1–3 years",
        "skills": "Coordination, Communication, HR operations",
        "description": "Coordinate onboarding and employee support while maintaining clear process documentation.",
    },
    {
        "slug": "mechanical-design-engineer",
        "title": "Mechanical Design Engineer",
        "company": "Meridian Engineering",
        "location": "Indore",
        "work_mode": "On-site",
        "job_type": "Full-time",
        "salary": "₹6–10 LPA",
        "experience": "2–5 years",
        "skills": "CAD, Design, Manufacturing",
        "description": "Prepare engineering drawings and support design reviews with manufacturing partners.",
    },
)
DEMO_APPLICATION_ROLES = frozenset(role["slug"] for role in DEMO_JOB_ROLES)

DEMO_COMPANIES = tuple(
    {
        "slug": company.lower().replace(" ", "-").replace("&", "and").replace(".", ""),
        "name": company,
        "industry": industry,
        "location": location,
        "description": description,
        "open_roles": roles,
    }
    for company, industry, location, description, roles in (
        (
            "Google",
            "Technology",
            "Remote / Bengaluru",
            "Product and engineering teams hiring for frontend and platform roles across India.",
            1,
        ),
        (
            "Northstar Studio",
            "Design",
            "Bhopal",
            "A product design studio focused on research-led UX for growth-stage companies.",
            1,
        ),
        (
            "Orbit Systems",
            "Software",
            "Remote",
            "Early-stage product company building cloud tools for operations teams.",
            1,
        ),
        (
            "Nova Digital",
            "Digital agency",
            "Bhopal",
            "Web and marketing studio helping local businesses ship modern customer experiences.",
            1,
        ),
        (
            "ClearPath Consulting",
            "Consulting",
            "Mumbai",
            "Business analysis and process improvement for mid-market organizations.",
            1,
        ),
        (
            "Pixel & Co.",
            "Product design",
            "Indore",
            "Design partner for SaaS teams needing reusable product systems.",
            1,
        ),
    )
)
_HEAD_ELEMENT = re.compile(br"<head\b[^>]*>", re.IGNORECASE)
_BASE_ELEMENT = re.compile(br"<base\b", re.IGNORECASE)


def _render_page(request, template_name, context=None):
    response = django_render(request, template_name, context or {})
    if response.status_code != 200 or not response.get("Content-Type", "").startswith("text/html"):
        return response

    content = response.content
    if _BASE_ELEMENT.search(content):
        return response

    base_href = "/pages/"
    if request.path.startswith("/pages/"):
        page_path = request.path[len("/pages/"):].rstrip("/")
        parent = page_path.rpartition("/")[0]
        if parent:
            base_href = f"/pages/{parent}/"

    head = _HEAD_ELEMENT.search(content)
    if head is None:
        raise RuntimeError(f"HTML page template {template_name!r} has no <head> element.")

    base_element = f'\n  <base href="{base_href}">'.encode("ascii")
    premium_stylesheet = b'\n  <link rel="stylesheet" href="/css/base/tb-premium-system.css?v=1">'
    response.content = content[:head.end()] + base_element + premium_stylesheet + content[head.end():]
    return response


def _account_profile_completion(user, profile, education):
    profile = profile or Profile()
    full_name = profile.full_name.strip() or user.get_full_name().strip()
    return [
        {"label": "Name added", "done": bool(full_name), "target": "firstName"},
        {
            "label": "Account email",
            "done": bool(user.email.strip()),
            "href": reverse("edit-profile"),
        },
        {
            "label": "Professional headline",
            "done": bool(profile.headline.strip()),
            "target": "headline",
        },
        {"label": "About you", "done": bool(profile.bio.strip()), "target": "bio"},
        {"label": "Skills listed", "done": bool(profile.skills.strip()), "target": "skills"},
        {"label": "Education", "done": bool(education.strip()), "target": "education"},
        {
            "label": "Experience",
            "done": bool(profile.experience.strip()),
            "target": "experience",
        },
        {"label": "Location", "done": bool(profile.location.strip()), "target": "location"},
        {
            "label": "Resume uploaded",
            "done": bool(profile.resume),
            "href": reverse("resume-management"),
        },
    ]


def _application_form(request):
    job_id = request.GET.get("job_id")
    if job_id and job_id.isdecimal():
        return apply_job(request, int(job_id))

    demo_role = request.GET.get("role", "")
    if demo_role in DEMO_APPLICATION_ROLES:
        return _render_page(
            request,
            "application-form.html",
            {
                "demo_role": demo_role,
                "form_notice": (
                    "This is a sample application preview. No application was sent or saved."
                    if request.method == "POST"
                    else ""
                ),
            },
        )

    messages.info(request, "Choose a job before starting an application.")
    return redirect("jobs")


def salary_calculator(request):
    values = {
        "annual_salary": "",
        "hours_per_week": "40",
        "weeks_per_year": "52",
        "currency": "INR",
    }
    results = None
    error = ""
    currency_symbols = {"INR": "₹", "USD": "$", "EUR": "€", "GBP": "£"}

    if request.method == "POST":
        values = {
            "annual_salary": (request.POST.get("annual_salary") or "").strip()[:32],
            "hours_per_week": (request.POST.get("hours_per_week") or "").strip()[:32],
            "weeks_per_year": (request.POST.get("weeks_per_year") or "").strip()[:32],
            "currency": (request.POST.get("currency") or "").strip()[:3],
        }
        try:
            annual = Decimal(values["annual_salary"])
            hours = Decimal(values["hours_per_week"])
            weeks = Decimal(values["weeks_per_year"])
        except InvalidOperation:
            error = "Enter valid numbers for salary and working schedule."
        else:
            valid_numbers = all(value.is_finite() for value in (annual, hours, weeks))
            if values["currency"] not in currency_symbols:
                error = "Choose a supported currency."
            elif (
                not valid_numbers
                or annual < 0
                or annual > Decimal("1000000000000")
                or hours <= 0
                or hours > 168
                or weeks <= 0
                or weeks > 52
            ):
                error = "Use a salary from 0 to 1,000,000,000,000, hours up to 168 per week, and 1 to 52 work weeks."
            else:
                weekly = annual / weeks
                results = {
                    "annual": annual,
                    "monthly": annual / 12,
                    "semi_monthly": annual / 24,
                    "biweekly": annual / 26,
                    "weekly": weekly,
                    "daily": weekly / 5,
                    "hourly": annual / (hours * weeks),
                }

    context = _public_auth_context(request, "salary-calculator.html")
    context.update(
        {
            "values": values,
            "results": results,
            "error": error,
            "currency_symbol": currency_symbols.get(values["currency"], ""),
        }
    )
    return _render_page(request, "salary-calculator.html", context)


def page_view(request, filename):
    """Render a known public page through Django's template engine.

    The page allowlist prevents arbitrary template paths from being requested
    through the friendly URL aliases.
    """
    allowed_pages = {
        "signup-role.html", "company-signup.html", "jobseeker-signup.html",
        "employer.html", "employee.html", "login.html", "pricing.html",
        "salary-calculator.html",
        "jobseaker.html", "ai-audit-center.html", "blog.html", "careers.html",
        "cookie-preferences.html", "customer-stories.html",
        "platform-status.html", "trust-center.html",
        "posting-job.html", "terms.html", "privacy.html", "about.html",
        "contact.html", "help.html", "faq.html", "categories.html",
        "job-listings.html", "job-search.html", "job-detail.html",
        "remote-work-guide.html",
        "recommended-jobs.html",
        "saved-jobs.html", "applied-jobs.html", "application-form.html",
        "resume-management.html", "profile.html", "edit-profile.html",
        "privacy-settings.html",
        "account-security.html",
        "employer-profile.html", "company-details.html", "manage-jobs.html",
        "manage-applications.html", "candidate-details.html",
        "candidate-search.html",
        "notifications.html", "interviews.html", "admin-dashboard.html",
        "forgot-password.html", "password-reset.html",
        "application-success.html", "access-denied.html", "404.html",
    }
    if filename not in allowed_pages:
        raise Http404("Page not found")
    if filename == "access-denied.html":
        return access_denied_view(request)
    if filename == "salary-calculator.html":
        return salary_calculator(request)
    if filename in {"job-listings.html", "job-search.html"}:
        return job_list(request)
    if filename == "recommended-jobs.html":
        return recommended_jobs(request)
    if filename in {"profile.html", "edit-profile.html"}:
        return profile_view(request)
    if filename == "privacy-settings.html":
        return profile_discovery_settings(request)
    if filename == "account-security.html":
        return account_security(request)
    if filename in {"employer-profile.html", "company-details.html"}:
        return company_profile_view(request)
    if filename == "contact.html":
        return contact_page(request)
    if filename == "resume-management.html":
        return resume_management(request)
    if filename == "application-form.html":
        return _application_form(request)
    if filename == "applied-jobs.html":
        return applied_jobs(request)
    if filename == "manage-jobs.html":
        return manage_jobs(request)
    if filename == "manage-applications.html":
        return manage_applications(request)
    if filename == "candidate-search.html":
        return candidate_search(request)
    if filename == "saved-jobs.html":
        return saved_jobs_view(request)
    if filename == "notifications.html":
        return notifications_view(request)
    if filename == "interviews.html":
        return interviews_view(request)
    if filename == "candidate-details.html":
        return candidate_details(request)
    if filename == "admin-dashboard.html":
        return admin_dashboard(request)
    frontend_root = Path(getattr(settings, "FRONTEND_ROOT", settings.PROJECT_ROOT))
    template_path = frontend_root / "pages" / filename
    if not template_path.is_file():
        template_path = Path(settings.PROJECT_ROOT) / "pages" / filename
    if not template_path.is_file():
        raise Http404("Page not found")
    context = _public_auth_context(request, filename)
    if request.method == "POST":
        context["form_notice"] = (
            "This form is not connected to a server-side workflow yet. "
            "No information was saved."
        )
    return _render_page(request, filename, context)


def page_file(request, path):
    """Render nested page templates safely, rather than serving raw HTML."""
    frontend_root = Path(getattr(settings, "FRONTEND_ROOT", settings.PROJECT_ROOT))
    pages_root = (frontend_root / "pages").resolve()
    if not pages_root.is_dir():
        pages_root = (Path(settings.PROJECT_ROOT) / "pages").resolve()
    requested = (pages_root / path).resolve()
    if pages_root not in requested.parents or not requested.is_file() or requested.suffix.lower() != ".html":
        raise Http404("Page not found")
    if path.startswith("dashboard/") and not request.user.is_authenticated:
        query = urlencode({"next": request.get_full_path()})
        return redirect(f"{reverse('login')}?{query}")
    if path == "dashboard/dindex.html":
        return redirect("/pages/dashboard/cdashboard.html")
    if requested.name in {"job-listings.html", "job-search.html"}:
        return job_list(request)
    if requested.name == "salary-calculator.html":
        return salary_calculator(request)
    if requested.name == "recommended-jobs.html":
        return recommended_jobs(request)
    if requested.name in {"profile.html", "edit-profile.html"}:
        return profile_view(request)
    if requested.name == "privacy-settings.html":
        return profile_discovery_settings(request)
    if requested.name == "account-security.html":
        return account_security(request)
    if requested.name in {"employer-profile.html", "company-details.html"}:
        return company_profile_view(request)
    if requested.name == "contact.html":
        return contact_page(request)
    if requested.name == "resume-management.html":
        return resume_management(request)
    if requested.name == "application-form.html":
        return _application_form(request)
    if requested.name == "applied-jobs.html":
        return applied_jobs(request)
    if requested.name == "manage-jobs.html":
        return manage_jobs(request)
    if requested.name == "manage-applications.html":
        return manage_applications(request)
    if requested.name == "candidate-search.html":
        return candidate_search(request)
    if requested.name == "saved-jobs.html":
        return saved_jobs_view(request)
    if requested.name == "notifications.html":
        return notifications_view(request)
    if requested.name == "interviews.html":
        return interviews_view(request)
    if requested.name == "candidate-details.html":
        return candidate_details(request)
    if requested.name == "admin-dashboard.html":
        return admin_dashboard(request)
    if requested.name == "access-denied.html":
        return access_denied_view(request)
    relative = requested.relative_to(pages_root).as_posix()
    context = _public_auth_context(request, requested.name)
    if path == "dashboard/jdashboard.html":
        account_profile = Profile.objects.filter(user=request.user).first()
        context["account_profile"] = account_profile
        context["account_education"] = _resume_draft_education(request.user)
        context["account_profile_completion"] = _account_profile_completion(
            request.user,
            account_profile,
            context["account_education"],
        )
        account_applications = Application.objects.filter(
            applicant=request.user,
            job__is_demo=False,
        ).select_related("job", "job__company").order_by("-submitted_at")
        context["account_applications"] = account_applications
        context["account_application_count"] = account_applications.count()
        context["account_saved_count"] = SavedJob.objects.filter(user=request.user).count()
    elif path == "dashboard/cdashboard.html":
        company = Company.objects.filter(owner=request.user).first()
        all_owned_jobs = Job.objects.filter(company__owner=request.user, is_demo=False)
        owned_jobs = all_owned_jobs.filter(is_active=True).annotate(applicant_count=Count("applications")).order_by("-posted_at")
        employer_applications = Application.objects.filter(
            job__company__owner=request.user,
            job__is_demo=False,
        ).select_related("job", "applicant", "applicant__profile").order_by("-submitted_at")
        account_interviews = Interview.objects.filter(
            application__job__company__owner=request.user,
            application__job__is_demo=False,
        )
        chart_start = timezone.now() - timedelta(days=365)
        application_history = employer_applications.filter(
            submitted_at__gte=chart_start,
        ).annotate(
            day=TruncDate("submitted_at"),
        ).values("day").annotate(
            count=Count("pk"),
        ).order_by("day")
        interview_history = account_interviews.filter(
            scheduled_at__gte=chart_start,
        ).annotate(
            day=TruncDate("scheduled_at"),
        ).values("day").annotate(
            count=Count("pk"),
        ).order_by("day")
        context["account_company"] = {
            "name": company.name if company else "",
            "industry": company.industry if company else "",
            "location": company.location if company else "",
            "website": company.website if company else "",
            "description": company.description if company else "",
        }
        context["account_jobs"] = owned_jobs
        context["account_employer_applications"] = employer_applications[:8]
        context["account_job_count"] = owned_jobs.count()
        context["account_closed_job_count"] = all_owned_jobs.filter(is_active=False).count()
        context["account_applicant_count"] = employer_applications.count()
        context["account_pending_count"] = employer_applications.filter(status__in=("applied", "pending")).count()
        context["account_reviewed_count"] = employer_applications.filter(status__in=("under_review", "reviewed")).count()
        context["account_shortlisted_count"] = employer_applications.filter(status="shortlisted").count()
        context["account_rejected_count"] = employer_applications.filter(status="rejected").count()
        context["account_interview_count"] = Interview.objects.filter(
            application__job__company__owner=request.user,
            application__job__is_demo=False,
            status="scheduled",
        ).count()
        context["account_application_history"] = [
            {"date": row["day"].isoformat(), "count": row["count"]}
            for row in application_history
        ]
        context["account_interview_history"] = [
            {"date": row["day"].isoformat(), "count": row["count"]}
            for row in interview_history
        ]
    if request.method == "POST":
        context["form_notice"] = (
            "This form is not connected to a server-side workflow yet. "
            "No information was saved."
        )
    return _render_page(request, relative, context)


def access_denied_view(request, exception=None):
    response = _render_page(request, "access-denied.html")
    response.status_code = 403
    return response


def _public_auth_context(request, filename):
    if filename not in {"login.html", "jobseeker-signup.html", "company-signup.html"}:
        return {}
    next_url = request.GET.get("next", "")
    if not next_url or not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = ""
    return {
        "next": next_url,
        "google_login_enabled": google_oauth_configured(),
    }


def home(request):
    return django_render(
        request,
        "index.html",
        {
            "active_job_count": Job.objects.filter(
                is_active=True,
                is_demo=False,
                company__is_approved=True,
            ).count(),
            "approved_company_count": Company.objects.filter(is_approved=True).count(),
            "candidate_count": Profile.objects.filter(
                role="job_seeker",
                user__is_active=True,
            ).count(),
        },
    )


def company_directory(request):
    companies = Company.objects.filter(is_approved=True).order_by("name")
    demo_companies = () if companies.exists() else DEMO_COMPANIES
    return _render_page(
        request,
        "companies/list.html",
        {"companies": companies, "demo_companies": demo_companies},
    )


def public_company_detail(request, company_id):
    company = get_object_or_404(Company, pk=company_id, is_approved=True)
    jobs = company.jobs.filter(is_active=True, is_demo=False).order_by("-posted_at")
    return _render_page(request, "companies/detail.html", {"company": company, "jobs": jobs})


@login_required(login_url="login")
def dashboard_redirect(request):
    profile = Profile.objects.filter(user=request.user).first()
    if profile and profile.role == "employer":
        company = Company.objects.filter(owner=request.user).first()
        if company and not company.is_approved:
            return redirect("employer_pending")
        return redirect("/pages/dashboard/cdashboard.html")
    return redirect("/pages/dashboard/jdashboard.html")


@login_required
@require_POST
def dashboard_profile_save(request):
    full_name = request.POST.get("full_name", "").strip()[:100]
    if not full_name:
        return JsonResponse({"error": "Enter your full name."}, status=400)

    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={"full_name": full_name},
    )
    profile.full_name = full_name
    profile.headline = request.POST.get("headline", "").strip()[:200]
    profile.location = request.POST.get("location", "").strip()[:100]
    profile.skills = request.POST.get("skills", "").strip()[:200]
    profile.experience = request.POST.get("experience", "").strip()[:100]
    profile.bio = request.POST.get("description", "").strip()[:5000]
    education = request.POST.get("education", "").strip()[:2000]
    with transaction.atomic():
        profile.save(update_fields=("full_name", "headline", "location", "skills", "experience", "bio"))

        names = full_name.split()
        request.user.first_name = names[0][:150]
        request.user.last_name = " ".join(names[1:])[:150]
        request.user.save(update_fields=("first_name", "last_name"))
        _save_resume_draft_education(request.user, education)
    return JsonResponse({"ok": True})


def _resume_draft_education(user):
    draft = ResumeDraft.objects.filter(user=user).only("content").first()
    if draft is None:
        return ""
    if not isinstance(draft.content, dict):
        raise RuntimeError("The saved resume draft has an invalid data format.")
    education = draft.content.get("education", "")
    return education if isinstance(education, str) else ""


def _save_resume_draft_education(user, education):
    draft, _ = ResumeDraft.objects.get_or_create(user=user)
    if not isinstance(draft.content, dict):
        raise RuntimeError("The saved resume draft has an invalid data format.")
    draft.content["education"] = education
    draft.save(update_fields=("content", "updated_at"))


@login_required(login_url="login")
def account_security(request):
    form = PasswordChangeForm(
        user=request.user,
        data=request.POST if request.method == "POST" else None,
    )
    if request.method == "POST" and form.is_valid():
        account = form.save()
        update_session_auth_hash(request, account)
        messages.success(request, "Your password has been updated.")
        return redirect("account-security")
    return _render_page(request, "account-security.html", {"form": form})


def job_list(request, *, work_mode=None, startup_only=False):
    jobs = Job.objects.filter(is_active=True, company__is_approved=True).select_related("company").order_by("-posted_at")
    if not settings.DEBUG:
        jobs = jobs.filter(is_demo=False)
    keyword = request.GET.get("keyword", "").strip()[:100]
    title = request.GET.get("title", "").strip()[:100]
    company = request.GET.get("company", "").strip()[:100]
    location = request.GET.get("location", "").strip()[:100]
    skills = request.GET.get("skills", "").strip()[:100]
    experience = request.GET.get("experience", "").strip()[:100]
    job_type = request.GET.get("job_type", "").strip()
    requested_work_mode = request.GET.get("work_mode", "").strip()
    selected_work_mode = work_mode or requested_work_mode
    sort = request.GET.get("sort", "newest").strip().lower()
    filter_errors = []

    allowed_job_types = {choice[0] for choice in Job.JOB_TYPE_CHOICES}
    allowed_work_modes = {"On-site", "Hybrid", "Remote"}
    if job_type and job_type not in allowed_job_types:
        filter_errors.append("The selected job type was invalid and has been ignored.")
        job_type = ""
    if requested_work_mode and requested_work_mode not in allowed_work_modes:
        filter_errors.append("The selected work mode was invalid and has been ignored.")
        if not work_mode:
            selected_work_mode = ""
    if sort not in {"newest", "relevant"}:
        filter_errors.append("The selected sort order was invalid; newest jobs are shown.")
        sort = "newest"

    if selected_work_mode:
        jobs = jobs.filter(work_mode=selected_work_mode)
    if startup_only:
        jobs = jobs.filter(
            Q(company__industry__icontains="startup")
            | Q(company__name__icontains="startup")
            | Q(company__description__icontains="startup")
            | Q(description__icontains="startup")
        )
    if keyword:
        jobs = jobs.filter(Q(title__icontains=keyword) | Q(skills__icontains=keyword) |
                           Q(description__icontains=keyword) | Q(company__name__icontains=keyword))
    if title:
        jobs = jobs.filter(title__icontains=title)
    if company:
        jobs = jobs.filter(company__name__icontains=company)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if skills:
        jobs = jobs.filter(Q(skills__icontains=skills) | Q(requirements__icontains=skills))
    if experience:
        jobs = jobs.filter(experience__icontains=experience)
    if job_type:
        jobs = jobs.filter(job_type=job_type)

    relevance_term = title or keyword
    if sort == "relevant" and (relevance_term or company or skills):
        rank_conditions = []
        if relevance_term:
            rank_conditions.extend((
                When(title__iexact=relevance_term, then=Value(5)),
                When(title__icontains=relevance_term, then=Value(4)),
                When(skills__icontains=relevance_term, then=Value(3)),
                When(company__name__icontains=relevance_term, then=Value(2)),
            ))
        if skills:
            rank_conditions.append(When(skills__icontains=skills, then=Value(3)))
        if company:
            rank_conditions.extend((
                When(company__name__iexact=company, then=Value(5)),
                When(company__name__icontains=company, then=Value(2)),
            ))
        jobs = jobs.annotate(
            search_relevance=Case(
                *rank_conditions,
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by("-search_relevance", "-posted_at")
    else:
        jobs = jobs.order_by("-posted_at")

    demo_roles = []
    if settings.DEBUG and not jobs.exists():
        demo_roles = [
            role for role in DEMO_JOB_ROLES
            if (not keyword or keyword.casefold() in " ".join(str(value) for value in role.values()).casefold())
            and (not title or title.casefold() in role["title"].casefold())
            and (not company or company.casefold() in role["company"].casefold())
            and (not location or location.casefold() in role["location"].casefold())
            and (not skills or skills.casefold() in role["skills"].casefold())
            and (not experience or experience.casefold() in role["experience"].casefold())
            and (not job_type or role["job_type"] == job_type)
            and (not selected_work_mode or role["work_mode"] == selected_work_mode)
            and (not startup_only or role.get("is_startup", False))
        ]

    page_obj = Paginator(jobs, 12).get_page(request.GET.get("page"))

    def page_url(page_number):
        params = request.GET.copy()
        params["page"] = page_number
        return f"{request.path}?{params.urlencode()}"

    listing_url = reverse(
        "remote-jobs" if work_mode == "Remote" else
        "startup-jobs" if startup_only else
        "jobs"
    )
    if work_mode == "Remote":
        page_title = "Remote jobs"
        page_heading = "Find remote work that fits."
        page_description = "Browse active roles marked as remote by approved employers."
    elif startup_only:
        page_title = "Startup jobs"
        page_heading = "Explore startup opportunities."
        page_description = "Browse roles at approved companies identified as startups."
    else:
        page_title = "Latest jobs"
        page_heading = "Find work that fits."
        page_description = "Search opportunities by role, skills, or location."
    has_filters = any((keyword, title, company, location, skills, experience, job_type, selected_work_mode))
    return _render_page(
        request,
        "jobs/home.html",
        {
            "jobs": page_obj.object_list,
            "page_obj": page_obj,
            "demo_roles": demo_roles,
            "keyword": keyword,
            "title": title,
            "company_query": company,
            "location": location,
            "skills_query": skills,
            "experience_query": experience,
            "job_types": Job.JOB_TYPE_CHOICES,
            "work_modes": (("On-site", "On-site"), ("Hybrid", "Hybrid"), ("Remote", "Remote")),
            "selected_job_type": job_type,
            "selected_work_mode": selected_work_mode,
            "selected_sort": sort,
            "filter_errors": filter_errors,
            "has_filters": has_filters,
            "previous_page_url": page_url(page_obj.previous_page_number()) if page_obj.has_previous() else "",
            "next_page_url": page_url(page_obj.next_page_number()) if page_obj.has_next() else "",
            "listing_url": listing_url,
            "page_title": page_title,
            "page_heading": page_heading,
            "page_description": page_description,
        },
    )


def remote_jobs(request):
    return job_list(request, work_mode="Remote")


def startup_jobs(request):
    return job_list(request, startup_only=True)


def _experience_years(value):
    value = (value or "").strip().casefold()
    if re.search(r"\b(entry[- ]level|fresher|no experience|zero years?)\b", value):
        return 0.0
    match = re.search(r"(?<!\w)(\d+(?:\.\d+)?)", value)
    return float(match.group(1)) if match else None


def _experience_matches(profile_experience, job_experience):
    candidate_years = _experience_years(profile_experience)
    requirement = (job_experience or "").casefold().replace("–", "-").replace("—", "-")
    required_years = [float(value) for value in re.findall(r"(?<!\w)(\d+(?:\.\d+)?)", requirement)]
    if candidate_years is None:
        return False
    if not required_years:
        return candidate_years == 0 and bool(
            re.search(r"\b(entry[- ]level|fresher|no experience|zero years?)\b", requirement)
        )
    if len(required_years) > 1 and re.search(r"\d\s*(?:-|to)\s*\d", requirement):
        return required_years[0] <= candidate_years <= required_years[1]
    if "+" in requirement or "plus" in requirement:
        return candidate_years >= required_years[0]
    return candidate_years >= required_years[0]


def _recommendation_match_signals(searchable_text, role_location, skill_terms, profile_location,
                                  profile_experience, job_experience):
    searchable_text = searchable_text.casefold()
    matched_skills = [
        display
        for normalized, display in skill_terms.items()
        if re.search(rf"(?<!\w){re.escape(normalized)}(?!\w)", searchable_text)
    ]
    location_match = bool(
        profile_location
        and profile_location in (role_location or "").casefold()
    )
    experience_match = _experience_matches(profile_experience, job_experience)
    return matched_skills, location_match, experience_match


@login_required(login_url="login")
def recommended_jobs(request):
    profile = Profile.objects.filter(user=request.user).first()
    skill_terms = {}
    for term in re.split(r"[,;\n|]", profile.skills if profile else ""):
        if term.strip():
            skill_terms.setdefault(term.strip().casefold(), term.strip())
    profile_location = (profile.location if profile else "").strip().casefold()
    profile_experience = profile.experience if profile else ""
    selected_job_type = request.GET.get("job_type", "").strip()
    selected_work_mode = request.GET.get("work_mode", "").strip()
    filter_errors = []
    if selected_job_type and selected_job_type not in {choice[0] for choice in Job.JOB_TYPE_CHOICES}:
        filter_errors.append("The selected job type was invalid and has been ignored.")
        selected_job_type = ""
    if selected_work_mode and selected_work_mode not in {"On-site", "Hybrid", "Remote"}:
        filter_errors.append("The selected work mode was invalid and has been ignored.")
        selected_work_mode = ""
    available_jobs = Job.objects.filter(
        is_active=True,
        company__is_approved=True,
        is_demo=False,
    ).exclude(
        applications__applicant=request.user,
    ).select_related("company").distinct()
    if selected_job_type:
        available_jobs = available_jobs.filter(job_type=selected_job_type)
    if selected_work_mode:
        available_jobs = available_jobs.filter(work_mode=selected_work_mode)
    saved_job_ids = set(
        SavedJob.objects.filter(user=request.user).values_list("job_id", flat=True)
    )
    recommendations = []
    for job in available_jobs:
        matched_skills, location_match, experience_match = _recommendation_match_signals(
            f"{job.title} {job.skills} {job.requirements}",
            job.location,
            skill_terms,
            profile_location,
            profile_experience,
            job.experience,
        )
        reasons = []
        if matched_skills:
            reasons.append("Skills: " + ", ".join(matched_skills))
        if location_match:
            reasons.append("Location matches your profile")
        if experience_match:
            reasons.append("Your listed experience fits the stated requirement")
        if selected_job_type:
            reasons.append("Matches your selected job type")
        if selected_work_mode:
            reasons.append("Matches your selected work mode")
        recommendations.append({
            "job": job,
            "skill_matches": len(matched_skills),
            "matched_skills": matched_skills,
            "location_match": location_match,
            "experience_match": experience_match,
            "reasons": reasons,
            "is_saved": job.pk in saved_job_ids,
        })
    recommendations.sort(
        key=lambda item: (
            item["skill_matches"],
            item["experience_match"],
            item["location_match"],
            item["job"].posted_at,
        ),
        reverse=True,
    )

    demo_recommendations = []
    has_real_jobs = Job.objects.filter(
        is_active=True,
        company__is_approved=True,
        is_demo=False,
    ).exists()
    if settings.DEBUG and not has_real_jobs:
        for index, role in enumerate(DEMO_JOB_ROLES):
            if selected_job_type and role["job_type"] != selected_job_type:
                continue
            if selected_work_mode and role["work_mode"] != selected_work_mode:
                continue
            matched_skills, location_match, experience_match = _recommendation_match_signals(
                f"{role['title']} {role['skills']} {role['description']}",
                role["location"],
                skill_terms,
                profile_location,
                profile_experience,
                role["experience"],
            )
            reasons = []
            if matched_skills:
                reasons.append("Skills: " + ", ".join(matched_skills))
            if location_match:
                reasons.append("Location matches your profile")
            if experience_match:
                reasons.append("Your listed experience fits the stated requirement")
            if selected_job_type:
                reasons.append("Matches your selected job type")
            if selected_work_mode:
                reasons.append("Matches your selected work mode")
            demo_recommendations.append({
                "role": role,
                "skill_matches": len(matched_skills),
                "matched_skills": matched_skills,
                "location_match": location_match,
                "experience_match": experience_match,
                "reasons": reasons,
                "order": index,
            })
        demo_recommendations.sort(
            key=lambda item: (
                item["skill_matches"],
                item["experience_match"],
                item["location_match"],
                -item["order"],
            ),
            reverse=True,
        )

    return _render_page(
        request,
        "recommended-jobs.html",
        {
            "recommendations": recommendations,
            "demo_recommendations": demo_recommendations,
            "profile": profile,
            "job_types": Job.JOB_TYPE_CHOICES,
            "selected_job_type": selected_job_type,
            "selected_work_mode": selected_work_mode,
            "filter_errors": filter_errors,
        },
    )


def job_detail(request, job_id):
    available_jobs = Job.objects.select_related("company").filter(
        is_active=True,
        company__is_approved=True,
    )
    if not settings.DEBUG:
        available_jobs = available_jobs.filter(is_demo=False)
    job = get_object_or_404(available_jobs, pk=job_id)
    return _render_page(request, "job-detail.html", {"job": job})


def _job_alert_match_fields(preference, job):
    matched_fields = []
    if preference.title:
        if preference.title.casefold() not in job.title.casefold():
            return []
        matched_fields.append("title")
    if preference.location:
        wanted_location = preference.location.casefold()
        location_matches = wanted_location in job.location.casefold()
        if wanted_location in {"remote", "work from home"}:
            location_matches = location_matches or job.work_mode.casefold() == "remote"
        if not location_matches:
            return []
        matched_fields.append("location")
    if preference.skills:
        wanted_skills = [
            skill.strip().casefold()
            for skill in re.split(r"[,;\n]+", preference.skills)
            if skill.strip()
        ]
        job_skills = f"{job.skills} {job.requirements}".casefold()
        if not any(skill in job_skills for skill in wanted_skills):
            return []
        matched_fields.append("skills")
    if preference.job_type:
        if preference.job_type != job.job_type:
            return []
        matched_fields.append("job type")
    if preference.work_mode:
        if preference.work_mode != job.work_mode:
            return []
        matched_fields.append("work mode")
    if preference.experience:
        if preference.experience.casefold() not in job.experience.casefold():
            return []
        matched_fields.append("experience")
    return matched_fields


@transaction.atomic
def _record_job_alert(preference, job):
    matched_fields = _job_alert_match_fields(preference, job)
    if not matched_fields:
        return False
    alert, created = JobAlert.objects.get_or_create(
        user=preference.user,
        job=job,
        defaults={
            "preference": preference,
            "matched_fields": matched_fields,
        },
    )
    if created:
        Notification.objects.create(
            user=preference.user,
            title="New job matches your alert",
            message=(
                f"{job.title} at {job.company.name} matches your saved "
                f"{', '.join(matched_fields)} criteria."
            ),
            category="job_alert",
            target_url=reverse("job_detail", args=(job.pk,)),
        )
    return created


def _match_job_alert_preferences(job):
    if not job.is_active or job.is_demo or not job.company.is_approved:
        return
    preferences = JobAlertPreference.objects.filter(enabled=True).select_related("user")
    for preference in preferences.iterator():
        _record_job_alert(preference, job)


def _match_existing_jobs_for_preference(preference):
    if not preference.enabled:
        return
    jobs = Job.objects.filter(
        is_active=True,
        is_demo=False,
        company__is_approved=True,
    ).select_related("company").order_by("-posted_at")
    for job in jobs.iterator():
        _record_job_alert(preference, job)


@login_required
def job_alerts_view(request):
    profile_role = Profile.objects.filter(user=request.user).values_list("role", flat=True).first()
    if profile_role == "employer" or Company.objects.filter(owner=request.user).exists():
        messages.error(request, "Job alerts are available to job seekers.")
        return redirect("dashboard")

    if request.method == "POST" and request.POST.get("action") == "toggle":
        preference_id = request.POST.get("preference_id", "").strip()
        if not preference_id.isdecimal():
            messages.error(request, "Choose a valid saved search.")
            return redirect("job-alerts")
        preference = get_object_or_404(
            JobAlertPreference,
            user=request.user,
            pk=int(preference_id),
        )
        with transaction.atomic():
            preference.enabled = not preference.enabled
            preference.save(update_fields=("enabled", "updated_at"))
            if preference.enabled:
                _match_existing_jobs_for_preference(preference)
        messages.success(
            request,
            "Job alert enabled." if preference.enabled else "Job alert paused.",
        )
        return redirect("job-alerts")

    if request.method == "POST":
        preference_id = request.POST.get("preference_id", "").strip()
        if preference_id:
            if not preference_id.isdecimal():
                messages.error(request, "Choose a valid saved search.")
                return redirect("job-alerts")
            instance = get_object_or_404(
                JobAlertPreference,
                user=request.user,
                pk=int(preference_id),
            )
        else:
            instance = None
        form = JobAlertPreferenceForm(request.POST, instance=instance)
        if form.is_valid():
            with transaction.atomic():
                preference = form.save(commit=False)
                preference.user = request.user
                preference.save()
                if preference.enabled:
                    _match_existing_jobs_for_preference(preference)
            messages.success(request, "Your job alert preferences were saved.")
            return redirect("job-alerts")
    else:
        preference_id = request.GET.get("edit", "").strip()
        if preference_id and not preference_id.isdecimal():
            raise Http404("Saved search not found")
        instance = (
            get_object_or_404(JobAlertPreference, user=request.user, pk=int(preference_id))
            if preference_id
            else None
        )
        form = JobAlertPreferenceForm(instance=instance)

    preferences = JobAlertPreference.objects.filter(user=request.user)
    alerts = JobAlert.objects.filter(user=request.user).select_related(
        "job",
        "job__company",
    )
    return _render_page(
        request,
        "job-alerts.html",
        {
            "form": form,
            "editing_preference": instance,
            "job_alert_preferences": preferences,
            "job_alerts": alerts,
        },
    )


def _assess_job_post_quality(title, description, location, skills, job_type, work_mode, salary="", experience=""):
    """Return a transparent 0-100 quality score with checklist tips. No fabricated AI score."""
    checks = []
    score = 0

    def add(ok, points, label):
        nonlocal score
        if ok:
            score += points
        checks.append({"ok": bool(ok), "label": label, "points": points})

    add(bool(title and len(title) >= 4), 15, "Clear job title")
    add(bool(location), 10, "Location listed")
    add(bool(skills) and len([part for part in skills.replace(";", ",").split(",") if part.strip()]) >= 2, 15, "At least two skills")
    add(len(description or "") >= 30, 15, "Description has at least 30 characters")
    add(len(description or "") >= 120, 15, "Description has useful detail (120+ characters)")
    add(bool(job_type), 10, "Employment type selected")
    add(bool(work_mode), 10, "Work mode selected")
    add(bool(salary), 5, "Salary or pay range included")
    add(bool(experience), 5, "Experience expectation included")
    score = min(100, score)
    if score >= 85:
        level = "Strong"
    elif score >= 60:
        level = "Good"
    else:
        level = "Needs improvement"
    return {"score": score, "level": level, "checks": checks}


@login_required
def create_job(request):
    if request.method != "POST":
        return redirect("posting-job")
    company = Company.objects.filter(owner=request.user).first()
    if company is None:
        messages.error(request, "An employer account is required to publish a job.")
        return redirect("posting-job")
    if not company.is_approved:
        messages.info(request, "Your employer account must be approved before you can publish jobs.")
        return redirect("employer_pending")
    title = request.POST.get("jobTitle", "").strip()
    description = request.POST.get("description", "").strip()
    location = request.POST.get("location", "").strip()
    skills = request.POST.get("skills", "").strip()
    job_type = request.POST.get("employmentType", "")
    work_mode = request.POST.get("workMode", "")
    salary = request.POST.get("salary", "").strip()
    experience = request.POST.get("experience", "").strip()
    allowed_job_types = {choice[0] for choice in Job.JOB_TYPE_CHOICES}
    allowed_work_modes = {"On-site", "Hybrid", "Remote"}
    if not title or not description or len(description) < 30 or not location or not skills:
        messages.error(request, "Add a title, location, skills, and a job description of at least 30 characters.")
        return redirect("posting-job")
    if job_type not in allowed_job_types or work_mode not in allowed_work_modes:
        messages.error(request, "Choose a valid employment type and work arrangement.")
        return redirect("posting-job")
    if len(skills) > 200:
        messages.error(request, "Keep the combined skills list to 200 characters or fewer.")
        return redirect("posting-job")
    quality = _assess_job_post_quality(
        title, description, location, skills, job_type, work_mode, salary=salary, experience=experience
    )
    with transaction.atomic():
        job = Job.objects.create(
            company=company,
            title=title[:200],
            description=description[:5000],
            requirements=skills,
            salary=salary[:100],
            location=location[:100],
            job_type=job_type,
            work_mode=work_mode,
            experience=experience[:100],
            skills=skills,
        )
        _match_job_alert_preferences(job)
    messages.success(
        request,
        f"Your job has been published. Posting quality: {quality['score']}/100 ({quality['level']}).",
    )
    return redirect("job_detail", job_id=job.pk)


@login_required
def apply_job(request, job_id):
    job = get_object_or_404(
        Job.objects.select_related("company"),
        pk=job_id,
        is_active=True,
        company__is_approved=True,
        is_demo=False,
    )
    Profile.objects.get_or_create(
        user=request.user,
        defaults={"full_name": request.user.get_full_name() or request.user.email},
    )
    if request.method == "POST":
        if request.POST.get("confirm") != "yes":
            messages.error(request, "Please confirm your application details before submitting.")
            return redirect(f"{request.path}")
        application, created = Application.objects.get_or_create(
            job=job,
            applicant=request.user,
            defaults={
                "cover_note": request.POST.get("cover_note", "").strip()[:5000],
                "status": "applied",
            },
        )
        if created:
            if job.company.owner_id:
                ApplicationStatusEvent.objects.create(
                    application=application,
                    from_status="",
                    to_status=application.status,
                    changed_by=request.user,
                    note="Application submitted",
                )
                Notification.objects.create(
                    user=job.company.owner,
                    title="New job application",
                    message=f"A candidate applied for {job.title}.",
                    category="application",
                    target_url="/manage-applications/",
                )
            messages.success(request, "Your application has been submitted.")
            return redirect("application-success")
        messages.info(request, "You have already applied for this role.")
        return redirect("job_detail", job_id=job.pk)
    return _render_page(request, "application-form.html", {"job": job})


@login_required
def applied_jobs(request):
    applications = Application.objects.filter(
        applicant=request.user,
        job__is_demo=False,
    ).select_related("job", "job__company").prefetch_related("status_events")
    application_id = request.GET.get("application_id", "").strip()
    if application_id:
        if not application_id.isdecimal():
            raise Http404("Application not found")
        applications = applications.filter(pk=int(application_id))
    status_events = ApplicationStatusEvent.objects.filter(
        application__applicant=request.user,
        application__job__is_demo=False,
    ).select_related("application", "application__job", "application__job__company", "changed_by")[:50]
    status_counts = {
        "total": applications.count() if not application_id else Application.objects.filter(
            applicant=request.user,
            job__is_demo=False,
        ).count(),
        "under_review": Application.objects.filter(
            applicant=request.user,
            job__is_demo=False,
            status__in=("under_review", "reviewed", "pending"),
        ).count(),
        "interview": Application.objects.filter(
            applicant=request.user,
            job__is_demo=False,
            status="interview_scheduled",
        ).count(),
        "selected": Application.objects.filter(
            applicant=request.user,
            job__is_demo=False,
            status="selected",
        ).count(),
    }
    return _render_page(
        request,
        "applied-jobs.html",
        {
            "applications": applications,
            "status_events": status_events,
            "status_counts": status_counts,
            "filtered_application_id": application_id,
        },
    )


@login_required
def manage_jobs(request):
    company = Company.objects.filter(owner=request.user).first()
    if company is None:
        messages.error(request, "An employer account is required to manage jobs.")
        return redirect("home")
    jobs = Job.objects.filter(company=company, is_demo=False).order_by("-posted_at")
    return _render_page(request, "manage-jobs.html", {"company": company, "jobs": jobs})


@login_required
def edit_job(request, job_id):
    company = get_object_or_404(Company, owner=request.user)
    job = get_object_or_404(Job, pk=job_id, company=company, is_demo=False)
    form_values = {
        "jobTitle": job.title,
        "description": job.description,
        "location": job.location,
        "skills": job.skills,
        "employmentType": job.job_type,
        "workMode": job.work_mode,
        "salary": job.salary,
        "experience": job.experience,
    }
    form_errors = []

    if request.method == "POST":
        form_values = request.POST
        title = request.POST.get("jobTitle", "").strip()
        description = request.POST.get("description", "").strip()
        location = request.POST.get("location", "").strip()
        skills = request.POST.get("skills", "").strip()
        job_type = request.POST.get("employmentType", "")
        work_mode = request.POST.get("workMode", "")
        allowed_job_types = {choice[0] for choice in Job.JOB_TYPE_CHOICES}
        allowed_work_modes = {"On-site", "Hybrid", "Remote"}

        if not title or not location or not skills or len(description) < 30:
            form_errors.append(
                "Add a title, location, skills, and a job description of at least 30 characters."
            )
        if job_type not in allowed_job_types or work_mode not in allowed_work_modes:
            form_errors.append("Choose a valid employment type and work arrangement.")
        if len(skills) > 200:
            form_errors.append("Keep the combined skills list to 200 characters or fewer.")

        if not form_errors:
            job.title = title[:200]
            job.description = description[:5000]
            job.location = location[:100]
            job.skills = skills
            job.requirements = skills
            job.job_type = job_type
            job.work_mode = work_mode
            job.salary = request.POST.get("salary", "").strip()[:100]
            job.experience = request.POST.get("experience", "").strip()[:100]
            job.save(update_fields=(
                "title",
                "description",
                "location",
                "skills",
                "requirements",
                "job_type",
                "work_mode",
                "salary",
                "experience",
            ))
            messages.success(request, "Your job posting has been updated.")
            return redirect("manage-jobs")

    return _render_page(
        request,
        "jobs/edit_job.html",
        {
            "job": job,
            "form_values": form_values,
            "form_errors": form_errors,
            "job_type_choices": Job.JOB_TYPE_CHOICES,
            "work_mode_choices": (("On-site", "On-site"), ("Hybrid", "Hybrid"), ("Remote", "Remote")),
        },
    )


@login_required
def manage_applications(request):
    if not Company.objects.filter(owner=request.user).exists():
        messages.error(request, "An employer account is required to manage applications.")
        return redirect("dashboard")
    applications = Application.objects.filter(
        job__company__owner=request.user,
        job__is_demo=False,
    ).select_related("job", "applicant", "applicant__profile")
    query = request.GET.get("q", "").strip()[:100]
    status = request.GET.get("status", "").strip()
    sort = request.GET.get("sort", "newest").strip()
    valid_statuses = {value for value, _label in Application.STATUS_CHOICES}
    if status and status in valid_statuses:
        applications = applications.filter(status=status)
    elif status:
        messages.error(request, "Choose a valid application status filter.")
        status = ""
    if query:
        applications = applications.filter(
            Q(applicant__first_name__icontains=query)
            | Q(applicant__last_name__icontains=query)
            | Q(applicant__email__icontains=query)
            | Q(applicant__profile__full_name__icontains=query)
            | Q(applicant__profile__skills__icontains=query)
            | Q(applicant__profile__experience__icontains=query)
            | Q(job__title__icontains=query)
        )
    if sort == "oldest":
        applications = applications.order_by("submitted_at", "pk")
    else:
        sort = "newest"
        applications = applications.order_by("-submitted_at", "-pk")
    page_obj = Paginator(applications, 25).get_page(request.GET.get("page"))
    return _render_page(
        request,
        "manage-applications.html",
        {
            "applications": page_obj.object_list,
            "page_obj": page_obj,
            "application_status_choices": Application.STATUS_CHOICES,
            "application_query": query,
            "application_status_filter": status,
            "application_sort": sort,
        },
    )


@login_required(login_url="login")
def candidate_search(request):
    company = get_object_or_404(
        Company,
        owner=request.user,
        is_approved=True,
    )
    query = request.GET.get("q", "").strip()[:100]
    applications = Application.objects.filter(
        job__company=company,
        job__is_demo=False,
    ).select_related(
        "job",
        "applicant",
        "applicant__profile",
    )
    if query:
        applications = applications.filter(
            Q(applicant__first_name__icontains=query)
            | Q(applicant__last_name__icontains=query)
            | Q(applicant__email__icontains=query)
            | Q(applicant__profile__full_name__icontains=query)
            | Q(applicant__profile__headline__icontains=query)
            | Q(applicant__profile__skills__icontains=query)
            | Q(applicant__profile__location__icontains=query)
            | Q(job__title__icontains=query)
        )
    discoverable_profiles = Profile.objects.filter(
        role="job_seeker",
        is_discoverable=True,
        user__is_active=True,
        user__is_staff=False,
    ).order_by("full_name")
    if query:
        discoverable_profiles = discoverable_profiles.filter(
            Q(full_name__icontains=query)
            | Q(headline__icontains=query)
            | Q(skills__icontains=query)
            | Q(location__icontains=query)
            | Q(experience__icontains=query)
            | Q(bio__icontains=query)
        )
    profile_page = Paginator(discoverable_profiles, 25).get_page(
        request.GET.get("profile_page")
    )
    page_obj = Paginator(applications.order_by("-submitted_at"), 25).get_page(
        request.GET.get("page")
    )
    return _render_page(
        request,
        "candidate-search.html",
        {
            "applications": page_obj.object_list,
            "page_obj": page_obj,
            "discoverable_profiles": profile_page.object_list,
            "profile_page_obj": profile_page,
            "query": query,
        },
    )


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={"full_name": request.user.get_full_name() or request.user.email},
    )
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()[:100]
        email = request.POST.get("email", "").strip().lower()
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Enter a valid email address.")
            return redirect("edit-profile")
        if not full_name:
            messages.error(request, "Full name is required.")
            return redirect("edit-profile")
        if User.objects.filter(Q(email__iexact=email) | Q(username__iexact=email)).exclude(pk=request.user.pk).exists():
            messages.error(request, "That email address is already associated with another account.")
            return redirect("edit-profile")
        request.user.email = email
        request.user.username = email
        request.user.first_name = full_name.split()[0][:150]
        request.user.last_name = " ".join(full_name.split()[1:])[:150]
        request.user.save(update_fields=("email", "username", "first_name", "last_name"))
        profile.full_name = full_name
        profile.location = request.POST.get("location", "").strip()[:100]
        profile.headline = request.POST.get("headline", "").strip()[:200]
        profile.skills = request.POST.get("skills", "").strip()[:200]
        profile.experience = request.POST.get("experience", "").strip()[:100]
        profile.bio = request.POST.get("description", "").strip()[:5000]
        education = request.POST.get("education", "").strip()[:2000]
        with transaction.atomic():
            profile.save()
            _save_resume_draft_education(request.user, education)
        messages.success(request, "Your profile has been updated.")
        return redirect("profile")
    template_name = "edit-profile.html" if request.path.rstrip("/").endswith("edit-profile") else "profile.html"
    return _render_page(
        request,
        template_name,
        {"profile": profile, "education": _resume_draft_education(request.user)},
    )


@login_required(login_url="login")
def profile_discovery_settings(request):
    profile = Profile.objects.filter(
        user=request.user,
        role="job_seeker",
    ).first()
    if profile is None:
        messages.error(request, "Job seeker profile settings are not available for this account.")
        return redirect("dashboard")

    if request.method == "POST":
        profile.is_discoverable = request.POST.get("is_discoverable") == "true"
        profile.save(update_fields=("is_discoverable",))
        messages.success(
            request,
            "Your profile discovery preference has been saved.",
        )
        return redirect("privacy-settings")

    return _render_page(
        request,
        "privacy-settings.html",
        {"profile": profile},
    )


@login_required
def company_profile_view(request):
    company = Company.objects.filter(owner=request.user).first()
    if company is None:
        messages.error(request, "An employer account is required to manage company details.")
        return redirect("home")
    if request.method == "POST":
        name = request.POST.get("company_name", "").strip()[:200]
        if not name:
            messages.error(request, "Company name is required.")
            return redirect("company-details")
        company.name = name
        company.location = request.POST.get("location", "").strip()[:100]
        company.industry = request.POST.get("industry", "").strip()[:100]
        company.website = request.POST.get("website", "").strip()[:200]
        company.description = request.POST.get("description", "").strip()[:5000]
        try:
            company.full_clean()
            company.save()
        except ValidationError as error:
            messages.error(request, "; ".join(error.messages))
            return redirect("company-details")
        messages.success(request, "Your company profile has been updated.")
        return redirect("company-details")
    return _render_page(request, "company-details.html", {"company": company})


def contact_page(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        topic = request.POST.get("topic", "")
        body = request.POST.get("message", "").strip()
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Enter a valid email address.")
            return redirect("contact")
        allowed_topics = {choice[0] for choice in ContactInquiry.TOPIC_CHOICES}
        if not name or len(name) > 100 or topic not in allowed_topics or not body or len(body) > 5000:
            messages.error(request, "Complete each field using valid information.")
            return redirect("contact")
        ContactInquiry.objects.create(name=name, email=email, topic=topic, message=body)
        messages.success(request, "Thanks for reaching out. Your message has been recorded for our team.")
        return redirect("contact")
    return _render_page(request, "contact.html")


@login_required
def resume_management(request):
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={"full_name": request.user.get_full_name() or request.user.email},
    )
    if request.method == "POST":
        resume = request.FILES.get("resume")
        if resume is None:
            messages.error(request, "Choose a resume file to upload.")
            return redirect("resume-management")
        suffix = Path(resume.name).suffix.lower()
        if suffix not in {".pdf", ".doc", ".docx"} or resume.size > 5 * 1024 * 1024:
            messages.error(request, "Upload a PDF, DOC or DOCX file no larger than 5 MB.")
            return redirect("resume-management")
        signature = resume.read(8)
        resume.seek(0)
        valid_signature = (suffix == ".pdf" and signature.startswith(b"%PDF-")) or (
            suffix == ".doc" and signature.startswith(bytes.fromhex("D0CF11E0A1B11AE1"))
        )
        if suffix == ".docx" and signature.startswith(b"PK"):
            try:
                with zipfile.ZipFile(resume) as document:
                    valid_signature = {
                        "[Content_Types].xml",
                        "word/document.xml",
                    }.issubset(document.namelist())
            except zipfile.BadZipFile:
                valid_signature = False
            finally:
                resume.seek(0)
        if not valid_signature:
            messages.error(request, "The file contents do not match the selected resume format.")
            return redirect("resume-management")
        previous_resume_name = profile.resume.name if profile.resume else None
        profile.resume.save(resume.name, resume, save=True)
        if previous_resume_name and previous_resume_name != profile.resume.name:
            profile.resume.storage.delete(previous_resume_name)
        messages.success(request, "Your resume has been uploaded.")
        return redirect("resume-management")
    return _render_page(
        request,
        "resume-management.html",
        {
            "profile": profile,
            "resume_is_pdf": bool(profile.resume)
            and Path(profile.resume.name).suffix.lower() == ".pdf",
        },
    )


@login_required(login_url="login")
def resume_builder(request):
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={"full_name": request.user.get_full_name() or request.user.email},
    )
    draft = ResumeDraft.objects.filter(user=request.user).first()
    initial = {
        "full_name": profile.full_name,
        "headline": profile.headline,
        "email": request.user.email,
        "phone": profile.phone,
        "location": profile.location,
        "summary": profile.bio,
        "skills": profile.skills,
        "experience": profile.experience,
        "education": _resume_draft_education(request.user),
        "links": "",
    }
    if draft:
        if not isinstance(draft.content, dict):
            raise RuntimeError("The saved resume draft has an invalid data format.")
        initial.update(
            {
                key: value
                for key, value in draft.content.items()
                if key in ResumeBuilderForm.base_fields and isinstance(value, str)
            }
        )

    form = ResumeBuilderForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        draft, _ = ResumeDraft.objects.get_or_create(user=request.user)
        draft.content = dict(form.cleaned_data)
        draft.save(update_fields=("content", "updated_at"))
        messages.success(request, "Your resume draft has been saved to your account.")
        return redirect("resume-builder")

    preview = {
        field: form[field].value() or ""
        for field in ResumeBuilderForm.base_fields
    }
    preview["skill_list"] = [
        skill.strip() for skill in preview["skills"].split(",") if skill.strip()
    ]
    return _render_page(
        request,
        "resume-builder.html",
        {
            "form": form,
            "preview": preview,
            "has_saved_draft": draft is not None,
        },
    )


@login_required
def resume_download(request):
    application_id = request.GET.get("application_id", "")
    if application_id:
        if not application_id.isdecimal():
            raise Http404("Resume not found")
        application = get_object_or_404(
            Application.objects.select_related("applicant"),
            pk=int(application_id),
            job__company__owner=request.user,
        )
        profile = get_object_or_404(Profile, user=application.applicant)
    else:
        profile = get_object_or_404(Profile, user=request.user)
    if not profile.resume:
        raise Http404("Resume not found")
    return FileResponse(
        profile.resume.open("rb"),
        as_attachment=True,
        filename=Path(profile.resume.name).name,
        content_type="application/octet-stream",
    )


@login_required
def resume_preview(request):
    profile = get_object_or_404(Profile, user=request.user)
    if not profile.resume or Path(profile.resume.name).suffix.lower() != ".pdf":
        raise Http404("PDF preview not found")
    response = FileResponse(
        profile.resume.open("rb"),
        as_attachment=False,
        filename=Path(profile.resume.name).name,
        content_type="application/pdf",
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@login_required
@require_POST
def resume_delete(request):
    profile = Profile.objects.filter(user=request.user).first()
    if profile is None or not profile.resume:
        messages.info(request, "There is no resume to delete.")
        return redirect("resume-management")
    profile.resume.delete(save=True)
    messages.success(request, "Your resume has been deleted.")
    return redirect("resume-management")


EMAIL_VERIFICATION_SALT = "talentbridge.email-verification.v1"


def _send_signup_verification(request, user):
    token = signing.dumps({"user_id": user.pk, "email": user.email}, salt=EMAIL_VERIFICATION_SALT)
    verify_url = request.build_absolute_uri(
        reverse("verify-email", kwargs={"uidb64": urlsafe_base64_encode(force_bytes(user.pk)), "token": token})
    )
    send_mail(
        subject="Verify your TalentBridge AI email",
        message=(
            f"Hello {user.first_name or 'there'},\\n\\n"
            "Please verify your email address to activate your TalentBridge AI account.\\n"
            f"{verify_url}\\n\\n"
            "This link expires in 24 hours. If you did not create this account, ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def verify_email(request, uidb64, token):
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        payload = signing.loads(token, salt=EMAIL_VERIFICATION_SALT, max_age=86400)
        if str(payload.get("user_id")) != str(user_id):
            raise signing.BadSignature("User mismatch")
        user = User.objects.get(pk=user_id, email__iexact=payload.get("email", ""))
    except (ValueError, TypeError, OverflowError, signing.BadSignature, signing.SignatureExpired, User.DoesNotExist):
        messages.error(request, "This verification link is invalid or expired. Please request a new one.")
        return redirect("login")

    record = SignupRecord.objects.filter(user=user).first()
    if record is None:
        messages.error(request, "No pending signup verification was found for this account.")
        return redirect("login")
    record.email_verified = True
    record.save(update_fields=["email_verified"])
    user.is_active = True
    user.save(update_fields=["is_active"])

    # Keep django-allauth's verified-email state aligned for Google/email account linking.
    try:
        from allauth.account.models import EmailAddress
        EmailAddress.objects.update_or_create(
            user=user, email=user.email,
            defaults={"verified": True, "primary": True},
        )
    except Exception:
        pass
    messages.success(request, "Email verified successfully. You can now sign in.")
    return redirect("login")


def resend_verification(request):
    messages.info(request, "Email verification is temporarily disabled. You can sign in without verifying your email.")
    return redirect("login")


def _register(request, role):
    page = "pages/company-signup.html" if role == "employer" else "pages/jobseeker-signup.html"
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method != "POST":
        return _render_page(
            request,
            page.split("/", 1)[1],
            {
                "next": request.GET.get("next", ""),
                "google_login_enabled": google_oauth_configured(),
            },
        )
    first_name = request.POST.get("firstName", "").strip()[:150]
    last_name = request.POST.get("lastName", "").strip()[:150]
    email = request.POST.get("email", "").strip().lower()
    phone = request.POST.get("phone", "").strip()[:30]
    password = request.POST.get("password", "")
    confirm = request.POST.get("confirmPassword", "")
    company_name = request.POST.get("companyName", "").strip()[:200]
    if not all((first_name, last_name, email, phone)):
        messages.error(request, "Please complete all required fields.")
        return redirect(page)
    try:
        validate_email(email)
    except ValidationError:
        messages.error(request, "Enter a valid email address.")
        return redirect(page)
    if not re.fullmatch(r"[+]?[0-9 ()-]{7,30}", phone):
        messages.error(request, "Enter a valid phone number.")
        return redirect(page)
    if not request.POST.get("terms"):
        messages.error(request, "Please accept the Terms of Service and Privacy Policy.")
        return redirect(page)
    if password != confirm:
        messages.error(request, "Your passwords do not match.")
        return redirect(page)
    if (len(password) < 8 or not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password)
            or not re.search(r"[0-9]", password) or not re.search(r"[^A-Za-z0-9]", password)):
        messages.error(request, "Password must contain 8+ characters, uppercase, lowercase, a number and a symbol.")
        return redirect(page)
    if role == "employer" and not company_name:
        messages.error(request, "Enter your company name.")
        return redirect(page)
    if User.objects.filter(Q(email__iexact=email) | Q(username__iexact=email)).exists():
        messages.error(request, "An account with this email already exists. Please sign in.")
        return redirect(page)
    try:
        with transaction.atomic():
            # The pre-check blocks legacy accounts too; this unique audit row
            # makes new registrations race-safe even though Django's stock User
            # model does not enforce unique email addresses.
            if User.objects.filter(email__iexact=email).exists():
                raise IntegrityError("This email is already registered.")
            user = User.objects.create_user(username=email, email=email, password=password,
                                            first_name=first_name, last_name=last_name)
            SignupRecord.objects.create(
                user=user, email=email, signup_method="email_password",
                role=role, email_verified=False,
            )
            Profile.objects.create(user=user, role=role, phone=phone,
                                   full_name=f"{first_name} {last_name}".strip())
            if role == "employer":
                Company.objects.create(owner=user, name=company_name, is_approved=False, location="")
    except IntegrityError:
        messages.error(request, "Could not create the account because this email may already be registered.")
        return redirect(page)
    if role == "employer":
        user.backend = "jobs.backends.EmailOrUsernameBackend"
        login(request, user)
        messages.success(request, "Employer account created. Complete your company setup.")
        return redirect("employer_pending")
    messages.success(request, "Account created. You can now sign in.")
    return redirect("login")

def jobseeker_signup(request):
    return _register(request, "job_seeker")

def employer_signup(request):
    return _register(request, "employer")

def login_view(request):
    next_url = request.POST.get("next") or request.GET.get("next", "")
    if not next_url or not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = ""

    if request.user.is_authenticated:
        return redirect(next_url or settings.LOGIN_REDIRECT_URL)
    if request.method != "POST":
        return _render_page(
            request,
            "pages/login.html",
            {"next": next_url, "google_login_enabled": google_oauth_configured()},
        )

    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "")
    if not email or not password:
        messages.error(request, "Enter your email address and password.")
        return _render_page(
            request,
            "pages/login.html",
            {"next": next_url, "google_login_enabled": google_oauth_configured()},
        )
    candidate = User.objects.filter(email__iexact=email).first()
    if candidate and not candidate.is_superuser:
        signup_record = SignupRecord.objects.filter(user=candidate).first()
        if (
            signup_record
            and signup_record.signup_method == "email_password"
            and not signup_record.email_verified
            and not candidate.is_active
            and candidate.check_password(password)
        ):
            candidate.is_active = True
            candidate.save(update_fields=["is_active"])
        if not candidate.is_active:
            messages.error(request, "This account is inactive. Contact support or an administrator.")
            return _render_page(request, "pages/login.html", {"next": next_url, "google_login_enabled": google_oauth_configured()})
    # Pass the email directly to the email-aware backend. Do not choose the
    # first account when legacy data contains duplicate email addresses.
    user = authenticate(request, username=email, password=password)
    if user is None:
        messages.error(request, "Email or password is incorrect.")
        return _render_page(
            request,
            "pages/login.html",
            {"next": next_url, "google_login_enabled": google_oauth_configured()},
        )
    login(request, user)
    return redirect(next_url or settings.LOGIN_REDIRECT_URL)


@require_http_methods(["GET", "POST"])
def social_login_start(request, provider):
    if provider != "google":
        raise Http404("Authentication provider not found.")

    role = request.POST.get("role") or request.GET.get("role", "choose")
    valid_roles = {"job_seeker", "employer", "choose"}
    if role not in valid_roles:
        messages.error(request, "Choose a valid account type before continuing.")
        return redirect("signup")

    if not google_oauth_configured():
        messages.warning(
            request,
            "Google sign-in is not configured. This option is temporarily unavailable.",
        )
        return redirect("login" if role == "choose" else (
            "company-signup" if role == "employer" else "jobseeker-signup"
        ))

    next_url = request.POST.get("next") or request.GET.get("next", "")
    if next_url and not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = ""

    # Always start OAuth on the Google-registered public host (:8000) so the
    # callback URI matches Cloud Console even when Django is on :8001.
    if not google_oauth_request_matches_public_host(request):
        query = urlencode(
            {key: value for key, value in (("role", role), ("next", next_url)) if value}
        )
        target = (
            f"{google_oauth_public_origin(request)}"
            f"{reverse('social-login-start', args=[provider])}"
        )
        if query:
            target = f"{target}?{query}"
        return redirect(target)

    if request.method == "GET":
        return django_render(
            request,
            "socialaccount/auto_login.html",
            {
                "provider": provider,
                "provider_name": "Google",
                "role": role,
                "next": next_url,
            },
        )

    request.session["talentbridge.social_signup_role"] = role
    if next_url:
        request.session["talentbridge.social_login_next"] = next_url
    else:
        request.session.pop("talentbridge.social_login_next", None)

    if provider == "google":
        sync_google_social_app()
        from allauth.socialaccount.providers.google.views import oauth2_login

        return oauth2_login(request)


@require_POST
def logout_view(request):
    logout(request)
    return redirect("home")

@login_required
def employer_pending(request):
    company = Company.objects.filter(owner=request.user).first()
    if company is None:
        messages.info(request, "Complete employer registration to create your company workspace.")
        return redirect("employer_signup")
    if company.is_approved:
        messages.success(request, "Your employer account is approved.")
        return redirect("dashboard")
    return _render_page(request, "employer-pending.html", {"company": company})


@login_required
def saved_jobs_view(request):
    saved = SavedJob.objects.filter(
        user=request.user,
        job__is_active=True,
        job__is_demo=False,
        job__company__is_approved=True,
    ).select_related("job", "job__company")
    return _render_page(request, "saved-jobs.html", {"saved_jobs": saved})


@login_required
@require_POST
def toggle_saved_job(request, job_id):
    job = get_object_or_404(
        Job,
        pk=job_id,
        is_active=True,
        is_demo=False,
        company__is_approved=True,
    )
    saved, created = SavedJob.objects.get_or_create(user=request.user, job=job)
    if not created:
        saved.delete()
        messages.success(request, "Job removed from your saved jobs.")
    else:
        messages.success(request, "Job saved to your account.")
    next_url = request.POST.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect("saved-jobs")


@login_required
def notifications_view(request):
    if request.method == "POST":
        notification_id = request.POST.get("notification_id", "")
        if notification_id and notification_id.isdecimal():
            Notification.objects.filter(user=request.user, pk=int(notification_id)).update(is_read=True)
        elif not notification_id:
            Notification.objects.filter(user=request.user).update(is_read=True)
        else:
            messages.error(request, "Choose a valid notification.")
            return redirect("notifications")
        messages.success(request, "Notification status updated.")
        return redirect("notifications")
    items = Notification.objects.filter(user=request.user)
    category = request.GET.get("category", "").strip()
    allowed_categories = {choice[0] for choice in Notification.CATEGORY_CHOICES}
    if category in allowed_categories:
        items = items.filter(category=category)
    unread_only = request.GET.get("unread", "") == "1"
    if unread_only:
        items = items.filter(is_read=False)
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return _render_page(
        request,
        "notifications.html",
        {
            "notifications": items,
            "unread_count": unread_count,
            "active_category": category if category in allowed_categories else "",
            "unread_only": unread_only,
            "notification_categories": Notification.CATEGORY_CHOICES,
        },
    )


@login_required
def interviews_view(request):
    if request.method == "POST":
        application_id = request.POST.get("application_id", "")
        scheduled_raw = request.POST.get("scheduled_at", "")
        location_or_link = request.POST.get("location_or_link", "").strip()[:500]
        notes = request.POST.get("notes", "").strip()[:3000]
        if not application_id.isdecimal():
            messages.error(request, "Choose a valid application.")
            return redirect("interviews")
        scheduled_at = parse_datetime(scheduled_raw)
        if not scheduled_at:
            messages.error(request, "Enter a valid interview date and time.")
            return redirect("interviews")
        if timezone.is_naive(scheduled_at):
            scheduled_at = timezone.make_aware(scheduled_at, timezone.get_current_timezone())
        if scheduled_at <= timezone.now():
            messages.error(request, "Interview time must be in the future.")
            return redirect("interviews")
        with transaction.atomic():
            application = get_object_or_404(
                Application.objects.select_for_update().select_related(
                    "job",
                    "job__company",
                    "applicant",
                ),
                pk=int(application_id),
                job__company__owner=request.user,
            )
            interview, created = Interview.objects.get_or_create(
                application=application,
                scheduled_at=scheduled_at,
                defaults={
                    "location_or_link": location_or_link,
                    "notes": notes,
                    "created_by": request.user,
                },
            )
            if created:
                _set_application_status(
                    application,
                    "interview_scheduled",
                    changed_by=request.user,
                    note="Interview scheduled",
                )
                Notification.objects.create(
                    user=application.applicant,
                    title="Interview scheduled",
                    message=(
                        f"An interview for {application.job.title} is scheduled for "
                        f"{timezone.localtime(interview.scheduled_at):%b %d, %Y at %I:%M %p}."
                    ),
                    category="interview",
                    target_url="/interviews/",
                )
        if created:
            messages.success(request, "Interview scheduled and candidate notified.")
        else:
            messages.info(request, "That interview is already scheduled.")
        return redirect("interviews")
    employer_applications = Application.objects.filter(
        job__company__owner=request.user,
    ).select_related("job", "applicant").order_by("-submitted_at")
    interviews = Interview.objects.filter(
        application__job__company__owner=request.user,
    ).select_related("application", "application__job", "application__applicant")
    candidate_interviews = Interview.objects.filter(
        application__applicant=request.user,
    ).select_related("application", "application__job", "application__job__company")
    context = {"applications": employer_applications, "interviews": interviews, "candidate_interviews": candidate_interviews}
    return _render_page(request, "interviews.html", context)


def _set_application_status(application, status, changed_by=None, note=""):
    if application.status == status:
        return False
    previous = application.status
    application.status = status
    application.save(update_fields=("status",))
    ApplicationStatusEvent.objects.create(
        application=application,
        from_status=previous,
        to_status=status,
        changed_by=changed_by,
        note=(note or "")[:255],
    )
    return True


@login_required
@require_POST
def update_interview_status(request, interview_id):
    status = request.POST.get("status", "")
    allowed = {choice[0] for choice in Interview.STATUS_CHOICES}
    if status not in allowed:
        messages.error(request, "Choose a valid interview status.")
        return redirect("interviews")
    with transaction.atomic():
        interview = get_object_or_404(
            Interview.objects.select_for_update().select_related(
                "application",
                "application__job",
                "application__applicant",
            ),
            pk=interview_id,
            application__job__company__owner=request.user,
        )
        if interview.status == status:
            messages.info(request, "The interview already has that status.")
            return redirect("interviews")
        interview.status = status
        interview.save(update_fields=("status",))
        Notification.objects.create(
            user=interview.application.applicant,
            title="Interview status updated",
            message=f"The interview for {interview.application.job.title} is now {interview.get_status_display().lower()}.",
            category="interview",
            target_url="/interviews/",
        )
    messages.success(request, "Interview status updated.")
    return redirect("interviews")


@login_required
@require_POST
def update_application_status(request, application_id):
    status = request.POST.get("status", "")
    allowed = {choice[0] for choice in Application.STATUS_CHOICES}
    if status not in allowed:
        messages.error(request, "Choose a valid application status.")
        return redirect("manage-applications")
    with transaction.atomic():
        application = get_object_or_404(
            Application.objects.select_for_update().select_related("job", "applicant"),
            pk=application_id,
            job__company__owner=request.user,
        )
        if not _set_application_status(application, status, changed_by=request.user):
            messages.info(request, "The application already has that status.")
            return redirect("manage-applications")
        Notification.objects.create(
            user=application.applicant,
            title="Application status updated",
            message=f"Your application for {application.job.title} is now {application.get_status_display()}.",
            category="application",
            target_url=f"/applied-jobs/?application_id={application.pk}",
        )
    messages.success(request, "Application status updated.")
    return redirect("manage-applications")


@login_required
@require_POST
def toggle_job_active(request, job_id):
    company = get_object_or_404(Company, owner=request.user)
    job = get_object_or_404(Job, pk=job_id, company=company)
    with transaction.atomic():
        job.is_active = not job.is_active
        job.save(update_fields=("is_active",))
        if job.is_active:
            _match_job_alert_preferences(job)
    messages.success(request, "Job status updated.")
    return redirect("manage-jobs")


@login_required
def candidate_details(request):
    application_id = request.GET.get("application_id", "")
    if not application_id.isdecimal():
        messages.info(request, "Select a candidate from your applications.")
        return redirect("manage-applications")
    application = get_object_or_404(
        Application.objects.select_related("job", "applicant", "applicant__profile"),
        pk=int(application_id),
        job__company__owner=request.user,
    )
    return _render_page(
        request,
        "candidate-details.html",
        {
            "application": application,
            "candidate": application.applicant,
            "candidate_education": _resume_draft_education(application.applicant),
        },
    )


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "Administrator access is required.")
        return redirect("home")
    can_view_companies = (
        request.user.has_perm("jobs.view_company")
        or request.user.has_perm("jobs.change_company")
    )
    can_approve_companies = request.user.has_perm("jobs.change_company")
    pending_companies = (
        Company.objects.filter(is_approved=False)
        .select_related("owner")
        .order_by("created_at")
        if can_view_companies
        else Company.objects.none()
    )
    context = {
        "user_count": User.objects.count(),
        "company_count": Company.objects.count(),
        "pending_companies": pending_companies,
        "pending_company_count": pending_companies.count(),
        "can_view_companies": can_view_companies,
        "can_approve_companies": can_approve_companies,
        "job_count": Job.objects.filter(is_demo=False).count(),
        "demo_job_count": Job.objects.filter(is_demo=True).count(),
        "application_count": Application.objects.filter(job__is_demo=False).count(),
        "contact_inquiries": ContactInquiry.objects.order_by("-received_at")[:20],
    }
    return _render_page(request, "admin-dashboard.html", context)


@login_required
@require_POST
def approve_company(request, company_id):
    if not request.user.is_staff:
        raise Http404("Page not found")
    if not request.user.has_perm("jobs.change_company"):
        raise PermissionDenied
    company = get_object_or_404(Company, pk=company_id)
    company.is_approved = True
    company.save(update_fields=("is_approved",))
    if company.owner_id:
        Notification.objects.create(
            user=company.owner,
            title="Employer account approved",
            message="Your employer account has been approved. You can now publish jobs.",
            category="account",
            target_url="/posting-job/",
        )
    messages.success(request, f"{company.name} has been approved.")
    return redirect("admin-dashboard")
