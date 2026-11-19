# TalentBridge AI — Python/Django Connectivity Pass

## Implemented in this pass
- Corrected Django project-root resolution: templates, root `index.html`, CSS, JavaScript, and image assets are stored at the repository root while `manage.py` is under `legacy-django/`. Django settings and URL serving now point to the correct root.
- Connected sign-in and both registration forms to Django URL names and added CSRF tokens.
- Connected job posting to the existing `create_job` POST view and enabled the wizard's publish submit button.
- Connected contact, profile, company-details, resume, and application forms to their Django views/routes with CSRF tokens.
- Application form now shows the selected job/account values and sends the confirmation flag expected by the application view.
- Profile forms now use profile/user values instead of hard-coded demo data. Profile view returns the appropriate profile/edit template based on route.
- Added Django message display to key form pages so validation and success messages are visible.
- Added `.env.example` without credentials and a Windows launcher (`RUN_DJANGO_WINDOWS.bat`).

## Existing backend features used
- User login/logout and job seeker/employer registration.
- Employer approval checks and job publishing.
- Job search/detail and job application submission.
- Profile and company profile updates.
- Contact inquiry storage.
- Resume upload/download validation.
- Password reset routes and social sign-in start routes.

## Still database/schema dependent
- Persistent saved-job bookmarks (no `SavedJob` model exists yet).
- Notification and interview records (no dedicated models exist yet).
- Admin/candidate management workflows beyond the existing `Application` model.
- External OAuth sign-in requires valid provider credentials in environment variables.

## Static verification performed
- Scanned 56 HTML files for literal `\n` text: none found.
- Python syntax compilation: 21 Python files, no syntax errors.
- HTML parser smoke pass: 56 files, no parser exceptions.
- Verified CSRF tags and Django action routes on the connected forms.
- Final ZIP archive integrity and extraction are checked after packaging.

## Runtime test limitation
Django is not installed in this execution environment, and package installation was unavailable. Therefore `manage.py check`, Django test suite, database migrations, and browser-based responsive/runtime tests could not be executed here. Run these in a Python environment with dependencies installed before production deployment.

## Run locally (Windows)
1. Extract the ZIP.
2. Open the extracted `TalentBridgeAI` folder in VS Code.
3. Run `RUN_DJANGO_WINDOWS.bat`, or manually run commands below.
4. Open `http://127.0.0.1:8000/` (do not use Live Server port 5500 for Django template pages).

Manual commands:
```bat
cd legacy-django
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
py manage.py migrate
py manage.py check
py manage.py test
py manage.py runserver
```
