import logging
from typing import List, Dict, Optional
import httpx
from backend.services.ai.base import BaseAIProvider

logger = logging.getLogger(__name__)

class GeminiProvider(BaseAIProvider):
    """
    Provider for Google Gemini API via official REST endpoints.
    """

    def __init__(self, model_name: str = "gemini-1.5-flash", api_key: Optional[str] = None):
        super().__init__(model_name)
        self.api_key = api_key

    def is_available(self) -> bool:
        return bool(self.api_key)

    def supports_vision(self) -> bool:
        # All Gemini 1.5 models natively support vision
        return "gemini" in self.model_name.lower()

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        image_mime_type: Optional[str] = "image/jpeg",
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> str:
        if not self.is_available():
            raise ValueError(
                "Gemini API Key is missing. Please set `GEMINI_API_KEY` in your .env or settings."
            )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"

        contents = []
        for idx, msg in enumerate(messages):
            is_last = (idx == len(messages) - 1)
            role = "user" if msg["role"] == "user" else "model"
            parts = [{"text": msg["content"]}]

            if is_last and image_bytes and role == "user":
                import base64
                b64_img = base64.b64encode(image_bytes).decode("utf-8")
                parts.append({
                    "inline_data": {
                        "mime_type": image_mime_type or "image/jpeg",
                        "data": b64_img
                    }
                })

            contents.append({"role": role, "parts": parts})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }

        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                raise RuntimeError(f"Gemini API returned error {response.status_code}: {response.text}")

            data = response.json()
            candidates = data.get("candidates", [])
            if candidates and "content" in candidates[0]:
                parts = candidates[0]["content"].get("parts", [])
                return "".join([p.get("text", "") for p in parts]).strip()
            return ""

