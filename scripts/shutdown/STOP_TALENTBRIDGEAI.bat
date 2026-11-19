@echo off
setlocal
cd /d "%~dp0..\.."
if exist "%SystemRoot%\py.exe" (set "PY=py") else (set "PY=python")
%PY% tools\windows_manager.py stop
if errorlevel 1 (echo Safe stop did not complete. Review logs\setup.log & pause & exit /b 1)
pause
