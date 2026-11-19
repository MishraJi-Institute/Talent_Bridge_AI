from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


# Company / Employer Model
class Company(models.Model):
    # Link an employer company to the account that registered it.
    # Nullable so existing company records and imported legacy data remain valid.
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_company",
    )
    is_approved = models.BooleanField(
        default=False,
        help_text="Only approved employers may publish jobs.",
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    logo = models.ImageField(
        upload_to='company_logos',
        blank=True,
        null=True
    )
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# Job Model
class Job(models.Model):

    JOB_TYPE_CHOICES = (
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Internship', 'Internship'),
        ('Freelance', 'Freelance'),
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='jobs'
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    salary = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)

    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPE_CHOICES,
        default='Full-time'
    )
    work_mode = models.CharField(
        max_length=20,
        choices=(("On-site", "On-site"), ("Hybrid", "Hybrid"), ("Remote", "Remote")),
        default="Hybrid",
    )

    experience = models.CharField(max_length=100, blank=True)
    skills = models.CharField(max_length=200, blank=True)

    is_active = models.BooleanField(default=True)
    is_demo = models.BooleanField(
        default=False,
        help_text="Sample listing for local demonstrations; applications are disabled.",
    )
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# Job Seeker Profile Model
class Profile(models.Model):

    ROLE_CHOICES = (
        ("job_seeker", "Job Seeker"),
        ("employer", "Employer"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="job_seeker")
    phone = models.CharField(max_length=30, blank=True)

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(max_length=100)
    headline = models.CharField(max_length=200, blank=True)
    skills = models.CharField(max_length=200, blank=True)
    experience = models.CharField(max_length=100, blank=True)

    resume = models.FileField(
        upload_to='resumes/',
        blank=True,
        null=True
    )

    location = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    is_discoverable = models.BooleanField(
        default=False,
        help_text="Allow approved employers to find this profile in Candidate Search.",
    )

    def __str__(self):
        return self.full_name


class SignupRecord(models.Model):
    """One-time signup audit trail; email is unique across new registrations."""
    METHOD_CHOICES = (
        ("email_password", "Email and password"),
        ("google", "Google"),
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="signup_record",
    )
    email = models.EmailField(max_length=254, unique=True)
    signup_method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    role = models.CharField(max_length=20, blank=True)
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Signup record"
        verbose_name_plural = "Signup records"

    def __str__(self):
        return f"{self.email} ({self.get_signup_method_display()})"


class ResumeDraft(models.Model):
    """A private, editable resume draft belonging to one account."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resume_draft",
    )
    content = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Resume draft for {self.user}"


class Application(models.Model):
    STATUS_CHOICES = (
        ("applied", "Applied"),
        ("under_review", "Under Review"),
        ("shortlisted", "Shortlisted"),
        ("interview_scheduled", "Interview Scheduled"),
        ("selected", "Selected"),
        ("rejected", "Rejected"),
        # Retain values already present in installations using the earlier workflow.
        ("pending", "Pending review"),
        ("reviewed", "Reviewed"),
    )

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_applications",
    )
    cover_note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="applied")
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-submitted_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("job", "applicant"),
                name="unique_job_application_per_applicant",
            ),
        ]

    def __str__(self):
        return f"{self.applicant} — {self.job}"


class ApplicationStatusEvent(models.Model):
    """Immutable history entry when an application status changes."""
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="status_events",
    )
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20)
    note = models.CharField(max_length=255, blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="application_status_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.application_id}: {self.from_status or '—'} → {self.to_status}"


class ContactInquiry(models.Model):
    TOPIC_CHOICES = (
        ("General question", "General question"),
        ("Account support", "Account support"),
        ("Job seeker support", "Job seeker support"),
        ("Employer support", "Employer support"),
    )

    name = models.CharField(max_length=100)
    email = models.EmailField()
    topic = models.CharField(max_length=40, choices=TOPIC_CHOICES)
    message = models.TextField(max_length=5000)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-received_at",)

    def __str__(self):
        return f"{self.topic}: {self.email}"

class SavedJob(models.Model):
    """A job bookmarked by a job seeker."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_jobs")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="saved_by")
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-saved_at",)
        constraints = [
            models.UniqueConstraint(fields=("user", "job"), name="unique_saved_job_per_user"),
        ]

    def __str__(self):
        return f"{self.user} saved {self.job}"


class Notification(models.Model):
    """User-visible in-app notification."""
    CATEGORY_CHOICES = (
        ("application", "Application"),
        ("interview", "Interview"),
        ("job_alert", "Job alert"),
        ("account", "Account"),
        ("general", "General"),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="portal_notifications")
    title = models.CharField(max_length=160)
    message = models.TextField(max_length=2000)
    target_url = models.CharField(max_length=500, blank=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="general",
        blank=True,
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user}: {self.title}"


class JobAlertPreference(models.Model):
    """A job seeker's saved criteria for newly published job alerts."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_alert_preferences",
    )
    title = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    skills = models.CharField(max_length=200, blank=True)
    job_type = models.CharField(max_length=20, choices=Job.JOB_TYPE_CHOICES, blank=True)
    work_mode = models.CharField(
        max_length=20,
        choices=(("On-site", "On-site"), ("Hybrid", "Hybrid"), ("Remote", "Remote")),
        blank=True,
    )
    experience = models.CharField(max_length=100, blank=True)
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)

    def __str__(self):
        return f"Job alert preferences for {self.user}"


class JobAlert(models.Model):
    """A unique in-app match between a job seeker and a published job."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_alerts",
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="alerts")
    preference = models.ForeignKey(
        JobAlertPreference,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matches",
    )
    matched_fields = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("user", "job"),
                name="unique_job_alert_per_user",
            ),
        ]

    def __str__(self):
        return f"Job alert for {self.user}: {self.job}"


class Interview(models.Model):
    """Interview appointment linked to an application."""
    STATUS_CHOICES = (
        ("scheduled", "Scheduled"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="interviews")
    scheduled_at = models.DateTimeField()
    location_or_link = models.CharField(max_length=500, blank=True)
    notes = models.TextField(max_length=3000, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_interviews")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("scheduled_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("application", "scheduled_at"),
                name="unique_interview_slot_per_application",
            ),
        ]

    def __str__(self):
        return f"Interview: {self.application} at {self.scheduled_at:%Y-%m-%d %H:%M}"
