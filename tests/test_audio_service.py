import pytest
from backend.services.audio.audio_service import AudioService
from backend.core.languages import (
    detect_text_language,
    get_voice_for_language,
    get_stt_code
)

def test_language_detection():
    # Hindi text
    assert detect_text_language("नमस्ते, आप कैसे हैं?") == "hi"
    # English text
    assert detect_text_language("Hello, how are you doing?") == "en"
    # Hinglish text
    assert detect_text_language("Aap kaise ho bhai? Sab theek?") == "hi-en"
    # Bengali text
    assert detect_text_language("কেমন আছেন আপনি?") == "bn"

def test_voice_mapping_hindi_and_english():
    hindi_voice = get_voice_for_language("hi", gender="female")
    assert "Swara" in hindi_voice or "hi-IN" in hindi_voice

    hindi_male_voice = get_voice_for_language("hi", gender="male")
    assert "Madhur" in hindi_male_voice or "hi-IN" in hindi_male_voice

    us_voice = get_voice_for_language("en", gender="female")
    assert "Aria" in us_voice or "en-US" in us_voice

    in_voice = get_voice_for_language("en-in", gender="female")
    assert "Neerja" in in_voice or "en-IN" in in_voice

def test_stt_code_resolution():
    assert get_stt_code("hi") == "hi-IN"
    assert get_stt_code("en") == "en-US"
    assert get_stt_code("es") == "es-ES"

@pytest.mark.asyncio
async def test_audio_empty_synthesis():
    service = AudioService()
    with pytest.raises(ValueError):
        await service.synthesize_speech("")

@pytest.mark.asyncio
async def test_audio_empty_transcription():
    service = AudioService()
    with pytest.raises(ValueError):
        await service.transcribe_audio(b"")

def test_audio_languages_endpoint(client):
    res = client.get("/api/audio/languages")
    assert res.status_code == 200
    data = res.json()
    assert "languages" in data
    codes = [l["code"] for l in data["languages"]]
    assert "hi" in codes
    assert "en" in codes
    assert "es" in codes
    assert "fr" in codes
