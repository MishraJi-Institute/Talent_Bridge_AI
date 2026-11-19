@echo off
setlocal
schtasks /Delete /TN "TalentBridgeAI Local Development Server" /F
if errorlevel 1 echo Task was not found or could not be removed.
pause
