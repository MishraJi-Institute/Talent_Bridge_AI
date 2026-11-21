@echo off
setlocal
schtasks /Delete /TN "TalentBridgeAI Django Server" /F
schtasks /Delete /TN "TalentBridgeAI Local Development Server" /F
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
if exist "%STARTUP%\TalentBridgeAI_Server_Startup.cmd" del /f /q "%STARTUP%\TalentBridgeAI_Server_Startup.cmd"
if exist "%STARTUP%\TalentBridgeAI_Server_Startup.vbs" del /f /q "%STARTUP%\TalentBridgeAI_Server_Startup.vbs"
echo Automatic Django logon startup disabled. Data and .env are unchanged.
echo Start manually anytime with START_TALENTBRIDGEAI.bat
pause