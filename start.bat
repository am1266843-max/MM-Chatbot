@echo off
cd /d "%~dp0"

echo =======================================================
echo    Starting Nexus Multilingual AI Voice Assistant...
echo =======================================================
echo.

if not exist .venv\Scripts\python.exe call setup.bat

echo [*] Starting FastAPI Backend on http://localhost:8000...
start "Nexus AI - Backend" .venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

echo [*] Starting Streamlit Frontend on http://localhost:8501...
start "Nexus AI - Frontend" .venv\Scripts\python.exe -m streamlit run frontend/app.py --server.port 8501 --server.headless false

echo [*] Waiting for services to initialize...
ping 127.0.0.1 -n 5 >nul

echo [*] Opening browser to http://localhost:8501...
start http://localhost:8501

echo.
echo =======================================================
echo [SUCCESS] Chatbot application is running!
echo Web UI:      http://localhost:8501
echo Backend API: http://localhost:8000/docs
echo Close the terminal windows or run stop.bat to stop.
echo =======================================================
echo.
