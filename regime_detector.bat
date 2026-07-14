@echo off
REM MrUnderdog Cockpit - CLI regime read for XAU / BTC / US500 (deploy timing + funded easy-mode).
cd /d "%~dp0"
python regime_detector.py
echo.
pause
