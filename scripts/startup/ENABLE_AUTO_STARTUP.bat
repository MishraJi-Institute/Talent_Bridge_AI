@echo off
setlocal
cd /d "%~dp0..\.."
call "%~dp0..\..\FIX_SERVER_PERMANENTLY.bat"
exit /b %ERRORLEVEL%