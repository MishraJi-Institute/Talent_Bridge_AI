@echo off
setlocal
cd /d "%~dp0..\.."
if exist "%SystemRoot%\py.exe" (set "PY=py") else (set "PY=python")
%PY% tools\windows_manager.py repair
if errorlevel 1 (echo Repair checks failed. Review logs\setup.log & pause & exit /b 1)
pause
