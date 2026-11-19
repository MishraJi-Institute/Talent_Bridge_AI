@echo off
setlocal
cd /d "%~dp0..\.."
if exist "%SystemRoot%\py.exe" (set "PY=py") else (set "PY=python")
%PY% tools\package_release.py backup
if errorlevel 1 (
  echo.
  echo Backup failed. See the error above; no success archive was published.
  pause
  exit /b 1
)
echo.
echo Protected backup completed. Keep it on access-controlled storage.
pause
