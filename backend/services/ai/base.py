from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseAIProvider(ABC):
    """Abstract base class for all AI model providers."""

    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the provider is properly configured with credentials."""
        pass

    @abstractmethod
    def supports_vision(self) -> bool:
        """Return True if the current model supports vision/image inputs."""
        pass

    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        image_mime_type: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> str:
        """Generate a response given conversation messages and optional multimodal image inputs."""
        pass

