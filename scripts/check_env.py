import os
import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.config import settings

def check_environment():
    print("=" * 60)
    print("Checking Environment Configuration...")
    print("=" * 60)
    print(f"Python Version: {sys.version}")
    print(f"App Environment: {settings.APP_ENV}")
    print(f"Backend URL: {settings.BACKEND_URL}")
    print(f"Frontend URL: {settings.FRONTEND_URL}")
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"Upload Directory: {settings.UPLOAD_DIR}")
    print(f"Vector Store Directory: {settings.VECTOR_STORE_DIR}")
    print("-" * 60)
    print("AI Provider Keys:")
    print(f" - Groq API Key: {'[Configured]' if settings.GROQ_API_KEY else '[Missing]'}")
    print(f" - OpenAI API Key: {'[Configured]' if settings.OPENAI_API_KEY else '[Missing]'}")
    print(f" - Hugging Face API Key: {'[Configured]' if settings.HUGGINGFACE_API_KEY else '[Missing]'}")
    print(f" - Gemini API Key: {'[Configured]' if settings.GEMINI_API_KEY else '[Missing]'}")
    print("-" * 60)
    print("Search & Audio Services:")
    print(f" - Search Provider: {settings.SEARCH_PROVIDER}")
    print(f" - TTS Engine: {settings.TTS_ENGINE}")
    print("=" * 60)
    print("[OK] System configuration check complete!")

if __name__ == "__main__":
    check_environment()
