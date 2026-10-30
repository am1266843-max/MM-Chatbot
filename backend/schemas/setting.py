from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class ProviderStatus(BaseModel):
    name: str
    configured: bool
    status_label: str
    details: Optional[str] = None

class SystemStatusResponse(BaseModel):
    backend_status: str
    database_status: str
    database_type: str
    active_ai_provider: str
    providers: List[ProviderStatus]
    search_configured: bool
    voice_configured: bool
    rag_configured: bool
    upload_limit_mb: int

class SettingItem(BaseModel):
    key: str
    value: str

