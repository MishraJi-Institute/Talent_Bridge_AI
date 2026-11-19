from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import parse_qs, urlparse
from zipfile import ZIP_DEFLATED, ZipFile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import Profile, ResumeDraft


User = get_user_model()


class ResumeUploadAcceptanceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='resume-candidate@example.com',
            email='resume-candidate@example.com',
            password='SecurePass123!',
        )
        self.client.force_login(self.user)

    def test_resume_page_exposes_the_account_upload_workflow(self):
        response = self.client.get(reverse('resume-management'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No resume uploaded yet')
        self.assertContains(response, 'enctype="multipart/form-data"')
        self.assertContains(response, 'name="resume"')
        self.assertContains(response, 'required')
        self.assertContains(response, 'Maximum file size: 5 MB')
        self.assertNotContains(response, 'Choose a resume for preview')

    def test_resume_library_sign_out_uses_post(self):
        response = self.client.get(reverse('resume-management'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'action="/logout/"')
        self.assertContains(response, 'class="tb-logout-button" type="submit">Sign out')
        self.assertNotContains(response, 'href="/logout/"')

    def test_resume_library_requires_authentication(self):
        self.client.logout()

        response = self.client.get(reverse('resume-management'))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))
        self.assertEqual(
            parse_qs(urlparse(response.url).query).get('next'),
            [reverse('resume-management')],
        )

    def test_valid_pdf_upload_can_be_downloaded(self):
        pdf_content = b'%PDF-1.4\nTalentBridgeAI test resume\n'
        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            response = self.client.post(
                reverse('resume-management'),
                {
                    'resume': SimpleUploadedFile(
                        'candidate.pdf',
                        pdf_content,
                        content_type='application/pdf',
                    ),
                },
            )

            self.assertRedirects(response, reverse('resume-management'), fetch_redirect_response=False)
            profile = Profile.objects.get(user=self.user)
            self.assertTrue(profile.resume.name.endswith('candidate.pdf'))
            with profile.resume.open('rb') as uploaded:
                self.assertEqual(uploaded.read(), pdf_content)

            download = self.client.get(reverse('resume_download'))
            self.assertEqual(download.status_code, 200)
            self.assertEqual(b''.join(download.streaming_content), pdf_content)

    def test_pdf_preview_is_inline_and_private(self):
        pdf_content = b'%PDF-1.4\nTalentBridgeAI test resume\n'
        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            self.client.post(
                reverse('resume-management'),
                {'resume': SimpleUploadedFile('candidate.pdf', pdf_content, content_type='application/pdf')},
            )

            preview = self.client.get(reverse('resume_preview'))

            self.assertEqual(preview.status_code, 200)
            self.assertEqual(preview['Content-Type'], 'application/pdf')
            self.assertTrue(preview['Content-Disposition'].startswith('inline;'))
            self.assertEqual(preview['X-Content-Type-Options'], 'nosniff')
            self.assertEqual(b''.join(preview.streaming_content), pdf_content)

            self.client.logout()
            denied = self.client.get(reverse('resume_preview'))
            self.assertEqual(denied.status_code, 302)
            other_user = User.objects.create_user(
                username='another-candidate@example.com',
                email='another-candidate@example.com',
                password='SecurePass123!',
            )
            self.client.force_login(other_user)
            self.assertEqual(self.client.get(reverse('resume_preview')).status_code, 404)

    def test_doc_and_docx_uploads_are_supported(self):
        docx_content = BytesIO()
        with ZipFile(docx_content, 'w', compression=ZIP_DEFLATED) as document:
            document.writestr('[Content_Types].xml', '<Types/>')
            document.writestr('word/document.xml', '<document/>')

        uploads = (
            ('candidate.doc', bytes.fromhex('D0CF11E0A1B11AE1') + b'document', 'application/msword'),
            (
                'candidate.docx',
                docx_content.getvalue(),
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            ),
        )
        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            for filename, content, content_type in uploads:
                with self.subTest(filename=filename):
                    response = self.client.post(
                        reverse('resume-management'),
                        {'resume': SimpleUploadedFile(filename, content, content_type=content_type)},
                    )

                    self.assertRedirects(
                        response,
                        reverse('resume-management'),
                        fetch_redirect_response=False,
                    )
                    self.assertTrue(Profile.objects.get(user=self.user).resume.name.endswith(filename))

            self.assertEqual(self.client.get(reverse('resume_preview')).status_code, 404)

    def test_resume_can_be_replaced_and_deleted(self):
        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            for filename, content in (
                ('first.pdf', b'%PDF-1.4\nfirst resume'),
                ('replacement.pdf', b'%PDF-1.4\nreplacement resume'),
            ):
                response = self.client.post(
                    reverse('resume-management'),
                    {'resume': SimpleUploadedFile(filename, content, content_type='application/pdf')},
                )
                self.assertRedirects(
                    response,
                    reverse('resume-management'),
                    fetch_redirect_response=False,
                )
                profile = Profile.objects.get(user=self.user)
                self.assertTrue(profile.resume.name.endswith(filename))
                if filename == 'replacement.pdf':
                    self.assertFalse((Path(media_root) / 'resumes' / 'first.pdf').exists())

            stored_path = Path(media_root) / profile.resume.name
            deleted = self.client.post(reverse('resume_delete'))

            self.assertRedirects(
                deleted,
                reverse('resume-management'),
                fetch_redirect_response=False,
            )
            profile.refresh_from_db()
            self.assertFalse(profile.resume)
            self.assertFalse(stored_path.exists())
            self.assertContains(self.client.get(reverse('resume-management')), 'No resume uploaded yet')

    def test_upload_rejects_mismatched_format_and_files_over_five_mb(self):
        uploads = (
            (
                'candidate.txt',
                b'%PDF-1.4\nnot accepted by extension',
                'Upload a PDF, DOC or DOCX file no larger than 5 MB.',
            ),
            (
                'candidate.pdf',
                b'not a PDF document',
                'The file contents do not match the selected resume format.',
            ),
            (
                'large.pdf',
                b'%PDF-1.4\n' + (b'x' * (5 * 1024 * 1024)),
                'Upload a PDF, DOC or DOCX file no larger than 5 MB.',
            ),
        )
        for filename, content, expected_message in uploads:
            with self.subTest(filename=filename):
                response = self.client.post(
                    reverse('resume-management'),
                    {
                        'resume': SimpleUploadedFile(
                            filename,
                            content,
                            content_type='application/octet-stream',
                        ),
                    },
                    follow=True,
                )

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, expected_message)
                self.assertFalse(Profile.objects.get(user=self.user).resume)


class ResumeBuilderAcceptanceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="builder-candidate@example.com",
            email="builder-candidate@example.com",
            password="SecurePass123!",
        )

    def test_resume_builder_requires_authentication(self):
        response = self.client.get(reverse("resume-builder"))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/login/"))
        self.assertIn("next=/resume-builder/", response.url)

    def test_builder_prefills_profile_and_discloses_ai_unavailability(self):
        Profile.objects.create(
            user=self.user,
            full_name="Resume Candidate",
            headline="Product Designer",
            skills="Research, Figma",
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("resume-builder"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="Resume Candidate"')
        self.assertContains(response, "AI ASSIST UNAVAILABLE")
        self.assertContains(response, "Live resume preview")
        self.assertContains(response, "Print / Save as PDF")
        self.assertContains(response, "Research")
        self.assertContains(response, reverse("resume-management"))

    def test_saved_draft_persists_and_escapes_preview_content(self):
        self.client.force_login(self.user)
        form_data = {
            "full_name": "Avery Candidate",
            "headline": "Software Engineer",
            "email": self.user.email,
            "phone": "555-0100",
            "location": "Bhopal",
            "summary": "<script>alert(1)</script>",
            "skills": "Python, Django",
            "experience": "Software Engineer | Example Co",
            "education": "BSc Computer Science",
            "links": "https://example.com",
        }

        response = self.client.post(reverse("resume-builder"), form_data)

        self.assertRedirects(response, reverse("resume-builder"))
        draft = ResumeDraft.objects.get(user=self.user)
        self.assertEqual(draft.content["full_name"], "Avery Candidate")
        self.assertEqual(draft.content["summary"], form_data["summary"])
        response = self.client.get(reverse("resume-builder"))
        self.assertContains(response, 'value="Avery Candidate"')
        self.assertContains(response, "&lt;script&gt;alert(1)&lt;/script&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertContains(response, "Your saved draft is ready to edit.")

    def test_invalid_builder_submission_does_not_create_a_draft(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("resume-builder"),
            {"full_name": "Avery Candidate", "email": "not-an-email"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a valid email address.")
        self.assertFalse(ResumeDraft.objects.filter(user=self.user).exists())


class SmartProfileCardAcceptanceTests(TestCase):
    def test_job_seeker_dashboard_renders_smart_profile_card(self):
        user = User.objects.create_user(
            username='smart-card-candidate@example.com',
            email='smart-card-candidate@example.com',
            password='SecurePass123!',
        )
        Profile.objects.create(user=user, full_name='Smart Card Candidate', role='job_seeker')
        self.client.force_login(user)

        response = self.client.get('/pages/dashboard/jdashboard.html')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="page-smartcard"')
        self.assertContains(response, 'id="smartCard"')
        self.assertContains(response, 'jdashboard.js')

    def test_account_applications_and_browser_demo_tracker_are_separate(self):
        user = User.objects.create_user(
            username='application-tracker-candidate@example.com',
            email='application-tracker-candidate@example.com',
            password='SecurePass123!',
        )
        self.client.force_login(user)

        response = self.client.get('/pages/dashboard/jdashboard.html')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-account-application-rows="1"')
        self.assertContains(response, 'id="applicationList"')
        self.assertContains(response, 'Account applications')
        self.assertContains(response, 'id="demoApplicationList"')
        self.assertContains(response, 'Sample tracker (this browser)')
        self.assertContains(response, 'DEMO DATA')

    def test_dashboard_bootstraps_smart_profile_from_account_data(self):
        user = User.objects.create_user(
            username='profile-bootstrap@example.com',
            email='profile-bootstrap@example.com',
            password='SecurePass123!',
        )
        Profile.objects.create(
            user=user,
            full_name='Profile Bootstrap',
            headline='Product Designer',
            location='Bhopal',
            skills='Research, Prototyping',
            experience='Three years',
            bio='Designing clear product experiences.',
        )
        self.client.force_login(user)

        response = self.client.get('/pages/dashboard/jdashboard.html')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-account-name="Profile Bootstrap"')
        self.assertContains(response, 'data-account-headline="Product Designer"')
        self.assertContains(response, 'data-account-location="Bhopal"')
        self.assertContains(response, 'data-account-skills="Research, Prototyping"')
        self.assertContains(response, 'data-account-experience="Three years"')
        self.assertContains(response, 'data-account-bio="Designing clear product experiences."')
        self.assertContains(response, 'readonly aria-describedby="account-email-note"')


class DashboardProfileSaveAcceptanceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='profile-save@example.com',
            email='profile-save@example.com',
            password='SecurePass123!',
        )
        self.profile = Profile.objects.create(
            user=self.user,
            full_name='Original Name',
            headline='Original headline',
        )
        self.client.force_login(self.user)

    def test_dashboard_profile_save_updates_account_profile_and_identity(self):
        response = self.client.post(
            '/dashboard/profile/save/',
            {
                'full_name': 'Taylor Candidate',
                'headline': 'Early-career developer',
                'location': 'Indore',
                'skills': 'Python, Django',
                'experience': 'Open-source contributor',
                'description': 'Building accessible web products.',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'ok': True})
        self.profile.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(self.profile.full_name, 'Taylor Candidate')
        self.assertEqual(self.profile.headline, 'Early-career developer')
        self.assertEqual(self.profile.location, 'Indore')
        self.assertEqual(self.profile.skills, 'Python, Django')
        self.assertEqual(self.profile.experience, 'Open-source contributor')
        self.assertEqual(self.profile.bio, 'Building accessible web products.')
        self.assertEqual(self.user.get_full_name(), 'Taylor Candidate')
        self.assertEqual(self.user.email, 'profile-save@example.com')

    def test_dashboard_profile_save_rejects_empty_name_without_mutating_data(self):
        response = self.client.post(
            '/dashboard/profile/save/',
            {
                'full_name': ' ',
                'headline': 'Changed headline',
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Enter your full name.'})
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.full_name, 'Original Name')
        self.assertEqual(self.profile.headline, 'Original headline')

    def test_dashboard_profile_save_requires_authentication(self):
        self.client.logout()

        response = self.client.post(
            '/dashboard/profile/save/',
            {'full_name': 'Unauthorized Change'},
        )

        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.full_name, 'Original Name')

    def test_dashboard_profile_save_requires_a_valid_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        save_url = '/dashboard/profile/save/'

        rejected = client.post(save_url, {'full_name': 'CSRF Check'})
        self.assertEqual(rejected.status_code, 403)

        page = client.get('/pages/dashboard/jdashboard.html')
        csrf_token = page.cookies['csrftoken'].value
        accepted = client.post(
            save_url,
            {'full_name': 'CSRF Check'},
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(accepted.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.full_name, 'CSRF Check')
