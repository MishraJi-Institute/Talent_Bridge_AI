@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0CONNECT_GOOGLE_OAUTH.ps1" %*
exit /b %errorlevel%


