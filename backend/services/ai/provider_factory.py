import logging
from typing import Optional, List
from backend.core.config import settings
from backend.services.ai.base import BaseAIProvider
from backend.services.ai.mock_provider import MockProvider
from backend.services.ai.openai_provider import OpenAICompatibleProvider
from backend.services.ai.huggingface_provider import HuggingFaceProvider
from backend.services.ai.gemini_provider import GeminiProvider
from backend.schemas.model import ModelInfo

logger = logging.getLogger(__name__)

AVAILABLE_MODELS: List[ModelInfo] = [
    # Mock / Local
    ModelInfo(
        id="mock-model",
        name="Mock Assistant (Local / Offline)",
        provider="mock",
        supports_vision=True,
        supports_streaming=False,
        is_configured=True,
        description="Built-in simulated assistant for offline development and testing with zero API keys."
    ),
    # Groq (Free / Fast)
    ModelInfo(
        id="llama-3.1-8b-instant",
        name="LLaMA 3.1 8B Instant (Groq - Ultra Fast)",
        provider="groq",
        supports_vision=False,
        supports_streaming=True,
        is_configured=False,
        description="High-speed reasoning and conversation on Groq's LPU inference engine."
    ),
    ModelInfo(
        id="llama-3.2-11b-vision-preview",
        name="LLaMA 3.2 11B Vision (Groq - Multimodal)",
        provider="groq",
        supports_vision=True,
        supports_streaming=True,
        is_configured=False,
        description="Multimodal model capable of visual understanding and text analysis."
    ),
    ModelInfo(
        id="llama-3.3-70b-versatile",
        name="LLaMA 3.3 70B Versatile (Groq)",
        provider="groq",
        supports_vision=False,
        supports_streaming=True,
        is_configured=False,
        description="Flagship open-weights model for advanced logic, coding, and synthesis."
    ),
    # OpenAI
    ModelInfo(
        id="gpt-4o-mini",
        name="GPT-4o Mini (OpenAI - Vision & Speed)",
        provider="openai",
        supports_vision=True,
        supports_streaming=True,
        is_configured=False,
        description="Affordable, smart multimodal model for high performance text and image tasks."
    ),
    ModelInfo(
        id="gpt-4o",
        name="GPT-4o (OpenAI - Flagship Multimodal)",
        provider="openai",
        supports_vision=True,
        supports_streaming=True,
        is_configured=False,
        description="Industry-standard multimodal intelligence for text, images, and complex reasoning."
    ),
    # Hugging Face
    ModelInfo(
        id="meta-llama/Meta-Llama-3-8B-Instruct",
        name="Llama 3 8B Instruct (Hugging Face Serverless)",
        provider="huggingface",
        supports_vision=False,
        supports_streaming=False,
        is_configured=False,
        description="Hosted serverless inference on Hugging Face Hub."
    ),
    # Google Gemini
    ModelInfo(
        id="gemini-1.5-flash",
        name="Gemini 1.5 Flash (Google)",
        provider="gemini",
        supports_vision=True,
        supports_streaming=True,
        is_configured=False,
        description="Google's fast, multimodal workhorse model."
    ),
    # Ollama Local
    ModelInfo(
        id="llama3.2",
        name="Ollama LLaMA 3.2 (Local Host: 11434)",
        provider="ollama",
        supports_vision=False,
        supports_streaming=True,
        is_configured=True,
        description="Runs completely locally via Ollama without internet or API keys."
    )
]

def get_available_models() -> List[ModelInfo]:
    """Return model list annotated with live configuration status."""
    result = []
    for m in AVAILABLE_MODELS:
        configured = settings.is_provider_configured(m.provider)
        item = m.model_copy()
        item.is_configured = configured
        result.append(item)
    return result

def get_ai_provider(provider_name: Optional[str] = None, model_name: Optional[str] = None) -> BaseAIProvider:
    """
    Factory to retrieve an AI provider instance.
    Falls back gracefully if requested provider is unconfigured.
    """
    provider = (provider_name or settings.AI_PROVIDER).lower()
    model = model_name or settings.AI_MODEL

    if provider == "groq":
        api_key = settings.GROQ_API_KEY
        if not api_key:
            logger.warning("GROQ_API_KEY is not set. Falling back to MockProvider.")
            return MockProvider(model_name=model)
        return OpenAICompatibleProvider(
            model_name=model or "llama-3.1-8b-instant",
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
            provider_type="groq"
        )

    elif provider == "openai":
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            logger.warning("OPENAI_API_KEY is not set. Falling back to MockProvider.")
            return MockProvider(model_name=model)
        return OpenAICompatibleProvider(
            model_name=model or "gpt-4o-mini",
            api_key=api_key,
            base_url=settings.OPENAI_BASE_URL,
            provider_type="openai"
        )

    elif provider == "ollama":
        base_url = settings.OPENAI_BASE_URL or "http://localhost:11434/v1"
        return OpenAICompatibleProvider(
            model_name=model or "llama3.2",
            api_key="ollama",
            base_url=base_url,
            provider_type="ollama"
        )

    elif provider == "huggingface":
        api_key = settings.HUGGINGFACE_API_KEY
        if not api_key:
            logger.warning("HUGGINGFACE_API_KEY is not set. Falling back to MockProvider.")
            return MockProvider(model_name=model)
        return HuggingFaceProvider(
            model_name=model or "meta-llama/Meta-Llama-3-8B-Instruct",
            api_key=api_key
        )

    elif provider == "gemini":
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            logger.warning("GEMINI_API_KEY is not set. Falling back to MockProvider.")
            return MockProvider(model_name=model)
        return GeminiProvider(
            model_name=model or "gemini-1.5-flash",
            api_key=api_key
        )

    else:
        return MockProvider(model_name=model or "mock-model")

