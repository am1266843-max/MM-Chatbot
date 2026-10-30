import uuid
from sqlalchemy import Column, String, Text
from backend.core.database import Base

class Setting(Base):
    __tablename__ = "settings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    setting_key = Column(String(128), unique=True, nullable=False, index=True)
    setting_value = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Setting(key='{self.setting_key}')>"

