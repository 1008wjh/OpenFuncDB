from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.crud.base import CRUDBase
from app.models.func import FuncBase, FuncCategory, FuncCategoryRelation, FuncAudit
from app.schemas.func import FuncBaseCreate, FuncBaseUpdate


class CRUDFuncBase(CRUDBase[FuncBase]):
    def get_multi_filtered(
        self,
        db: Session,
        *,
        func_type: Optional[str] = None,
        is_safe: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[FuncBase]:
        query = select(self.model)
        filters = []
        if func_type is not None:
            filters.append(self.model.func_type == func_type)
        if is_safe is not None:
            filters.append(self.model.is_safe == is_safe)
        if filters:
            query = query.where(and_(*filters))
        query = query.order_by(self.model.create_time.desc()).offset(skip).limit(limit)
        return db.execute(query).scalars().all()

    def count_filtered(
        self,
        db: Session,
        *,
        func_type: Optional[str] = None,
        is_safe: Optional[bool] = None
    ) -> int:
        from sqlalchemy import func as sa_func
        query = select(sa_func.count(self.model.id))
        filters = []
        if func_type is not None:
            filters.append(self.model.func_type == func_type)
        if is_safe is not None:
            filters.append(self.model.is_safe == is_safe)
        if filters:
            query = query.where(and_(*filters))
        result = db.execute(query).scalar()
        return result or 0

    def search(
        self,
        db: Session,
        *,
        keyword: str,
        func_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[FuncBase]:
        query = select(self.model).where(
            self.model.func_name.ilike(f"%{keyword}%")
        )
        if func_type:
            query = query.where(self.model.func_type == func_type)
        query = query.order_by(self.model.create_time.desc()).offset(skip).limit(limit)
        return db.execute(query).scalars().all()

    def count_search(
        self,
        db: Session,
        *,
        keyword: str,
        func_type: Optional[str] = None
    ) -> int:
        from sqlalchemy import func as sa_func
        query = select(sa_func.count(self.model.id)).where(
            self.model.func_name.ilike(f"%{keyword}%")
        )
        if func_type:
            query = query.where(self.model.func_type == func_type)
        result = db.execute(query).scalar()
        return result or 0


class CRUDFuncCategory(CRUDBase[FuncCategory]):
    def get_by_func_type(self, db: Session, func_type: Optional[str] = None) -> List[FuncCategory]:
        query = select(self.model)
        if func_type is not None:
            query = query.where(self.model.func_type == func_type)
        query = query.order_by(self.model.id)
        return db.execute(query).scalars().all()


class CRUDFuncAudit(CRUDBase[FuncAudit]):
    def get_by_func_id(self, db: Session, func_id: int) -> Optional[FuncAudit]:
        query = select(self.model).where(self.model.func_id == func_id)
        return db.execute(query).scalar_one_or_none()


func_base_crud = CRUDFuncBase(FuncBase)
func_category_crud = CRUDFuncCategory(FuncCategory)
func_audit_crud = CRUDFuncAudit(FuncAudit)
