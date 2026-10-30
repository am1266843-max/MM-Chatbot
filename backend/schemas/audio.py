from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class AudioTranscribeResponse(BaseModel):
    success: bool
    text: str
    engine: str
    language: Optional[str] = None
    error: Optional[str] = None

class AudioSynthesizeRequest(BaseModel):
    text: str
    voice: Optional[str] = None
    language: Optional[str] = "auto"
    gender: Optional[str] = "female"
    engine: Optional[str] = "edge-tts"

class AudioSynthesizeResponse(BaseModel):
    success: bool
    audio_base64: Optional[str] = None
    mime_type: str = "audio/mp3"
    engine: str
    voice_used: Optional[str] = None
    error: Optional[str] = None

class LanguageInfo(BaseModel):
    code: str
    name: str
    edge_voice: str
    description: str

class LanguageListResponse(BaseModel):
    languages: List[LanguageInfo]
