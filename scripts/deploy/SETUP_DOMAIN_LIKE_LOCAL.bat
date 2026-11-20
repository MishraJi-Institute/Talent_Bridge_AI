@echo off
setlocal
cd /d "%~dp0..\.."
echo.
echo ============================================================
echo Domain = local jaisa (Django + database on app.talentbridge.qd.je)
echo ============================================================
echo.
echo GitHub Pages (talentbridge.qd.je) = sirf static pages.
echo Full work (DB, login, jobs)     = app.talentbridge.qd.je (Django + Postgres).
echo.
echo Steps:
echo   1. Render Blueprint connect (render.yaml in this repo)
echo   2. DNS: app.talentbridge.qd.je CNAME -^> talentbridge-ai.onrender.com
echo   3. Google OAuth for https://app.talentbridge.qd.je
echo   4. START_TALENTBRIDGEAI.bat for local; push main for Pages + Render deploy
echo.
echo Doc: docs\setup\DOMAIN_LIKE_LOCAL.md
echo.
start "" "https://dashboard.render.com/blueprint/new?repo=https://github.com/MishraJi-Institute/Talent_Bridge_AI"
timeout /t 2 >nul
start "" notepad "%~dp0..\..\docs\setup\DOMAIN_LIKE_LOCAL.md"
set "PY=python"
where py >nul 2>nul && set "PY=py"
%PY% tools\publish_live.py
pause