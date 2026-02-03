@echo off
cd /d "%~dp0"
echo Starting Ideamanager Services...

:: Start WhatsApp Bridge in background
echo Starting WhatsApp Bridge...
start /b node src/whatsapp/bridge.js

:: Start Python Worker
echo Starting Python Worker...
python -m src.main

pause
