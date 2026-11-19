from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from jobs.models import (
    Application,
    Company,
    ContactInquiry,
    Interview,
    Job,
    Notification,
    Profile,
    SavedJob,
)


DEMO_PREFIX = "demo-"
DEMO_COMPANIES = (
    ("Demo Northstar Studio", "Design", "Bhopal"),
    ("Demo Orbit Systems", "Technology", "Remote"),
    ("Demo Nova Digital", "Technology", "Pune"),
    ("Demo ClearPath Consulting", "Business", "Mumbai"),
    ("Demo Meridian Engineering", "Engineering", "Indore"),
)
DEMO_JOBS = (
    ("Demo Frontend Developer", "Build accessible product interfaces.", "JavaScript, React, CSS", "Remote"),
    ("Demo Product Designer", "Create clear product journeys and prototypes.", "Figma, Research, UI/UX", "Bhopal"),
    ("Demo Software Engineer Intern", "Contribute to product engineering with a mentor.", "Python, APIs, Git", "Remote"),
    ("Demo Business Analyst", "Turn operational data into useful recommendations.", "Analysis, Reporting, SQL", "Mumbai"),
    ("Demo Mechanical Design Engineer", "Support product design reviews and engineering drawings.", "CAD, Design, Manufacturing", "Indore"),
)


class Command(BaseCommand):
    help = "Create five clearly labeled demo records in each TalentBridge domain table."

    @transaction.atomic
    def handle(self, *args, **options):
        user_model = get_user_model()
        users = []
        companies = []

        for index in range(5):
            email = f"{DEMO_PREFIX}user-{index + 1}@example.test"
            user, created = user_model.objects.get_or_create(
                username=email,
                defaults={
                    "email": email,
                    "first_name": f"Demo User {index + 1}",
                    "is_active": False,
                },
            )
            if created:
                user.set_unusable_password()
                user.save(update_fields=("password",))
            if user.is_active or user.has_usable_password():
                raise CommandError(
                    f"Refusing to use active account {email} for demo data; existing accounts were left unchanged."
                )
            users.append(user)
            role = "employer" if index >= 3 else "job_seeker"
            profile, _ = Profile.objects.get_or_create(
                user=user,
                defaults={
                    "role": role,
                    "full_name": f"Demo User {index + 1}",
                    "headline": "Sample TalentBridge profile",
                    "skills": "Communication, Collaboration",
                    "location": ("Bhopal", "Pune", "Remote", "Mumbai", "Indore")[index],
                    "bio": "Demonstration profile only; this account cannot sign in.",
                },
            )

        for index, (name, industry, location) in enumerate(DEMO_COMPANIES):
            owner = users[index + 3] if index < 2 else None
            company, _ = Company.objects.get_or_create(
                name=name,
                defaults={
                    "owner": owner,
                    "is_approved": True,
                    "description": "Sample company for local demonstrations.",
                    "website": "https://example.test",
                    "industry": industry,
                    "location": location,
                },
            )
            companies.append(company)

        jobs = []
        for index, (title, description, skills, location) in enumerate(DEMO_JOBS):
            job, _ = Job.objects.get_or_create(
                company=companies[index],
                title=title,
                defaults={
                    "description": description,
                    "requirements": skills,
                    "skills": skills,
                    "salary": "Sample compensation",
                    "location": location,
                    "experience": "Sample experience",
                    "job_type": "Internship" if index == 2 else "Full-time",
                    "work_mode": "Remote" if location == "Remote" else "Hybrid",
                    "is_active": True,
                    "is_demo": True,
                },
            )
            jobs.append(job)

        applications = []
        for index, job in enumerate(jobs):
            applicant = users[index % 3]
            application, _ = Application.objects.get_or_create(
                job=job,
                applicant=applicant,
                defaults={
                    "cover_note": "DEMO application; no real application was submitted.",
                    "status": Application.STATUS_CHOICES[index % len(Application.STATUS_CHOICES)][0],
                },
            )
            applications.append(application)

        for index in range(5):
            name = f"Demo Contact {index + 1}"
            email = f"{DEMO_PREFIX}contact-{index + 1}@example.test"
            message = f"DEMO inquiry {index + 1}; sample message for local testing."
            if not ContactInquiry.objects.filter(name=name, email=email, message=message).exists():
                ContactInquiry.objects.create(
                    name=name,
                    email=email,
                    topic=ContactInquiry.TOPIC_CHOICES[index % len(ContactInquiry.TOPIC_CHOICES)][0],
                    message=message,
                )

        for index, job in enumerate(jobs):
            SavedJob.objects.get_or_create(user=users[(index + 1) % 3], job=job)

        for index, user in enumerate(users):
            title = f"[DEMO] Sample notification {index + 1}"
            Notification.objects.get_or_create(
                user=user,
                title=title,
                defaults={
                    "message": "Demonstration notification; no action is required.",
                    "target_url": "/jobs/",
                },
            )

        interview_time = timezone.now() + timedelta(days=7)
        for index, application in enumerate(applications):
            notes = f"[DEMO] Sample interview {index + 1}."
            if not Interview.objects.filter(application=application, notes=notes).exists():
                Interview.objects.create(
                    application=application,
                    scheduled_at=interview_time + timedelta(days=index),
                    location_or_link="Online demonstration meeting",
                    notes=notes,
                    created_by=companies[index].owner,
                )

        seeded_counts = {
            "users": user_model.objects.filter(username__startswith=DEMO_PREFIX).count(),
            "profiles": Profile.objects.filter(full_name__startswith="Demo User ").count(),
            "companies": Company.objects.filter(name__startswith="Demo ").count(),
            "jobs": Job.objects.filter(is_demo=True).count(),
            "applications": Application.objects.filter(job__is_demo=True).count(),
            "contact inquiries": ContactInquiry.objects.filter(email__startswith=DEMO_PREFIX).count(),
            "saved jobs": SavedJob.objects.filter(job__is_demo=True).count(),
            "notifications": Notification.objects.filter(title__startswith="[DEMO]").count(),
            "interviews": Interview.objects.filter(application__job__is_demo=True).count(),
        }
        self.stdout.write(
            self.style.SUCCESS(
                "Demo records ready: " + ", ".join(f"{name}={count}" for name, count in seeded_counts.items())
            )
        )
