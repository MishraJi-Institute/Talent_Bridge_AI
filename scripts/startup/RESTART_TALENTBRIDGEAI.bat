@echo off
setlocal
cd /d "%~dp0..\.."
if exist "%SystemRoot%\py.exe" (set "PY=py") else (set "PY=python")
%PY% tools\windows_manager.py restart
if errorlevel 1 (echo Restart failed. Review logs\setup.log and logs\server.log & exit /b 1)
