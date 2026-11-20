@echo off
setlocal
cd /d "%~dp0..\.."
echo [1/3] Static build...
python tools\build_static.py || exit /b 1
echo [2/3] All HTML in site/...
python tools\audit_all_html.py || exit /b 1
echo [3/3] Live + local HTTP checks (start Django on 8000 for local)...
python tools\audit_three_hosts.py
exit /b %ERRORLEVEL%