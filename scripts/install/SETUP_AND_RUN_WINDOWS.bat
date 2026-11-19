@echo off
rem Backward-compatible first-run installer.
call "%~dp0INSTALL_TALENTBRIDGEAI.bat"
if errorlevel 1 exit /b %errorlevel%
call "%~dp0..\startup\START_TALENTBRIDGEAI.bat"
exit /b %errorlevel%
