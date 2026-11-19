@echo off
setlocal
cd /d "%~dp0..\.."
if exist "%SystemRoot%\py.exe" (set "PY=py") else (set "PY=python")
echo [1/2] Installing and checking TalentBridgeAI...
%PY% tools\windows_manager.py install
if errorlevel 1 (echo Installation failed. Review logs\setup.log & pause & exit /b 1)
echo.
echo [2/2] Starting TalentBridgeAI and verifying login/admin/static assets...
%PY% tools\windows_manager.py start
if errorlevel 1 (echo Startup failed. Review logs\setup.log and logs\server.log & pause & exit /b 1)
