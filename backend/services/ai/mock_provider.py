import base64
from typing import List, Dict, Optional
from backend.services.ai.base import BaseAIProvider
from backend.core.languages import detect_text_language

class MockProvider(BaseAIProvider):
    """
    Multilingual Mock AI Provider for development, testing, and offline operation.
    Provides polite, informative, multilingual responses in Hindi, English, Hinglish, etc.
    without requiring external paid API keys.
    """

    def __init__(self, model_name: str = "mock-model"):
        super().__init__(model_name)

    def is_available(self) -> bool:
        return True

    def supports_vision(self) -> bool:
        return True

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        image_mime_type: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> str:
        last_message = messages[-1]["content"] if messages else ""
        detected_lang = detect_text_language(last_message)

        # Check if Hindi or Hinglish requested in system prompt or query
        is_hindi = (detected_lang == "hi") or (system_prompt and "Hindi (हिन्दी)" in system_prompt)
        is_hinglish = (detected_lang == "hi-en") or (system_prompt and "Hinglish" in system_prompt)
        is_spanish = (detected_lang == "es") or (system_prompt and "Spanish" in system_prompt)

        # Multimodal Vision Mock Response
        if image_bytes:
            size_kb = len(image_bytes) / 1024
            if is_hindi:
                return (
                    f"### 🖼️ छवि प्राप्त हुई (मॉक विज़न मोड - Mock Vision Mode)\n\n"
                    f"मुझे आपकी इमेज प्राप्त हो गई है (`{image_mime_type}`, साइज़: ~{size_kb:.1f} KB)।\n\n"
                    f"**आपका प्रश्न:** {last_message}\n\n"
                    f"> **नोट:** वर्तमान में चैटबॉट **मॉक AI प्रोवाइडर** का उपयोग कर रहा है। "
                    f"वास्तविक मल्टीमॉडल कंप्यूटर विज़न विश्लेषण के लिए, कृपया `.env` फ़ाइल में "
                    f"`GROQ_API_KEY` (LLaMA 3.2 Vision के लिए) या `OPENAI_API_KEY` (GPT-4o के लिए) कॉन्फ़िगर करें।"
                )
            return (
                f"### 🖼️ Image Received (Mock Vision Mode)\n\n"
                f"I received your image (`{image_mime_type}`, size: ~{size_kb:.1f} KB).\n\n"
                f"**Your Question:** {last_message}\n\n"
                f"> **Note:** The chatbot is currently using the **Mock AI Provider**. "
                f"To perform real multimodal computer vision analysis, please configure an API key "
                f"(such as `GROQ_API_KEY` for LLaMA 3.2 Vision, or `OPENAI_API_KEY` for GPT-4o) in your `.env` or settings."
            )

        query_lower = last_message.lower()

        # Hindi (हिन्दी) responses
        if is_hindi or any(w in last_message for w in ["नमस्ते", "हेलो", "कैसा", "मदद", "बताओ", "हिंदी"]):
            if any(w in query_lower for w in ["नमस्ते", "हेलो", "hello", "hi"]):
                return (
                    "**नमस्ते!** 🙏 मैं आपका **बहुभाषी AI वॉइस असिस्टेंट (Multimodal AI Voice Assistant)** हूँ।\n\n"
                    "मैं आपकी इन सभी चीज़ों में सहायता कर सकता हूँ:\n"
                    "- 🎙️ **वॉइस असिस्टेंस:** हिन्दी और अंग्रेज़ी में बोलकर सवाल पूछें और बोलकर जवाब सुनें।\n"
                    "- 🌐 **बहुभाषी सहायता:** हिन्दी (Hindi), English, Hinglish, बंगाली, मराठी आदि अनेक भाषाएँ।\n"
                    "- 📄 **डॉक्यूमेंट Q&A (RAG):** PDF, DOCX, CSV फाइल्स को पढ़कर उनका विश्लेषण।\n"
                    "- 🖼️ **इमेज विज़न:** तस्वीरों को देखकर उनके बारे में बताना।\n"
                    "- 🔍 **वेब सर्च:** ताज़ा जानकारी इंटरनेट से खोजना।\n\n"
                    "आज मैं आपकी क्या मदद कर सकता हूँ?"
                )
            elif "voice" in query_lower or "आवाज़" in last_message or "असिस्टेंट" in last_message:
                return (
                    "**🎙️ वॉइस असिस्टेंस सक्रिय है!**\n\n"
                    "आप नीचे दिए गए माइक्रोफ़ोन आइकन पर क्लिक करके हिन्दी में बोल सकते हैं। "
                    "साथ ही, मेरे किसी भी जवाब को सुनने के लिए **'🔊 Read Aloud'** बटन दबाएँ या साइडबार में **'Auto-Speak Responses'** चालू करें।"
                )
            return (
                f"आपके प्रश्न: **\"{last_message}\"** के लिए धन्यवाद!\n\n"
                f"यह जवाब **बहुभाषी मॉक AI मोड** द्वारा उत्पन्न किया गया है। "
                f"एप्लिकेशन का बैकएंड, वॉइस इंजन (Edge-TTS), डेटाबेस और RAG पूरी तरह से सुचारू रूप से काम कर रहे हैं!\n\n"
                f"💡 **सुझाव:** वास्तविक LLaMA 3.1 या GPT-4o मॉडल से लाइव जवाब पाने के लिए `.env` में `GROQ_API_KEY` या `OPENAI_API_KEY` जोड़ें।"
            )

        # Hinglish responses
        if is_hinglish:
            return (
                f"**Namaste!** 🙏 Mai aapka **Multimodal AI Voice Assistant** hu.\n\n"
                f"Aapka sawal tha: **\"{last_message}\"**\n\n"
                f"Mai Hindi, English, Hinglish aur anya bhashao me baat kar sakta hu. "
                f"Aap microphone use karke bol bhi sakte hain aur 'Read Aloud' se mera jawab sun bhi sakte hain!\n\n"
                f"💡 Live AI models ke liye `.env` file me `GROQ_API_KEY` ya `OPENAI_API_KEY` set karein."
            )

        # English responses
        if "hello" in query_lower or "hi" in query_lower:
            return (
                "**Hello!** 👋 I am your **Multimodal AI Voice Assistant**.\n\n"
                "I support text, voice input & output, image analysis, document processing (RAG), and live web search "
                "across **many languages** including **Hindi (हिन्दी), English, Spanish, French, German, Japanese, Bengali, and more**.\n\n"
                "How can I assist you today?"
            )
        elif "who are you" in query_lower or "voice" in query_lower:
            return (
                "**🎙️ Voice Assistant Active:** I am a complete Multimodal AI Assistant with interactive voice support. "
                "You can speak directly into your microphone, listen to spoken answers with neural voices, and switch languages anytime!"
            )

        return (
            f"Thank you for your message: **\"{last_message}\"**\n\n"
            f"This is a response generated by the **Multilingual Mock AI Provider**. "
            f"Voice assistance, document RAG, and translation are fully functional!\n\n"
            f"💡 **Tip:** To connect live cloud intelligence (such as LLaMA 3.1 or GPT-4o), "
            f"add your API key (`GROQ_API_KEY` or `OPENAI_API_KEY`) to the `.env` file."
        )
