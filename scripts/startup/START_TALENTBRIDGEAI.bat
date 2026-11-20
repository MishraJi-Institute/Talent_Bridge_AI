@echo off
rem Wrapper — asli auto-install file project root par hai
setlocal
call "%~dp0..\..\START_TALENTBRIDGEAI.bat" %*
exit /b %ERRORLEVEL%