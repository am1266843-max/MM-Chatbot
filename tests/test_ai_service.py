import pytest
from backend.services.ai.mock_provider import MockProvider
from backend.services.ai.provider_factory import get_ai_provider
from backend.services.ai.openai_provider import OpenAICompatibleProvider

@pytest.mark.asyncio
async def test_mock_provider_text_response():
    provider = MockProvider()
    assert provider.is_available() is True
    assert provider.supports_vision() is True

    messages = [{"role": "user", "content": "Hello!"}]
    reply = await provider.generate_response(messages)
    assert len(reply) > 0
    assert "Nexus" in reply or "Multimodal" in reply or "Hello" in reply

@pytest.mark.asyncio
async def test_mock_provider_hindi_response():
    provider = MockProvider()
    messages = [{"role": "user", "content": "नमस्ते, आप कैसे हैं?"}]
    reply = await provider.generate_response(messages)
    assert len(reply) > 0
    # Must respond in Hindi
    assert "नमस्ते" in reply or "सहायक" in reply or "मदद" in reply

@pytest.mark.asyncio
async def test_mock_provider_vision_response():
    provider = MockProvider()
    messages = [{"role": "user", "content": "What is in this image?"}]
    dummy_bytes = b"fake-image-bytes-data"

    reply = await provider.generate_response(
        messages=messages,
        image_bytes=dummy_bytes,
        image_mime_type="image/png"
    )
    assert "Image Received" in reply
    assert "Mock Vision Mode" in reply

def test_provider_factory_fallback():
    # When requesting groq without API key set, it safely falls back to MockProvider
    provider = get_ai_provider("groq", "llama-3.1-8b-instant")
    assert isinstance(provider, (MockProvider, OpenAICompatibleProvider))

def test_vision_support_detection():
    vision_model = OpenAICompatibleProvider("gpt-4o")
    assert vision_model.supports_vision() is True

    text_only_model = OpenAICompatibleProvider("llama-3.1-8b-instant")
    assert text_only_model.supports_vision() is False
