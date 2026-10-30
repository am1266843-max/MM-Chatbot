import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Base directory for the backend/project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    APP_NAME: str = "Multimodal AI Chatbot"
    APP_DEBUG: bool = True

    # Server
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_PORT: int = 8501
    FRONTEND_URL: str = "http://localhost:8501"

    # Database: Defaults to SQLite for immediate local plug-and-play, supports PostgreSQL
    DATABASE_URL: str = "sqlite:///./chatbot.db"

    # Storage
    UPLOAD_DIR: str = str(BASE_DIR / "data" / "uploads")
    VECTOR_STORE_DIR: str = str(BASE_DIR / "data" / "vector_store")
    MAX_UPLOAD_MB: int = 15

    # Default AI Provider & Model
    AI_PROVIDER: str = "mock"
    AI_MODEL: str = "mock-model"

    # API Keys
    GROQ_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # Embeddings & RAG
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    RAG_TOP_K: int = 4
    RAG_SCORE_THRESHOLD: float = 0.35

    # Web Search
    SEARCH_PROVIDER: str = "duckduckgo"
    TAVILY_API_KEY: Optional[str] = None

    # Audio
    TTS_ENGINE: str = "edge-tts"
    TTS_VOICE: str = "en-US-AriaNeural"
    STT_ENGINE: str = "auto"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def ensure_directories(self) -> None:
        """Ensure upload and vector store directories exist."""
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(self.VECTOR_STORE_DIR, exist_ok=True)

    def is_provider_configured(self, provider: str) -> bool:
        provider = provider.lower()
        if provider == "mock":
            return True
        if provider == "groq":
            return bool(self.GROQ_API_KEY)
        if provider == "openai":
            return bool(self.OPENAI_API_KEY)
        if provider == "huggingface":
            return bool(self.HUGGINGFACE_API_KEY)
        if provider == "gemini":
            return bool(self.GEMINI_API_KEY)
        if provider == "ollama":
            return True # Local Ollama assumed running without key
        return False

settings = Settings()
settings.ensure_directories()

