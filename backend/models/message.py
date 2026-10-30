import uuid
import json
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.core.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(32), nullable=False) # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    status = Column(String(32), default="completed", nullable=False) # 'pending', 'completed', 'failed'
    extra_metadata = Column(Text, nullable=True) # JSON encoded string for citations, images, audio info
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    conversation = relationship("Conversation", back_populates="messages")

    @property
    def metadata_dict(self):
        if not self.extra_metadata:
            return {}
        try:
            return json.loads(self.extra_metadata)
        except Exception:
            return {}

    @metadata_dict.setter
    def metadata_dict(self, val):
        if val is None:
            self.extra_metadata = None
        else:
            self.extra_metadata = json.dumps(val)

    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}', status='{self.status}')>"

