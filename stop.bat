@echo off
echo =======================================================
echo      Stopping Nexus Multimodal AI Chatbot...
echo =======================================================

echo [*] Stopping backend process on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
    echo Terminated backend process (PID %%a).
)

echo [*] Stopping frontend process on port 8501...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8501 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
    echo Terminated frontend process (PID %%a).
)

echo.
echo [OK] All chatbot processes stopped.
pause

