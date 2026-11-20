@echo off
setlocal
cd /d "%~dp0..\.."
echo.
echo ============================================================
echo TalentBridgeAI - LIVE website fix (wrong Render app)
echo ============================================================
echo.
echo Problem: talentbridge-ai.onrender.com shows a DIFFERENT Django
echo project (api/token URLs). This repo has /auth/social/google/.
echo.
echo Automatic fix steps:
echo   1. Opening Render Blueprint for THIS GitHub repo...
echo   2. Pushing latest code to GitHub (Pages rebuild)...
echo.
start "" "https://dashboard.render.com/blueprint/new?repo=https://github.com/MishraJi-Institute/Talent_Bridge_AI"
timeout /t 2 >nul
start "" "https://github.com/MishraJi-Institute/Talent_Bridge_AI/actions"
git push origin main
echo.
echo In Render: connect Blueprint OR set service repo to Talent_Bridge_AI, branch main.
echo After deploy, this URL must work:
echo   https://talentbridge-ai.onrender.com/__deploy__/health/
echo.
pause