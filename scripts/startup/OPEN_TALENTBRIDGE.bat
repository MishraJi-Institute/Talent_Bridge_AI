@echo off
setlocal
REM Always open TalentBridge on the bookmark-friendly port.
REM windows_manager keeps a redirect bridge so :8000 and :8001 both work.
start "" "http://127.0.0.1:8000/"
start "" "http://127.0.0.1:8000/login/"
exit /b 0
