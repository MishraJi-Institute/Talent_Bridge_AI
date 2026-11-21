@echo off
setlocal EnableExtensions
cd /d "%~dp0..\.."
set "ROOT=%CD%"
set "URL=http://127.0.0.1:8000/"
echo ============================================================
echo TalentBridgeAI - permanent local server (Windows sign-in)
echo ============================================================
echo.
echo This registers Django to start automatically after every
echo Windows sign-in — even if you move this folder later, run
echo START_TALENTBRIDGEAI.bat once after a move to refresh paths.
echo.
where python >nul 2>nul && set "PY=python" || (
  echo Python was not found. Install Python 3.11-3.13 and enable PATH.
  pause
  exit /b 1
)
where py >nul 2>nul && set "PY=py"
echo Registering auto-start and starting Django now...
"%PY%" "%ROOT%\tools\windows_manager.py" logon_start
if errorlevel 1 (
  echo.
  echo Setup failed. See logs\setup.log and logs\server.log
  pause
  exit /b 1
)
echo.
echo Waiting for health check at %URL%admin/login/ ...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ok=$false; for($i=0;$i -lt 90;$i++){ try{$r=Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8000/admin/login/' -TimeoutSec 2; if($r.StatusCode -eq 200){$ok=$true;break}}catch{}; Start-Sleep -Seconds 1 }; if($ok){Write-Host 'SERVER HEALTH: admin login HTTP 200'}else{Write-Host 'SERVER DID NOT START. Check logs\setup.log and logs\server.log'; exit 1}"
if errorlevel 1 (
  pause
  exit /b 1
)
echo.
echo SUCCESS: Django is running. Admin: %URL%admin/login/
echo After reboot, wait about 1 minute, then open the same admin URL.
echo To turn off auto-start: scripts\shutdown\DISABLE_AUTO_SERVER_STARTUP.bat
start "" "%URL%admin/login/"
pause