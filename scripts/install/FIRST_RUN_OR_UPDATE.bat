@echo off
setlocal
cd /d "%~dp0..\.."
echo ============================================================
echo TalentBridgeAI - automatic setup and start
echo ============================================================
set "PY=python"
where py >nul 2>nul && set "PY=py"
%PY% tools\windows_manager.py install
if errorlevel 1 (
  echo Setup failed. See logs\setup.log
  pause
  exit /b 1
)
%PY% tools\windows_manager.py start
if errorlevel 1 (
  echo Start failed. See logs\setup.log and logs\server.log
  pause
  exit /b 1
)
echo Setup and start completed.
pause
