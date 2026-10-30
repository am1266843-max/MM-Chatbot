import re
from typing import Dict, Any, List, Optional

# Supported language catalog with metadata for Edge-TTS neural voices, gTTS, and STT
SUPPORTED_LANGUAGES: Dict[str, Dict[str, Any]] = {
    "auto": {
        "name": "Auto-Detect (स्वचालित)",
        "edge_voice": "hi-IN-SwaraNeural", # Fallback if text is Hindi, otherwise en-US
        "gtts_code": "en",
        "stt_code": "en-US",
        "description": "Automatically detects spoken and written language"
    },
    "hi": {
        "name": "Hindi (हिन्दी)",
        "edge_voice": "hi-IN-SwaraNeural",
        "edge_voice_male": "hi-IN-MadhurNeural",
        "gtts_code": "hi",
        "stt_code": "hi-IN",
        "description": "Standard Hindi with Devanagari script"
    },
    "en": {
        "name": "English (US)",
        "edge_voice": "en-US-AriaNeural",
        "edge_voice_male": "en-US-GuyNeural",
        "gtts_code": "en",
        "stt_code": "en-US",
        "description": "Global English"
    },
    "en-in": {
        "name": "English (India)",
        "edge_voice": "en-IN-NeerjaNeural",
        "edge_voice_male": "en-IN-PrabhatNeural",
        "gtts_code": "en",
        "stt_code": "en-IN",
        "description": "Indian English accent"
    },
    "hi-en": {
        "name": "Hinglish (मिक्स हिन्दी-English)",
        "edge_voice": "en-IN-NeerjaNeural",
        "edge_voice_male": "en-IN-PrabhatNeural",
        "gtts_code": "hi",
        "stt_code": "en-IN",
        "description": "Conversational Hindi written in English script"
    },
    "es": {
        "name": "Spanish (Español)",
        "edge_voice": "es-ES-ElviraNeural",
        "edge_voice_male": "es-ES-AlvaroNeural",
        "gtts_code": "es",
        "stt_code": "es-ES",
        "description": "Spanish language"
    },
    "fr": {
        "name": "French (Français)",
        "edge_voice": "fr-FR-DeniseNeural",
        "edge_voice_male": "fr-FR-HenriNeural",
        "gtts_code": "fr",
        "stt_code": "fr-FR",
        "description": "French language"
    },
    "de": {
        "name": "German (Deutsch)",
        "edge_voice": "de-DE-KatjaNeural",
        "edge_voice_male": "de-DE-ConradNeural",
        "gtts_code": "de",
        "stt_code": "de-DE",
        "description": "German language"
    },
    "ja": {
        "name": "Japanese (日本語)",
        "edge_voice": "ja-JP-NanamiNeural",
        "edge_voice_male": "ja-JP-KeitaNeural",
        "gtts_code": "ja",
        "stt_code": "ja-JP",
        "description": "Japanese language"
    },
    "zh": {
        "name": "Chinese (中文 - Mandarin)",
        "edge_voice": "zh-CN-XiaoxiaoNeural",
        "edge_voice_male": "zh-CN-YunjianNeural",
        "gtts_code": "zh-CN",
        "stt_code": "zh-CN",
        "description": "Mandarin Chinese"
    },
    "ar": {
        "name": "Arabic (العربية)",
        "edge_voice": "ar-SA-ZariyahNeural",
        "edge_voice_male": "ar-SA-HamedNeural",
        "gtts_code": "ar",
        "stt_code": "ar-SA",
        "description": "Modern Standard Arabic"
    },
    "bn": {
        "name": "Bengali (বাংলা)",
        "edge_voice": "bn-IN-TanishaaNeural",
        "edge_voice_male": "bn-IN-BashkarNeural",
        "gtts_code": "bn",
        "stt_code": "bn-IN",
        "description": "Bengali language"
    },
    "mr": {
        "name": "Marathi (मराठी)",
        "edge_voice": "mr-IN-AarohiNeural",
        "edge_voice_male": "mr-IN-ManoharNeural",
        "gtts_code": "mr",
        "stt_code": "mr-IN",
        "description": "Marathi language"
    },
    "ta": {
        "name": "Tamil (தமிழ்)",
        "edge_voice": "ta-IN-PallaviNeural",
        "edge_voice_male": "ta-IN-ValluvarNeural",
        "gtts_code": "ta",
        "stt_code": "ta-IN",
        "description": "Tamil language"
    },
    "te": {
        "name": "Telugu (తెలుగు)",
        "edge_voice": "te-IN-ShrutiNeural",
        "edge_voice_male": "te-IN-MohanNeural",
        "gtts_code": "te",
        "stt_code": "te-IN",
        "description": "Telugu language"
    },
    "ru": {
        "name": "Russian (Русский)",
        "edge_voice": "ru-RU-SvetlanaNeural",
        "edge_voice_male": "ru-RU-DmitryNeural",
        "gtts_code": "ru",
        "stt_code": "ru-RU",
        "description": "Russian language"
    },
    "pt": {
        "name": "Portuguese (Português)",
        "edge_voice": "pt-BR-FranciscaNeural",
        "edge_voice_male": "pt-BR-AntonioNeural",
        "gtts_code": "pt",
        "stt_code": "pt-BR",
        "description": "Portuguese language"
    }
}

def detect_text_language(text: str) -> str:
    """
    Detect the likely language of a given text string using Unicode character ranges.
    Returns language code such as 'hi', 'bn', 'mr', 'ta', 'te', 'ar', 'ja', 'zh', 'ru', or 'en'.
    """
    if not text or not text.strip():
        return "en"

    # Check for Devanagari script (Hindi / Marathi)
    devanagari_count = len(re.findall(r'[\u0900-\u097F]', text))
    if devanagari_count >= 3 or (len(text) < 15 and devanagari_count >= 1):
        return "hi"

    # Check for Bengali script
    if len(re.findall(r'[\u0980-\u09FF]', text)) >= 3:
        return "bn"

    # Check for Tamil script
    if len(re.findall(r'[\u0B80-\u0BFF]', text)) >= 3:
        return "ta"

    # Check for Telugu script
    if len(re.findall(r'[\u0C00-\u0C7F]', text)) >= 3:
        return "te"

    # Check for Arabic script
    if len(re.findall(r'[\u0600-\u06FF]', text)) >= 3:
        return "ar"

    # Check for Japanese (Hiragana, Katakana, Kanji)
    if len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF]', text)) >= 2:
        return "ja"

    # Check for Chinese (CJK Unified Ideographs without Japanese kana)
    if len(re.findall(r'[\u4E00-\u9FFF]', text)) >= 3:
        return "zh"

    # Check for Russian / Cyrillic script
    if len(re.findall(r'[\u0400-\u04FF]', text)) >= 3:
        return "ru"

    # Common Hinglish phrases indicator
    lower = text.lower()
    hinglish_keywords = ["aap ", "kaise ho", "kya ", "mera ", "meri ", "batao", "shukriya", "dhanyawad", "accha", "theek", "bolo"]
    if any(kw in lower for kw in hinglish_keywords):
        return "hi-en"

    return "en"

def get_voice_for_language(lang_code: str, text: Optional[str] = None, gender: str = "female") -> str:
    """Resolve the best neural TTS voice for a language code or sample text."""
    resolved_lang = lang_code.lower() if lang_code else "auto"

    if resolved_lang == "auto" and text:
        resolved_lang = detect_text_language(text)

    info = SUPPORTED_LANGUAGES.get(resolved_lang, SUPPORTED_LANGUAGES["en"])
    if gender.lower() == "male" and "edge_voice_male" in info:
        return info["edge_voice_male"]
    return info.get("edge_voice", "en-US-AriaNeural")

def get_gtts_code(lang_code: str, text: Optional[str] = None) -> str:
    """Resolve gTTS language code."""
    resolved_lang = lang_code.lower() if lang_code else "auto"
    if resolved_lang == "auto" and text:
        resolved_lang = detect_text_language(text)

    info = SUPPORTED_LANGUAGES.get(resolved_lang, SUPPORTED_LANGUAGES["en"])
    return info.get("gtts_code", "en")

def get_stt_code(lang_code: str) -> str:
    """Resolve SpeechRecognition language code (e.g. 'hi-IN', 'en-US')."""
    resolved_lang = lang_code.lower() if lang_code else "en"
    if resolved_lang == "auto":
        resolved_lang = "en"
    info = SUPPORTED_LANGUAGES.get(resolved_lang, SUPPORTED_LANGUAGES["en"])
    return info.get("stt_code", "en-US")

