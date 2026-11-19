@echo off
setlocal
cd /d "%~dp0..\.."
if exist "%SystemRoot%\py.exe" (set "PY=py") else (set "PY=python")
%PY% tools\windows_manager.py open
if not errorlevel 1 exit /b 0

echo.
echo Django is not currently healthy on port 8000.
echo Starting the managed Django server now. Keep this window open.
echo.
%PY% tools\windows_manager.py start
if errorlevel 1 (
  echo.
  echo Django startup failed. Review logs\setup.log and logs\server.log.
  pause
  exit /b 1
)
