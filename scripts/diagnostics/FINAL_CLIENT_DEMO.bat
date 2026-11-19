@echo off
setlocal
cd /d "%~dp0..\.."
echo ==========================================
echo       TALENTBRIDGE AI - CLIENT DEMO
echo ==========================================
echo.
echo This starts the Django application on port 8000.
echo Existing .env and SQLite database are preserved.
echo.
if not exist ".env" (
  echo WARNING: .env is missing. Google OAuth will require credentials.
)
call "%~dp0..\startup\RUN_DJANGO_WINDOWS.bat"
