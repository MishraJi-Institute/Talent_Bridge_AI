@echo off
setlocal
cd /d "%~dp0..\.."
if not exist "backend\legacy-django\manage.py" (
  echo ERROR: Open this batch file from the extracted TalentBridgeAI project root.
  pause
  exit /b 1
)
if exist "backend\legacy-django\.venv\Scripts\python.exe" (
  set "PY=backend\legacy-django\.venv\Scripts\python.exe"
) else (
  set "PY=python"
)
echo [1/3] Checking database migrations...
"%PY%" "backend\legacy-django\manage.py" migrate --noinput
if errorlevel 1 goto failed
echo.
echo [2/3] Checking or creating the first superuser...
"%PY%" "backend\legacy-django\manage.py" ensure_admin_account
if errorlevel 1 goto failed
echo.
echo [3/3] Starting TalentBridgeAI and checking server health...
call "START_TALENTBRIDGEAI.bat"
exit /b %errorlevel%
:failed
echo.
echo Setup stopped safely. Existing users and database were not deleted.
echo See logs\setup.log and logs\server.log if available.
pause
exit /b 1
