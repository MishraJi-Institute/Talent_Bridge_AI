@echo off
setlocal
cd /d "%~dp0..\.."
set "PY=python"
where py >nul 2>nul && set "PY=py"
if not exist logs mkdir logs
%PY% tools\diagnose_windows.py
 echo.
echo Diagnostic report: logs\diagnostic_report.txt
pause
