import io
import os
import base64
import logging
import asyncio
from typing import Optional
from backend.core.config import settings
from backend.core.languages import (
    get_voice_for_language,
    get_gtts_code,
    get_stt_code,
    detect_text_language
)

logger = logging.getLogger(__name__)

class AudioService:
    """Provides multilingual Speech-to-Text (STT) and Text-to-Speech (TTS) capabilities."""

    def __init__(self):
        self.tts_engine = settings.TTS_ENGINE
        self.tts_voice = settings.TTS_VOICE

    async def synthesize_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        language: Optional[str] = "auto",
        gender: str = "female"
    ) -> bytes:
        """
        Convert text to MP3 audio bytes using Edge-TTS or gTTS.
        Automatically resolves the optimal multilingual neural voice (e.g. Hindi, English, Spanish).
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty for speech synthesis.")

        # Clean markdown formatting for smoother spoken voice
        import re
        clean_text = re.sub(r"[*#_`>\[\]]", " ", text)
        clean_text = re.sub(r"https?://\S+", "", clean_text)
        clean_text = clean_text[:2000].strip() # Limit speech chunk for fast delivery

        # Determine voice name
        if voice and voice.strip():
            voice_name = voice
        else:
            voice_name = get_voice_for_language(language or "auto", text=clean_text, gender=gender)

        # 1. Try Edge-TTS (High quality Microsoft Neural Voice, free, no API key)
        try:
            import edge_tts
            communicate = edge_tts.Communicate(clean_text, voice_name)
            audio_buffer = bytearray()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_buffer.extend(chunk["data"])
            if audio_buffer:
                return bytes(audio_buffer)
        except Exception as e:
            logger.warning(f"Edge-TTS synthesis error for voice {voice_name}: {e}. Attempting gTTS fallback.")

        # 2. Try gTTS fallback (Google Translate TTS, free, no API key)
        try:
            from gtts import gTTS
            lang_code = get_gtts_code(language or "auto", text=clean_text)
            tts = gTTS(text=clean_text, lang=lang_code)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp.read()
        except Exception as e2:
            logger.error(f"gTTS synthesis failed: {e2}")
            raise RuntimeError(f"Speech synthesis failed: {e2}")

    async def transcribe_audio(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language: Optional[str] = "auto"
    ) -> str:
        """
        Transcribe speech audio bytes to text using available STT engine.
        Supports Hindi, English, and other global languages.
        """
        if not audio_bytes:
            raise ValueError("No audio data provided for transcription.")

        stt_lang = get_stt_code(language or "auto")

        # 1. Groq Whisper (if GROQ_API_KEY is configured - ultra fast)
        if settings.GROQ_API_KEY:
            try:
                from openai import AsyncOpenAI
                client = AsyncOpenAI(
                    api_key=settings.GROQ_API_KEY,
                    base_url="https://api.groq.com/openai/v1"
                )
                file_tuple = (filename, audio_bytes)
                whisper_kwargs = {
                    "model": "whisper-large-v3",
                    "file": file_tuple
                }
                if language and language != "auto" and language != "hi-en":
                    whisper_kwargs["language"] = language[:2] # e.g. 'hi', 'en', 'es'

                transcription = await client.audio.transcriptions.create(**whisper_kwargs)
                if transcription.text:
                    return transcription.text.strip()
            except Exception as e:
                logger.warning(f"Groq Whisper transcription failed: {e}. Trying local STT.")

        # 2. OpenAI Whisper (if OPENAI_API_KEY is configured)
        if settings.OPENAI_API_KEY:
            try:
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                file_tuple = (filename, audio_bytes)
                whisper_kwargs = {
                    "model": "whisper-1",
                    "file": file_tuple
                }
                if language and language != "auto" and language != "hi-en":
                    whisper_kwargs["language"] = language[:2]

                transcription = await client.audio.transcriptions.create(**whisper_kwargs)
                if transcription.text:
                    return transcription.text.strip()
            except Exception as e:
                logger.warning(f"OpenAI Whisper transcription failed: {e}. Trying local STT.")

        # 3. SpeechRecognition fallback (using free Google Web Speech API)
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()

            # Write temp wav
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=os.path.splitext(filename)[1] or ".wav", delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name

            try:
                with sr.AudioFile(tmp_path) as source:
                    audio_data = recognizer.record(source)
                    # Pass targeted language code (e.g. 'hi-IN' for Hindi, 'en-US' for English)
                    try:
                        text = recognizer.recognize_google(audio_data, language=stt_lang)
                        return text.strip()
                    except sr.UnknownValueError:
                        # If language specific recognition failed and was not en-US, try en-US as fallback
                        if stt_lang != "en-US":
                            text = recognizer.recognize_google(audio_data, language="en-US")
                            return text.strip()
                        raise
            finally:
                if os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass
        except Exception as e:
            logger.error(f"SpeechRecognition transcription failed: {e}")
            raise RuntimeError(
                f"Audio transcription failed ({e}). "
                f"For best results, speak clearly or configure `GROQ_API_KEY` for Whisper transcription."
            )

audio_service = AudioService()
