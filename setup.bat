@echo off
setlocal enabledelayedexpansion

echo =======================================================
echo     Nexus Multimodal AI Chatbot - Setup Script
echo =======================================================
echo.

:: 1. Check Python installation
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

python -c "import sys; print(f'Detected Python {sys.version.split()[0]}')"

:: 2. Check or create virtual environment
if not exist ".venv" (
    echo.
    echo [*] Creating virtual environment (.venv)...
    python -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
) else (
    echo [*] Virtual environment (.venv) already exists.
)

:: 3. Activate virtual environment
call .venv\Scripts\activate.bat

:: 4. Upgrade pip and install dependencies
echo.
echo [*] Installing required dependencies from requirements.txt...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Some dependencies had warnings during installation.
)

:: 5. Copy .env.example if .env does not exist
if not exist ".env" (
    echo.
    echo [*] Creating .env file from .env.example...
    copy .env.example .env >nul
    echo [OK] Created .env configuration file.
) else (
    echo [*] .env configuration file already exists.
)

:: 6. Initialize database tables
echo.
echo [*] Initializing database...
python scripts\init_db.py

echo.
echo =======================================================
echo [SUCCESS] Setup completed successfully!
echo To start the application, run: start.bat
echo =======================================================
echo.
pause

