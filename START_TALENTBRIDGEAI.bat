@echo off
rem Double-click from anywhere inside this project — full auto setup, live publish, Django start.
setlocal
cd /d "%~dp0"
set "PY=python"
where py >nul 2>nul && set "PY=py"
echo.
echo ============================================================
echo TalentBridgeAI - FULL AUTO (install + live publish + start)
echo ============================================================
%PY% tools\windows_manager.py auto
if errorlevel 1 (
  echo.
  echo Startup failed. See logs\setup.log and logs\server.log
  pause
  exit /b 1
)
exit /b 0