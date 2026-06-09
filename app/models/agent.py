"""AI Agent API Key 模型"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime, timezone

from app.db.session import Base


class AgentApiKey(Base):
    __tablename__ = "agent_api_key"

    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String(100), nullable=False)
    api_key = Column(String(64), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_used_at = Column(DateTime, nullable=True)
