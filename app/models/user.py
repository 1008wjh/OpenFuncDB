from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime, timezone

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    auth_level = Column(String(50), default="user")  # user, admin, super_admin
    is_active = Column(Boolean, default=True)
    create_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
