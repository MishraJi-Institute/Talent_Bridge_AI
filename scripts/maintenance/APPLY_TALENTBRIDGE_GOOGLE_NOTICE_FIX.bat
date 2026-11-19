@echo off
setlocal
cd /d "%~dp0..\.."
title TalentBridge AI - Apply Google notice fix

if not exist "backend\legacy-django\manage.py" (
  echo ERROR: Put this BAT in the main TalentBridgeAI project folder,
  echo next to the legacy-django folder and START_TALENTBRIDGEAI.bat.
  pause
  exit /b 1
)

echo Applying the Google OAuth notice fix to this project...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$ErrorActionPreference='Stop';" ^
 "$root=(Get-Location).Path;" ^
 "$dirs=@((Join-Path $root 'pages'),(Join-Path $root 'templates'),(Join-Path $root 'backend\legacy-django\templates'));" ^
 "$files=@(); foreach($d in $dirs){ if(Test-Path $d){ $files += Get-ChildItem -Path $d -Recurse -File -Filter '*.html' } };" ^
 "$changed=0;" ^
 "foreach($f in $files){ $s=[IO.File]::ReadAllText($f.FullName); $old=$s;" ^
 " $s=[regex]::Replace($s,'(?is)<p\b[^>]*>\s*Google\s+(?:sign-in|signup)\s+is\s+not\s+configured\..*?</p>','');" ^
 " $s=[regex]::Replace($s,'(?is)<div\b[^>]*class\s*=\s*[''\""][^''\""]*(?:google|oauth)[^''\""]*[''\""][^>]*>\s*Google\s+(?:sign-in|signup)\s+is\s+not\s+configured\..*?</div>','');" ^
 " if($s -ne $old){ $backup=$f.FullName+'.before-google-notice-fix.bak'; if(!(Test-Path $backup)){[IO.File]::WriteAllText($backup,$old,[Text.UTF8Encoding]::new($false))}; [IO.File]::WriteAllText($f.FullName,$s,[Text.UTF8Encoding]::new($false)); $changed++ }" ^
 "}; Write-Host ('Updated HTML files: '+$changed);"
if errorlevel 1 (
  echo Patch failed. No server restart was attempted.
  pause
  exit /b 1
)

echo.
echo The old credential warning has been removed from project HTML templates.
echo The Google button will still require valid Google Cloud credentials to work.
echo.
if exist "STOP_TALENTBRIDGEAI.bat" call "STOP_TALENTBRIDGEAI.bat"
if exist "START_TALENTBRIDGEAI.bat" (
  call "START_TALENTBRIDGEAI.bat"
) else (
  echo START_TALENTBRIDGEAI.bat not found. Restart Django using your normal launcher.
)
pause
