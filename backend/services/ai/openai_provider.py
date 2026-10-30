import base64
import logging
from typing import List, Dict, Optional
from openai import AsyncOpenAI
from backend.services.ai.base import BaseAIProvider

logger = logging.getLogger(__name__)

# List of known vision-supporting models
KNOWN_VISION_MODELS = {
    "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4-vision-preview",
    "llama-3.2-11b-vision-preview", "llama-3.2-90b-vision-preview",
    "llava", "llava:latest", "llava-phi3", "qwen2-vl"
}

class OpenAICompatibleProvider(BaseAIProvider):
    """
    Provider for OpenAI and OpenAI-compatible services (Groq, Together, Ollama, DeepSeek).
    """

    def __init__(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        provider_type: str = "openai"
    ):
        super().__init__(model_name)
        self.provider_type = provider_type
        self.api_key = api_key or "no-key-required"
        self.base_url = base_url

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def is_available(self) -> bool:
        if self.provider_type == "ollama":
            return True
        return bool(self.api_key and self.api_key != "no-key-required")

    def supports_vision(self) -> bool:
        model_lower = self.model_name.lower()
        return any(v in model_lower for v in KNOWN_VISION_MODELS) or "vision" in model_lower

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
                f"API Key is missing for provider '{self.provider_type}'. "
                f"Please set your API key in the .env file or configuration settings."
            )

        formatted_messages = []

        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})

        # Process conversation messages
        for idx, msg in enumerate(messages):
            is_last = (idx == len(messages) - 1)
            role = msg["role"]
            content = msg["content"]

            if is_last and image_bytes and role == "user":
                if not self.supports_vision():
                    raise ValueError(
                        f"The selected model '{self.model_name}' does not support vision/image inputs. "
                        f"Please select a vision-capable model (such as LLaMA 3.2 Vision on Groq or GPT-4o on OpenAI)."
                    )
                b64_img = base64.b64encode(image_bytes).decode("utf-8")
                mime = image_mime_type or "image/jpeg"
                content_payload = [
                    {"type": "text", "text": content},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime};base64,{b64_img}"
                        }
                    }
                ]
                formatted_messages.append({"role": role, "content": content_payload})
            else:
                formatted_messages.append({"role": role, "content": content})

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=45.0
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"OpenAI/Groq provider error: {e}")
            raise

