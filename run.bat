@echo off
setlocal
cd /d "%~dp0"

echo =======================================================
echo    Starting Nexus Multilingual AI Voice Assistant...
echo =======================================================
echo.

if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" "%~dp0run_app.py"
) else (
    call "%~dp0start.bat"
)

pause
