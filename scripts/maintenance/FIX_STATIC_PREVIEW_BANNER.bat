@echo off
setlocal
cd /d "%~dp0..\.."
echo Removing the static-preview notice from generated site files...
if exist "js\demo-forms.js" (
  echo Source file found.
) else (
  echo ERROR: js\demo-forms.js was not found. Run this from the TalentBridgeAI project root.
  pause
  exit /b 1
)
if exist "%SystemRoot%\py.exe" (
  py tools\build_static.py
) else (
  python tools\build_static.py
)
if errorlevel 1 (
  echo.
  echo Static rebuild failed. See the error above.
  pause
  exit /b 1
)
echo.
echo SUCCESS: static-preview notice injection has been removed.
echo Authentication forms still forward to Django on port 8000.
echo Open the actual website at http://127.0.0.1:8000/
echo.
pause
