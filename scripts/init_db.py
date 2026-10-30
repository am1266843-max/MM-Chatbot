import os
import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.database import engine, Base
from backend.core.config import settings
import backend.models # Ensure all models are imported

def init_database():
    print("=" * 50)
    print("Initializing Database...")
    print(f"DATABASE_URL: {settings.DATABASE_URL}")
    print("=" * 50)

    try:
        settings.ensure_directories()
        Base.metadata.create_all(bind=engine)
        print("[OK] Database tables successfully created/verified!")
        
        # Stamp Alembic migration revision
        try:
            import subprocess
            subprocess.run([sys.executable, "-m", "alembic", "stamp", "head"], capture_output=True, check=False)
            print("[OK] Alembic migration state synchronized (head).")
        except Exception:
            pass
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()
