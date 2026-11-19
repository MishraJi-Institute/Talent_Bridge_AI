from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.template import engines
from django.test import Client, SimpleTestCase, override_settings
from django.test.client import RequestFactory

from .dev_preview import LivePreviewMiddleware, source_fingerprints
from .dev_preview_views import _template_errors


class LivePreviewTests(SimpleTestCase):
    def test_source_fingerprints_skip_environment_and_collected_static_directories(self):
        with TemporaryDirectory() as temporary_root:
            project_root = Path(temporary_root)
            app_root = project_root / 'legacy-django'
            for directory in (
                project_root / 'css',
                project_root / 'js',
                project_root / 'images',
                project_root / 'logo',
                project_root / 'videos',
                project_root / 'pages',
            ):
                directory.mkdir(parents=True)
            (project_root / 'css' / 'style.css').write_text('body {}', encoding='utf-8')
            (project_root / 'js' / 'app.js').write_text('void 0;', encoding='utf-8')
            (app_root / 'jobs').mkdir(parents=True)
            (app_root / 'jobs' / 'views.py').write_text('def view(): pass', encoding='utf-8')
            (app_root / '.venv' / 'Lib').mkdir(parents=True)
            (app_root / '.venv' / 'Lib' / 'installed.py').write_text('package = True', encoding='utf-8')
            (app_root / 'staticfiles').mkdir()
            (app_root / 'staticfiles' / 'collected.py').write_text('asset = True', encoding='utf-8')

            with override_settings(PROJECT_ROOT=project_root, BASE_DIR=app_root):
                _fingerprints, counts, _missing_roots, _source_files = source_fingerprints()

        self.assertEqual(counts['scripts'], 1)
        self.assertEqual(counts['styles'], 1)
        self.assertEqual(counts['backend'], 1)

    @override_settings(DEBUG=True)
    def test_dashboard_and_state_are_available_in_development(self):
        client = Client()

        dashboard = client.get('/__dev__/')
        self.assertEqual(dashboard.status_code, 200)
        self.assertContains(dashboard, 'Live preview')

        state = client.get('/__dev__/state/')
        self.assertEqual(state.status_code, 200)
        self.assertEqual(state.json()['server']['mode'], 'development')
        self.assertIn('styles', state.json()['fingerprints'])

    @override_settings(DEBUG=True)
    def test_state_uses_request_origin_and_port(self):
        response = Client().get('/__dev__/state/', HTTP_HOST='localhost:8001')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('application/json'))
        state = response.json()
        self.assertEqual(state['server']['url'], 'http://localhost:8001/')
        self.assertEqual(state['server']['status'], 'ok')
        self.assertEqual(state['frontend']['status'], 'ok')

    @override_settings(DEBUG=False)
    def test_preview_endpoints_are_hidden_outside_development(self):
        client = Client()
        self.assertEqual(client.get('/__dev__/').status_code, 404)
        self.assertEqual(client.get('/__dev__/state/').status_code, 404)

    def test_template_check_ignores_templates_outside_the_project(self):
        with TemporaryDirectory() as external_app:
            template_root = Path(external_app) / 'templates'
            template_root.mkdir()
            (template_root / 'invalid.html').write_text(
                '{% load missing_external_library %}',
                encoding='utf-8',
            )
            app_config = SimpleNamespace(path=external_app)
            engines['django']
            with patch(
                'jobs.dev_preview_views.apps.get_app_configs',
                return_value=[app_config],
            ):
                errors = _template_errors()

        self.assertFalse(any(
            'missing_external_library' in error['message']
            for error in errors
        ))

    def test_middleware_injects_refresh_script_into_html_only(self):
        middleware = LivePreviewMiddleware(
            lambda request: HttpResponse('<html><body>ok</body></html>')
        )
        response = middleware(RequestFactory().get('/'))

        self.assertIn(b'/js/core/dev-preview.js?v=', response.content)
        self.assertIn(b'</body>', response.content)

        plain_response = LivePreviewMiddleware(
            lambda request: HttpResponse('ok', content_type='text/plain')
        )(RequestFactory().get('/'))
        self.assertNotIn(b'dev-preview.js', plain_response.content)
