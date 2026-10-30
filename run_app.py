"""
Nexus Multimodal & Multilingual AI Voice Assistant
Unified Application Launcher (Desktop Runner)
"""
import os
import sys
import time
import signal
import webbrowser
import subprocess
from pathlib import Path

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent

def get_python_exe():
    """Locate python executable in virtual environment or current interpreter."""
    venv_py_win = BASE_DIR / ".venv" / "Scripts" / "python.exe"
    if venv_py_win.exists():
        return str(venv_py_win)
    return sys.executable

def main():
    print("=" * 65)
    print("       🎙️ Starting Nexus Multilingual AI Voice Assistant")
    print("       (Supports Hindi, English, Spanish, French, RAG & Vision)")
    print("=" * 65)

    py_exe = get_python_exe()
    print(f"[*] Using Python: {py_exe}")

    # 1. Ensure .env file exists
    env_file = BASE_DIR / ".env"
    env_example = BASE_DIR / ".env.example"
    if not env_file.exists() and env_example.exists():
        print("[*] Creating .env from .env.example...")
        import shutil
        shutil.copy(env_example, env_file)

    # 2. Check/Initialize Database
    print("[*] Verifying database schema...")
    try:
        subprocess.run([py_exe, str(BASE_DIR / "scripts" / "init_db.py")], check=True)
    except Exception as e:
        print(f"[WARNING] Database check notice: {e}")

    # 3. Launch FastAPI Backend
    print("[*] Starting FastAPI Backend on http://localhost:8000...")
    backend_cmd = [
        py_exe, "-m", "uvicorn", "backend.main:app",
        "--host", "127.0.0.1",
        "--port", "8000"
    ]
    backend_proc = subprocess.Popen(
        backend_cmd,
        cwd=str(BASE_DIR)
    )

    # 4. Wait for backend to be ready
    print("[*] Waiting for backend service...")
    time.sleep(2.5)

    # 5. Launch Streamlit Frontend
    print("[*] Starting Streamlit Frontend on http://localhost:8501...")
    frontend_cmd = [
        py_exe, "-m", "streamlit", "run", "frontend/app.py",
        "--server.port", "8501",
        "--server.headless", "true"
    ]
    frontend_proc = subprocess.Popen(
        frontend_cmd,
        cwd=str(BASE_DIR)
    )

    # 6. Open Browser
    time.sleep(2.0)
    print("\n" + "=" * 65)
    print(" [SUCCESS] Application is running!")
    print(" 🌐 Web UI:       http://localhost:8501")
    print(" 🔌 API Docs:     http://localhost:8000/docs")
    print(" Press Ctrl+C in this terminal to stop both servers.")
    print("=" * 65 + "\n")

    try:
        webbrowser.open("http://localhost:8501")
    except Exception:
        pass

    # Wait for process exit or interrupt
    def shutdown(sig, frame):
        print("\n[*] Shutting down Nexus Assistant...")
        try:
            frontend_proc.terminate()
            backend_proc.terminate()
            frontend_proc.wait(timeout=3)
            backend_proc.wait(timeout=3)
        except Exception:
            pass
        print("[OK] Stopped successfully. Goodbye!")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        while True:
            time.sleep(1)
            # If any process died unexpectedly
            if backend_proc.poll() is not None:
                print(f"[ERROR] Backend exited with code {backend_proc.returncode}")
                shutdown(None, None)
            if frontend_proc.poll() is not None:
                print(f"[*] Frontend closed (exit code {frontend_proc.returncode}).")
                shutdown(None, None)
    except KeyboardInterrupt:
        shutdown(None, None)

if __name__ == "__main__":
    main()

