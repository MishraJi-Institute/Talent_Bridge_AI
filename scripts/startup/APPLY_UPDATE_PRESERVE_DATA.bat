@echo off
setlocal
cd /d "%~dp0..\.."
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0APPLY_UPDATE_PRESERVE_DATA.ps1"
if errorlevel 1 (
  echo Update did not complete. Your original project folder was not deleted.
  pause
  exit /b 1
)
