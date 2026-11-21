@echo off
setlocal
cd /d "%~dp0..\.."
if not exist "backend\legacy-django\manage.py" (
  echo ERROR: Run from TalentBridgeAI project root.
  pause
  exit /b 1
)
if exist "backend\legacy-django\.venv\Scripts\python.exe" (
  set "PY=backend\legacy-django\.venv\Scripts\python.exe"
) else (
  set "PY=python"
)
echo.
echo TalentBridge local admin password reset
echo - Or set LOCAL_ADMIN_BOOTSTRAP_PASSWORD in .env then run this once.
echo - Or enter a new password when prompted below.
echo.
"%PY%" "backend\legacy-django\manage.py" reset_local_admin
if errorlevel 1 goto failed
echo.
echo Open: http://127.0.0.1:8000/admin/login/
pause
exit /b 0
:failed
pause
exit /b 1