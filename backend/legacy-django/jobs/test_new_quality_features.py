from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import (
    Application,
    Company,
    Job,
    JobAlert,
    JobAlertPreference,
    Notification,
    Profile,
    ResumeDraft,
)


class JobAlertWorkflowTests(TestCase):
    def setUp(self):
        self.employer = User.objects.create_user(
            username="alerts-employer@example.com",
            email="alerts-employer@example.com",
            password="SecurePass123!",
        )
        self.company = Company.objects.create(
            owner=self.employer,
            name="Alert Test Company",
            is_approved=True,
        )
        self.job_seeker = User.objects.create_user(
            username="alerts-seeker@example.com",
            email="alerts-seeker@example.com",
            password="SecurePass123!",
        )
        Profile.objects.create(
            user=self.job_seeker,
            full_name="Alert Seeker",
            role="job_seeker",
        )

    def test_published_matching_job_creates_one_alert_and_notification(self):
        JobAlertPreference.objects.create(
            user=self.job_seeker,
            skills="Python, Django",
            work_mode="Remote",
        )
        JobAlertPreference.objects.create(
            user=self.job_seeker,
            title="Python Engineer",
        )
        self.client.force_login(self.employer)

        response = self.client.post(
            reverse("create_job"),
            {
                "jobTitle": "Python Engineer",
                "description": "Build production web applications with our team.",
                "location": "Anywhere",
                "skills": "Python, Django",
                "employmentType": "Full-time",
                "workMode": "Remote",
                "experience": "2+ years",
            },
        )

        self.assertEqual(response.status_code, 302)
        job = Job.objects.get(title="Python Engineer")
        # Unique (user, job): one alert is stored even if multiple preferences match.
        alerts = list(JobAlert.objects.filter(user=self.job_seeker, job=job))
        self.assertEqual(len(alerts), 1)
        self.assertTrue(
            set(alerts[0].matched_fields) & {"title", "skills", "work mode"},
            alerts[0].matched_fields,
        )
        self.assertEqual(
            Notification.objects.filter(
                user=self.job_seeker,
                title="New job matches your alert",
            ).count(),
            1,
        )

        self.client.post(reverse("toggle-job-active", args=(job.pk,)))
        self.client.post(reverse("toggle-job-active", args=(job.pk,)))
        self.assertEqual(JobAlert.objects.filter(user=self.job_seeker, job=job).count(), 1)
        self.assertEqual(
            Notification.objects.filter(
                user=self.job_seeker,
                title="New job matches your alert",
            ).count(),
            1,
        )

    def test_saved_preference_matches_existing_job_and_can_be_paused(self):
        job = Job.objects.create(
            company=self.company,
            title="Product Designer",
            description="Design accessible workflows for a growing product.",
            location="Bhopal",
            skills="Figma, Research",
        )
        self.client.force_login(self.job_seeker)

        saved = self.client.post(
            reverse("job-alerts"),
            {"title": "Product Designer", "location": "Bhopal"},
        )

        self.assertEqual(saved.status_code, 302)
        preference = JobAlertPreference.objects.get(user=self.job_seeker)
        self.assertTrue(JobAlert.objects.filter(user=self.job_seeker, job=job).exists())
        self.client.post(
            reverse("job-alerts"),
            {"action": "toggle", "preference_id": preference.pk},
        )
        preference.refresh_from_db()
        self.assertFalse(preference.enabled)

        unrelated_job = Job.objects.create(
            company=self.company,
            title="Product Designer II",
            description="Design accessible workflows for a growing product team.",
            location="Bhopal",
        )
        self.assertFalse(JobAlert.objects.filter(user=self.job_seeker, job=unrelated_job).exists())

    def test_preferences_and_alerts_are_private_to_the_job_seeker(self):
        JobAlertPreference.objects.create(user=self.job_seeker, title="Engineer")
        other_user = User.objects.create_user(
            username="other-seeker@example.com",
            email="other-seeker@example.com",
            password="SecurePass123!",
        )
        self.client.force_login(other_user)

        response = self.client.get(reverse("job-alerts"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Engineer")

    def test_employers_cannot_manage_job_seeker_alerts(self):
        self.client.force_login(self.employer)

        response = self.client.get(reverse("job-alerts"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard"))

    def test_empty_preference_is_rejected(self):
        self.client.force_login(self.job_seeker)

        response = self.client.post(reverse("job-alerts"), {})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(JobAlertPreference.objects.count(), 0)
        self.assertContains(response, "Add at least one job alert criterion.")


class EmployerApplicationFilterTests(TestCase):
    def setUp(self):
        self.employer = User.objects.create_user(
            username="filter-employer@example.com",
            email="filter-employer@example.com",
            password="SecurePass123!",
        )
        Profile.objects.create(user=self.employer, full_name="Employer", role="employer")
        self.company = Company.objects.create(
            owner=self.employer,
            name="Owned Company",
            is_approved=True,
        )
        self.own_job = Job.objects.create(
            company=self.company,
            title="Backend Engineer",
            description="Build and maintain reliable application services.",
        )
        self.other_employer = User.objects.create_user(
            username="other-employer@example.com",
            email="other-employer@example.com",
            password="SecurePass123!",
        )
        self.other_company = Company.objects.create(
            owner=self.other_employer,
            name="Other Company",
            is_approved=True,
        )
        self.other_job = Job.objects.create(
            company=self.other_company,
            title="Private Employer Role",
            description="A role belonging to a different employer account.",
        )

    def make_applicant(self, index, name, skills):
        user = User.objects.create(
            username=f"candidate-{index}@example.com",
            email=f"candidate-{index}@example.com",
            first_name=name.split()[0],
            last_name=" ".join(name.split()[1:]),
        )
        Profile.objects.create(
            user=user,
            full_name=name,
            skills=skills,
            role="job_seeker",
        )
        return user

    def test_filters_search_candidate_skills_and_exclude_other_employers(self):
        python_candidate = self.make_applicant(1, "Priya Python", "Python, Django")
        other_candidate = self.make_applicant(2, "Sam Script", "JavaScript")
        own_application = Application.objects.create(
            job=self.own_job,
            applicant=python_candidate,
            status="shortlisted",
        )
        Application.objects.create(job=self.own_job, applicant=other_candidate)
        private_application = Application.objects.create(
            job=self.other_job,
            applicant=python_candidate,
            status="shortlisted",
        )
        self.client.force_login(self.employer)

        response = self.client.get(
            reverse("manage-applications"),
            {"q": "Django", "status": "shortlisted", "sort": "oldest"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Priya Python")
        self.assertNotContains(response, "Sam Script")
        self.assertNotContains(response, "Private Employer Role")
        self.assertEqual(list(response.context["applications"]), [own_application])
        self.assertEqual(response.context["page_obj"].paginator.count, 1)

        denied = self.client.get(
            reverse("candidate-details"),
            {"application_id": private_application.pk},
        )
        self.assertEqual(denied.status_code, 404)

    def test_demo_job_applications_are_not_in_employer_queue(self):
        demo_job = Job.objects.create(
            company=self.company,
            title="Sample-only role",
            description="This role is a demo and must not enter the real queue.",
            is_demo=True,
        )
        applicant = self.make_applicant(3, "Dana Demo", "Testing")
        Application.objects.create(job=demo_job, applicant=applicant)
        self.client.force_login(self.employer)

        response = self.client.get(reverse("manage-applications"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Sample-only role")

    def test_job_seekers_cannot_open_employer_application_management(self):
        applicant = self.make_applicant(4, "Jordan Seeker", "Writing")
        self.client.force_login(applicant)

        response = self.client.get(reverse("manage-applications"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard"))


class AccountProfileCompletionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="profile-seeker@example.com",
            email="profile-seeker@example.com",
            password="SecurePass123!",
            first_name="Ari",
            last_name="Applicant",
        )
        self.profile = Profile.objects.create(
            user=self.user,
            full_name="Ari Applicant",
            headline="",
            skills="Python",
            role="job_seeker",
        )
        ResumeDraft.objects.create(user=self.user, content={"education": "BSc Computing"})

    def test_dashboard_completion_uses_saved_profile_fields_and_direct_targets(self):
        self.client.force_login(self.user)

        response = self.client.get("/pages/dashboard/jdashboard.html")

        self.assertEqual(response.status_code, 200)
        checks = {
            check["label"]: check
            for check in response.context["account_profile_completion"]
        }
        self.assertTrue(checks["Name added"]["done"])
        self.assertTrue(checks["Account email"]["done"])
        self.assertTrue(checks["Skills listed"]["done"])
        self.assertTrue(checks["Education"]["done"])
        self.assertFalse(checks["Professional headline"]["done"])
        self.assertEqual(checks["Professional headline"]["target"], "headline")
        self.assertFalse(checks["Resume uploaded"]["done"])
        self.assertEqual(checks["Resume uploaded"]["href"], reverse("resume-management"))
        self.assertContains(response, 'id="accountProfileCompletion"')

    def test_profile_save_changes_only_persisted_completion_checks(self):
        self.client.force_login(self.user)

        saved = self.client.post(
            reverse("dashboard-profile-save"),
            {
                "full_name": "Ari Applicant",
                "headline": "Junior Python Developer",
                "location": "Bhopal",
                "skills": "Python, Django",
                "experience": "Built Django applications",
                "education": "BSc Computing",
                "description": "Backend developer focused on maintainable services.",
            },
        )

        self.assertEqual(saved.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.headline, "Junior Python Developer")
        self.assertEqual(self.profile.location, "Bhopal")
        self.assertEqual(self.profile.experience, "Built Django applications")
