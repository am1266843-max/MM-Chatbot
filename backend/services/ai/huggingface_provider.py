import logging
from typing import List, Dict, Optional
import httpx
from backend.services.ai.base import BaseAIProvider

logger = logging.getLogger(__name__)

class HuggingFaceProvider(BaseAIProvider):
    """
    Provider for Hugging Face Inference API / Serverless Router.
    """

    def __init__(self, model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct", api_key: Optional[str] = None):
        super().__init__(model_name)
        self.api_key = api_key
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"

    def is_available(self) -> bool:
        return bool(self.api_key)

    def supports_vision(self) -> bool:
        model_lower = self.model_name.lower()
        return "vl" in model_lower or "vision" in model_lower

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        image_mime_type: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> str:
        if not self.is_available():
            raise ValueError(
                "Hugging Face API Key is missing. Please set `HUGGINGFACE_API_KEY` in your .env or settings."
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Build prompt from conversation
        prompt_parts = []
        if system_prompt:
            prompt_parts.append(f"<|system|>\n{system_prompt}\n")

        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            prompt_parts.append(f"<|{role}|>\n{content}\n")

        prompt_parts.append("<|assistant|>\n")
        full_prompt = "\n".join(prompt_parts)

        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "return_full_text": False
            }
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(self.api_url, headers=headers, json=payload)

                if response.status_code == 503:
                    # Model is loading
                    error_data = response.json()
                    estimated_time = error_data.get("estimated_time", "a few")
                    raise RuntimeError(
                        f"Hugging Face model is currently loading (estimated wait: {estimated_time}s). "
                        f"Please retry in a moment."
                    )

                if response.status_code != 200:
                    raise RuntimeError(f"Hugging Face API returned error {response.status_code}: {response.text}")

                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    generated_text = data[0].get("generated_text", "")
                    return generated_text.strip()
                elif isinstance(data, dict) and "generated_text" in data:
                    return data["generated_text"].strip()
                else:
                    return str(data)

        except Exception as e:
            logger.error(f"Hugging Face API request failed: {e}")
            raise

