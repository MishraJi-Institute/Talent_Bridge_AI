@echo off
setlocal
call "%~dp0scripts\shutdown\STOP_TALENTBRIDGEAI.bat" %*
exit /b %ERRORLEVEL%

