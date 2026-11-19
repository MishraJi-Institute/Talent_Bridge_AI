# HTML Template Fixes and Verification

## Issues fixed
- Replaced literal `\\n` text accidentally embedded in `pages/login.html` and `pages/company-signup.html` with actual line breaks.
- Kept Django CSRF tags on server-handled signup, login and logout forms so POST requests remain protected.

## Verification performed
- Inspected all 45 HTML/HTM templates for literal `\\n` sequences; none remain.
- Confirmed server-rendered authentication forms include CSRF tokens.
- ZIP archive integrity and extraction are checked after packaging.

## Important runtime note
Django templates must be served through the Django development server, not VS Code Live Server. Start the app with `python manage.py runserver` and visit the Django route (for example, `/login/`). Opening `pages/login.html` directly on port 5500 will display Django template tags as text because Live Server does not process them.
