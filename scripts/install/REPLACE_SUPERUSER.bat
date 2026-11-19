@echo off
setlocal
cd /d "%~dp0..\.."
if not exist "backend\legacy-django\manage.py" (
  echo ERROR: Open this from the TalentBridgeAI project root.
  pause
  exit /b 1
)
if exist "backend\legacy-django\.venv\Scripts\python.exe" (
  set "PY=backend\legacy-django\.venv\Scripts\python.exe"
) else (
  set "PY=python"
)
echo Applying migrations before changing admin account...
"%PY%" "backend\legacy-django\manage.py" migrate --noinput
if errorlevel 1 goto failed
"%PY%" "backend\legacy-django\manage.py" replace_superuser
if errorlevel 1 goto failed
echo.
echo DONE. Use the new admin username and password at:
echo http://127.0.0.1:8000/admin/login/
pause
exit /b 0
:failed
echo.
echo FAILED. No password is printed or saved in a plain-text file.
pause
exit /b 1
