@echo off
setlocal
cd /d "%~dp0..\.."
set "PY=%CD%\backend\legacy-django\.venv\Scripts\python.exe"
if not exist "%PY%" (
  echo Project virtual environment not found.
  echo Run INSTALL_TALENTBRIDGEAI.bat first, then retry release packaging.
  pause
  exit /b 1
)
"%PY%" tools\package_release.py release --python "%PY%"
if errorlevel 1 (
  echo.
  echo Release creation or verification failed. Review the error above.
  pause
  exit /b 1
)
echo.
echo Verified portable release created under releases.
pause
