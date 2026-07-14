@echo off
title MrUnderdog Cockpit
echo ================================================
echo    Starting MrUnderdog Cockpit
echo    (opens in your browser at localhost:8501)
echo ================================================
echo.
cd /d "%~dp0"
streamlit run dashboard.py
pause
