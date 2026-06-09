from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class FuncCategoryBase(BaseModel):
    category_name: str
    func_type: Optional[str] = None
    category_desc: Optional[str] = None


class FuncCategoryCreate(FuncCategoryBase):
    pass


class FuncCategory(FuncCategoryBase):
    id: int

    class Config:
        from_attributes = True


class FuncBaseBase(BaseModel):
    func_type: str
    func_name: str
    func_content: str
    func_desc: Optional[str] = None
    func_params: Optional[str] = None
    func_return: Optional[str] = None


class FuncBaseCreate(FuncBaseBase):
    pass


class FuncBaseUpdate(BaseModel):
    func_type: Optional[str] = None
    func_name: Optional[str] = None
    func_content: Optional[str] = None
    func_desc: Optional[str] = None
    func_params: Optional[str] = None
    func_return: Optional[str] = None
    is_safe: Optional[bool] = None


class FuncBaseSimple(FuncBaseBase):
    id: int
    is_safe: bool
    create_time: datetime

    class Config:
        from_attributes = True


class FuncBaseDetail(FuncBaseSimple):
    update_time: datetime
    categories: List[FuncCategory] = []

    class Config:
        from_attributes = True


class FuncAuditCreate(BaseModel):
    audit_status: int  # 1: approved, 2: rejected
    audit_remark: Optional[str] = None


class FuncAudit(BaseModel):
    id: int
    func_id: int
    audit_status: int
    audit_user: Optional[str] = None
    audit_time: Optional[datetime] = None
    audit_remark: Optional[str] = None

    class Config:
        from_attributes = True
