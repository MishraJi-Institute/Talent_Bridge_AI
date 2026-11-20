@echo off
rem =============================================================================
rem TalentBridgeAI — kahin se bhi chalao: auto venv, pip install, migrate, live publish, Django start
rem Double-click, Desktop shortcut, Start Menu, ya CMD se kisi bhi folder se — path khud mil jayega
rem =============================================================================
setlocal EnableDelayedExpansion

set "ROOT=%~dp0"
if "!ROOT:~-1!"=="\" set "ROOT=!ROOT:~0,-1!"

call :RESOLVE_ROOT
if errorlevel 1 exit /b 1

cd /d "!ROOT!"
if not exist "!ROOT!\tools\windows_manager.py" (
  echo.
  echo [ERROR] tools\windows_manager.py missing in: !ROOT!
  pause
  exit /b 1
)

set "PY=python"
where py >nul 2>nul && set "PY=py"

echo.
echo ============================================================
echo TalentBridgeAI - FULL AUTO INSTALL + START
echo Project: !ROOT!
echo ============================================================
echo Python packages, database, static files, live publish — sab automatic.
echo.

%PY% "!ROOT!\tools\windows_manager.py" auto
if errorlevel 1 (
  echo.
  echo Startup failed. See logs\setup.log and logs\server.log
  pause
  exit /b 1
)

echo.
echo OK — server chal raha hai. Browser mein site khul chuki honi chahiye.
echo Dubara kahin se chalane ke liye Desktop par shortcut: "TalentBridgeAI START (Auto Install).bat"
exit /b 0

:RESOLVE_ROOT
if exist "!ROOT!\tools\windows_manager.py" exit /b 0

if not "!TALENTBRIDGEAI_ROOT!"=="" (
  set "ROOT=!TALENTBRIDGEAI_ROOT!"
  if exist "!ROOT!\tools\windows_manager.py" exit /b 0
)

set "PTR=%LOCALAPPDATA%\TalentBridgeAI\active_project.txt"
if exist "!PTR!" (
  for /f "usebackq delims=" %%I in ("!PTR!") do set "ROOT=%%I"
  if exist "!ROOT!\tools\windows_manager.py" exit /b 0
)

set "PTR2=%APPDATA%\TalentBridgeAI\active_project.txt"
if exist "!PTR2!" (
  for /f "usebackq delims=" %%I in ("!PTR2!") do set "ROOT=%%I"
  if exist "!ROOT!\tools\windows_manager.py" exit /b 0
)

for %%D in ("E:\Job POrtal\TalentBridgeAI" "%USERPROFILE%\TalentBridgeAI" "%USERPROFILE%\Documents\TalentBridgeAI" "%USERPROFILE%\Desktop\TalentBridgeAI") do (
  if exist "%%~D\tools\windows_manager.py" (
    set "ROOT=%%~D"
    exit /b 0
  )
)

echo.
echo [ERROR] TalentBridgeAI project folder nahi mila.
echo Pehli baar is file ko project folder ke andar se chalao, ya set karo:
echo   TALENTBRIDGEAI_ROOT=full path to TalentBridgeAI
pause
exit /b 1