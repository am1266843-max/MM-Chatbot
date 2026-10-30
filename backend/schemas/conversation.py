from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class MessageBase(BaseModel):
    role: str
    content: str
    status: Optional[str] = "completed"
    extra_metadata: Optional[Dict[str, Any]] = None

class MessageCreate(MessageBase):
    pass

class MessageRead(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    status: str
    extra_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ConversationBase(BaseModel):
    title: Optional[str] = "New Conversation"
    model_provider: Optional[str] = None
    model_name: Optional[str] = None

class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    model_provider: Optional[str] = None
    model_name: Optional[str] = None

class ConversationRead(BaseModel):
    id: str
    title: str
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[MessageRead] = []

    model_config = ConfigDict(from_attributes=True)

class ConversationListItem(BaseModel):
    id: str
    title: str
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = ConfigDict(from_attributes=True)

