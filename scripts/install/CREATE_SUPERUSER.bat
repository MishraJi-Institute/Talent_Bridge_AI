@echo off
setlocal
cd /d "%~dp0..\..\backend\legacy-django"
if not exist ".venv\Scripts\python.exe" (
  echo The project virtual environment is missing. Run START_TALENTBRIDGEAI.bat once, then try again.
  pause
  exit /b 1
)
set DJANGO_ENV=development
set DJANGO_DEBUG=true
".venv\Scripts\python.exe" manage.py ensure_superuser
if errorlevel 1 (echo Superuser setup did not finish. No existing password was reset. & pause & exit /b 1)
pause
