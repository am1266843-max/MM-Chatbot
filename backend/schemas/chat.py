from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class Attachment(BaseModel):
    filename: str
    file_type: str # 'image', 'document', 'audio'
    content_base64: Optional[str] = None
    file_path: Optional[str] = None

class Citation(BaseModel):
    document_name: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    snippet: str
    score: Optional[float] = None

class WebSearchSource(BaseModel):
    title: str
    url: str
    snippet: str
    published_date: Optional[str] = None

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str = Field(..., min_length=1)
    provider: Optional[str] = None
    model: Optional[str] = None
    language: Optional[str] = "auto"
    voice_gender: Optional[str] = "female"
    auto_speak: bool = False
    use_rag: bool = True
    use_web_search: bool = False
    system_prompt: Optional[str] = None
    image_base64: Optional[str] = None # For multimodal vision queries
    image_mime_type: Optional[str] = "image/jpeg"
    structured_format: Optional[str] = None # 'summary', 'checklist', 'json', 'table'

class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    reply: str
    model_provider: str
    model_name: str
    language: Optional[str] = "en"
    audio_base64: Optional[str] = None
    voice_used: Optional[str] = None
    citations: List[Citation] = []
    web_sources: List[WebSearchSource] = []
    structured_data: Optional[Any] = None
    tokens_used: Optional[int] = None
    error: Optional[str] = None
