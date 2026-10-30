from typing import List, Optional
from pydantic import BaseModel

class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    supports_vision: bool = False
    supports_streaming: bool = True
    is_configured: bool = False
    description: Optional[str] = None

class ModelListResponse(BaseModel):
    default_provider: str
    default_model: str
    models: List[ModelInfo]

