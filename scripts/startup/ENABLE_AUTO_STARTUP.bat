@echo off
setlocal
set "TASK=TalentBridgeAI Local Development Server"
schtasks /Create /TN "%TASK%" /SC ONLOGON /TR "\"%~dp0START_TALENTBRIDGEAI.bat\"" /F
if errorlevel 1 (echo Could not create task. Run this file as your Windows user and check Task Scheduler permissions.) else echo Automatic startup enabled. Disable with DISABLE_AUTO_STARTUP.bat.
pause
