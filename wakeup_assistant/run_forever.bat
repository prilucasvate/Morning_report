@echo off
title Morning Voice Assistant (Running...)
cd /d "%~dp0"

:loop
echo ========================================
echo Starting Assistant...
echo ========================================
python main_v3.py

echo.
echo [WARNING] Program closed or crashed!
echo Restarting in 5 seconds...
timeout /t 5
goto loop
