@echo off
setlocal
cd /d "%~dp0..\.."
set "PY=python"
where py >nul 2>nul && set "PY=py"
%PY% tools\windows_manager.py start
if errorlevel 1 (
  echo.
  echo ============================================================
  echo TalentBridgeAI did not start successfully.
  echo Read the exact error above and the logs below:
  echo   logs\setup.log
  echo   logs\server.log
  echo Run DIAGNOSE_TALENTBRIDGEAI.bat to create a diagnostic report.
  echo ============================================================
  pause
  exit /b 1
)
echo.
echo TalentBridgeAI launcher finished. If Django is running, keep its server terminal open.
