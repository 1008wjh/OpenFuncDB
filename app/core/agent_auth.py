"""AI Agent API Key 认证"""
from fastapi import Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.agent import AgentApiKey


async def verify_agent_api_key(x_api_key: str = Header(None, alias="X-API-Key")) -> str:
    """验证 Agent API Key，返回 key_name"""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )
    db: Session = SessionLocal()
    try:
        key_record = db.query(AgentApiKey).filter(
            AgentApiKey.api_key == x_api_key,
            AgentApiKey.is_active == True,
        ).first()
        if not key_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or inactive API key",
            )
        return key_record.key_name
    finally:
        db.close()
