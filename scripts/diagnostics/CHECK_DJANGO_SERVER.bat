@echo off
cd /d "%~dp0..\.."
python tools\windows_manager.py status
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command "try{$r=Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8000/' -TimeoutSec 3; Write-Host ('Homepage HTTP: '+$r.StatusCode)}catch{Write-Host 'Homepage: NOT REACHABLE'; Write-Host $_.Exception.Message}"
pause
