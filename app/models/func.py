from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db.session import Base


class FuncBase(Base):
    __tablename__ = "func_base"

    id = Column(Integer, primary_key=True, index=True)
    func_type = Column(String(50), nullable=False, index=True)
    func_name = Column(String(200), nullable=False)
    func_content = Column(Text, nullable=False)
    func_desc = Column(Text)
    func_params = Column(Text)
    func_return = Column(Text)
    is_safe = Column(Boolean, default=False)
    create_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    update_time = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    categories = relationship("FuncCategory", secondary="func_category_relation", back_populates="funcs")
    audits = relationship("FuncAudit", back_populates="func")


class FuncCategory(Base):
    __tablename__ = "func_category"

    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(100), nullable=False)
    func_type = Column(String(50), index=True)
    category_desc = Column(Text)

    funcs = relationship("FuncBase", secondary="func_category_relation", back_populates="categories")


class FuncCategoryRelation(Base):
    __tablename__ = "func_category_relation"

    id = Column(Integer, primary_key=True, index=True)
    func_id = Column(Integer, ForeignKey("func_base.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("func_category.id"), nullable=False)


class FuncAudit(Base):
    __tablename__ = "func_audit"

    id = Column(Integer, primary_key=True, index=True)
    func_id = Column(Integer, ForeignKey("func_base.id"), nullable=False)
    audit_status = Column(Integer, default=0)  # 0: pending, 1: approved, 2: rejected
    audit_user = Column(String(100))
    audit_time = Column(DateTime)
    audit_remark = Column(Text)

    func = relationship("FuncBase", back_populates="audits")
