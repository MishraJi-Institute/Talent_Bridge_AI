@echo off
setlocal EnableExtensions
cd /d "%~dp0..\.."
title TalentBridgeAI - Server Repair
echo ============================================================
echo TalentBridgeAI - Start and keep Django running
echo ============================================================
if not exist "START_TALENTBRIDGEAI.bat" (
  echo ERROR: This file must be placed in the main TalentBridgeAI project folder,
  echo beside START_TALENTBRIDGEAI.bat.
  pause
  exit /b 1
)
if not exist "tools\windows_manager.py" (
  echo ERROR: tools\windows_manager.py is missing. Extract the complete project ZIP.
  pause
  exit /b 1
)
where py >nul 2>nul
if errorlevel 1 (
  where python >nul 2>nul
  if errorlevel 1 (
    echo ERROR: Python is not installed or not on PATH.
    echo Install Python 3.11, 3.12, or 3.13, then run this file again.
    pause
    exit /b 1
  )
)
echo.
echo [1/3] Registering automatic start at Windows sign-in...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$ErrorActionPreference='Stop'; $root=(Get-Location).Path; $vbs=Join-Path $root 'START_TALENTBRIDGEAI_HIDDEN.vbs'; if(!(Test-Path $vbs)){ throw 'START_TALENTBRIDGEAI_HIDDEN.vbs is missing. Use the latest project package.' }; $exe=Join-Path $env:SystemRoot 'System32\wscript.exe'; $action=New-ScheduledTaskAction -Execute $exe -Argument ('"{0}"' -f $vbs) -WorkingDirectory $root; $trigger=New-ScheduledTaskTrigger -AtLogOn -User ($env:USERDOMAIN+'\'+$env:USERNAME); $settings=New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit ([TimeSpan]::Zero); Register-ScheduledTask -TaskName 'TalentBridgeAI Django Server' -Action $action -Trigger $trigger -Settings $settings -Description 'Starts the local TalentBridgeAI Django server at Windows sign-in.' -Force | Out-Null; Write-Host 'Automatic startup task registered.'"
if errorlevel 1 (
  echo Could not register the Windows startup task. Check Windows Task Scheduler permissions.
  pause
  exit /b 1
)
echo.
echo [2/3] Starting Django in the background...
wscript.exe "%~dp0START_TALENTBRIDGEAI_HIDDEN.vbs"
if errorlevel 1 (
  echo ERROR: Could not launch the hidden Django startup process.
  pause
  exit /b 1
)
echo.
echo [3/3] Waiting for the real Django homepage to return HTTP 200...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$ok=$false; for($i=0;$i -lt 120;$i++){ try{$r=Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8000/' -TimeoutSec 2; if($r.StatusCode -eq 200){$ok=$true;break}}catch{}; Start-Sleep -Seconds 1 }; if($ok){Write-Host 'SUCCESS: Django homepage returned HTTP 200.' -ForegroundColor Green; exit 0}else{Write-Host 'FAILED: Django did not start within 120 seconds.' -ForegroundColor Red; Write-Host 'Read logs\setup.log and logs\server.log in this project folder.'; exit 1}"
if errorlevel 1 (
  echo.
  echo SERVER START FAILED. Do not keep refreshing Firefox.
  echo Open logs\setup.log and logs\server.log and share those files for diagnosis.
  pause
  exit /b 1
)
echo.
echo SUCCESS: http://127.0.0.1:8000/ is responding.
echo Automatic startup is registered for future Windows sign-ins.
start "" "http://127.0.0.1:8000/"
echo.
pause
