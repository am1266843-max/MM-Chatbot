from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class DocumentChunkRead(BaseModel):
    id: str
    chunk_index: int
    extracted_text: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class DocumentRead(BaseModel):
    id: str
    conversation_id: Optional[str] = None
    original_filename: str
    mime_type: str
    file_size: int
    processing_status: str
    chunk_count: int
    error_message: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    file_size: int
    status: str
    chunk_count: int
    message: str

