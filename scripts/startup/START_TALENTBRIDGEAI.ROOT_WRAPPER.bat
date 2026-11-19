@echo off
setlocal
call "%~dp0scripts\startup\START_TALENTBRIDGEAI.bat" %*
exit /b %ERRORLEVEL%
