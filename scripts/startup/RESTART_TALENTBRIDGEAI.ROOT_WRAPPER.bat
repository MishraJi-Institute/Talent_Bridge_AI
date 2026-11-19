@echo off
setlocal
call "%~dp0scripts\startup\RESTART_TALENTBRIDGEAI.bat" %*
exit /b %ERRORLEVEL%
