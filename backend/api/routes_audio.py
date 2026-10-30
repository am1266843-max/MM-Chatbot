import base64
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from backend.schemas.audio import (
    AudioTranscribeResponse,
    AudioSynthesizeRequest,
    AudioSynthesizeResponse,
    LanguageListResponse,
    LanguageInfo
)
from backend.services.audio.audio_service import audio_service
from backend.core.languages import SUPPORTED_LANGUAGES, get_voice_for_language

router = APIRouter(prefix="/api/audio", tags=["Audio"])

@router.get("/languages", response_model=LanguageListResponse)
def list_languages():
    """List all supported multilingual languages and corresponding neural voices."""
    items = []
    for code, info in SUPPORTED_LANGUAGES.items():
        items.append(LanguageInfo(
            code=code,
            name=info["name"],
            edge_voice=info["edge_voice"],
            description=info["description"]
        ))
    return LanguageListResponse(languages=items)

@router.post("/transcribe", response_model=AudioTranscribeResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = Form("auto")
):
    """
    Transcribe speech audio file (WAV, MP3, OGG, WebM) into text.
    Supports Hindi, English, Spanish, and many more.
    """
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty audio file uploaded")

        text = await audio_service.transcribe_audio(
            content,
            filename=file.filename or "speech.wav",
            language=language or "auto"
        )
        return AudioTranscribeResponse(
            success=True,
            text=text,
            language=language,
            engine="whisper" if hasattr(audio_service, "tts_engine") else "speech_recognition"
        )
    except Exception as e:
        return AudioTranscribeResponse(
            success=False,
            text="",
            language=language,
            engine="stt",
            error=str(e)
        )

@router.post("/synthesize", response_model=AudioSynthesizeResponse)
async def synthesize_speech(payload: AudioSynthesizeRequest):
    """
    Synthesize text to speech audio, returning base64 encoded MP3 audio data.
    Automatically chooses the best neural voice for Hindi, English, etc.
    """
    try:
        voice = payload.voice or get_voice_for_language(payload.language or "auto", text=payload.text, gender=payload.gender or "female")
        audio_bytes = await audio_service.synthesize_speech(
            payload.text,
            voice=voice,
            language=payload.language or "auto",
            gender=payload.gender or "female"
        )
        b64 = base64.b64encode(audio_bytes).decode("utf-8")
        return AudioSynthesizeResponse(
            success=True,
            audio_base64=b64,
            mime_type="audio/mp3",
            voice_used=voice,
            engine="edge-tts"
        )
    except Exception as e:
        return AudioSynthesizeResponse(
            success=False,
            audio_base64=None,
            mime_type="audio/mp3",
            engine="tts",
            error=str(e)
        )

@router.post("/synthesize/raw")
async def synthesize_speech_raw(payload: AudioSynthesizeRequest):
    """Directly stream or return MP3 audio bytes for browser audio playback."""
    try:
        voice = payload.voice or get_voice_for_language(payload.language or "auto", text=payload.text, gender=payload.gender or "female")
        audio_bytes = await audio_service.synthesize_speech(
            payload.text,
            voice=voice,
            language=payload.language or "auto",
            gender=payload.gender or "female"
        )
        return Response(content=audio_bytes, media_type="audio/mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
