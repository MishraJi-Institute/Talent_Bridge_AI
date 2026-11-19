@echo off
setlocal EnableExtensions
cd /d "%~dp0..\.."
set "TASK=TalentBridgeAI Django Server"
set "URL=http://127.0.0.1:8000/"
echo ============================================================
echo TalentBridgeAI - persistent local Django server setup
echo ============================================================
where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python 3.11-3.13 and enable PATH.
  pause
  exit /b 1
)
echo Creating a Windows logon task to start Django automatically...
schtasks /Create /TN "%TASK%" /SC ONLOGON /TR "wscript.exe \"%~dp0..\startup\START_TALENTBRIDGEAI_HIDDEN.vbs\"" /F
if errorlevel 1 (
  echo Could not register automatic startup. Run this file as your Windows user.
  pause
  exit /b 1
)
echo Starting Django in the background...
wscript.exe "%~dp0..\startup\START_TALENTBRIDGEAI_HIDDEN.vbs"
echo Waiting for Django health check...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ok=$false; for($i=0;$i -lt 90;$i++){ try{$r=Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8000/' -TimeoutSec 2; if($r.StatusCode -eq 200){$ok=$true;break}}catch{}; Start-Sleep -Seconds 1 }; if($ok){Write-Host 'SERVER HEALTH: HTTP 200'}else{Write-Host 'SERVER DID NOT START. Check logs\setup.log and logs\server.log'; exit 1}"
if errorlevel 1 (
  echo.
  echo Server startup failed. The exact error should be in logs\setup.log or logs\server.log.
  pause
  exit /b 1
)
echo.
echo SUCCESS: Django is running at %URL%
echo It will also start automatically at your next Windows sign-in.
echo Keep this folder in the same location so the scheduled task remains valid.
start "" "%URL%"
pause
