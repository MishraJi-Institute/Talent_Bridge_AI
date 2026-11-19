@echo off
rem Backward-compatible launcher; use START_TALENTBRIDGEAI.bat for normal startup.
call "%~dp0START_TALENTBRIDGEAI.bat"
exit /b %errorlevel%
