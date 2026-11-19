@echo off
schtasks /Delete /TN "TalentBridgeAI Django Server" /F
echo Automatic startup task removed. This does not delete project data.
pause
