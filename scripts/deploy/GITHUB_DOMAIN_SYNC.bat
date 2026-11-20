@echo off
rem Local code -> GitHub main -> domain (Pages + Render auto-deploy)
setlocal
cd /d "%~dp0..\.."
set "PY=python"
where py >nul 2>nul && set "PY=py"

echo.
echo [1/4] GitHub connection...
%PY% tools\ensure_github_remote.py
if errorlevel 1 exit /b 1

echo.
echo [2/4] Pull latest from GitHub...
git pull --rebase origin main
if errorlevel 1 (
  echo Pull failed. Resolve conflicts then run again.
  pause
  exit /b 1
)

echo.
echo [3/4] Optional auto-commit (set TALENTBRIDGEAI_AUTO_COMMIT=1 in .env)...
%PY% tools\git_auto_commit.py

echo.
echo [4/4] Build static + push if ahead (triggers talentbridge.qd.je)...
%PY% tools\publish_live.py
if errorlevel 1 exit /b 1

echo.
echo Done. Local Django = http://127.0.0.1:8000  ^|  Domain = https://talentbridge.qd.je (GitHub Pages)
exit /b 0