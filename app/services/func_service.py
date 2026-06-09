from typing import Optional, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.crud.func import func_base_crud, func_category_crud, func_audit_crud
from app.schemas.func import FuncBaseCreate, FuncBaseUpdate, FuncAuditCreate
from app.schemas.common import PaginationResult
from app.schemas.common import PaginationResult


class FuncService:
    @staticmethod
    def get_func_list(
        db: Session,
        func_type: Optional[str] = None,
        is_safe: Optional[bool] = None,
        page: int = 1,
        size: int = 10
    ) -> PaginationResult:
        skip = (page - 1) * size
        func_list = func_base_crud.get_multi_filtered(
            db, func_type=func_type, is_safe=is_safe, skip=skip, limit=size
        )
        total = func_base_crud.count_filtered(
            db, func_type=func_type, is_safe=is_safe
        )
        pages = (total + size - 1) // size if size > 0 else 0
        return PaginationResult(
            list=func_list,
            total=total,
            page=page,
            size=size,
            pages=pages
        )

    @staticmethod
    def get_func_detail(db: Session, func_id: int) -> Optional[Any]:
        func = func_base_crud.get(db, func_id)
        if func:
            func.categories
        return func

    @staticmethod
    def submit_func(db: Session, func_in: FuncBaseCreate, username: str) -> Any:
        func_data = func_in.model_dump()
        func_data["is_safe"] = False
        func = func_base_crud.create(db, obj_in=func_data)

        audit_data = {
            "func_id": func.id,
            "audit_status": 0,
            "audit_user": username,
            "audit_time": datetime.now(timezone.utc),
            "audit_remark": "待审核"
        }
        try:
            func_audit_crud.create(db, obj_in=audit_data)
        except Exception:
            db.rollback()
            raise

        return func

    @staticmethod
    def search_funcs(
        db: Session,
        keyword: str,
        func_type: Optional[str] = None,
        page: int = 1,
        size: int = 10,
    ) -> PaginationResult:
        total = func_base_crud.count_search(db, keyword=keyword, func_type=func_type)
        skip = (page - 1) * size
        func_list = func_base_crud.search(
            db, keyword=keyword, func_type=func_type, skip=skip, limit=size
        )
        pages = (total + size - 1) // size if size > 0 else 0
        return PaginationResult(
            list=func_list, total=total, page=page, size=size, pages=pages
        )

    @staticmethod
    def audit_func(db: Session, func_id: int, audit_in: FuncAuditCreate, username: str) -> Optional[Any]:
        func = func_base_crud.get(db, func_id)
        if not func:
            return None

        audit_update = audit_in.model_dump()
        audit_update["audit_user"] = username
        audit_update["audit_time"] = datetime.now(timezone.utc)

        audit = func_audit_crud.get_by_func_id(db, func_id)
        if audit:
            func_audit_crud.update(db, db_obj=audit, obj_in=audit_update)
        else:
            audit_data = {"func_id": func_id, **audit_update}
            func_audit_crud.create(db, obj_in=audit_data)

        if audit_in.audit_status == 1:
            func_base_crud.update(db, db_obj=func, obj_in={"is_safe": True})

        return func

    @staticmethod
    def get_category_list(db: Session, func_type: Optional[str] = None):
        return func_category_crud.get_by_func_type(db, func_type=func_type)

    @staticmethod
    def update_func(db: Session, func_id: int, update_in: FuncBaseUpdate) -> Optional[Any]:
        func = func_base_crud.get(db, func_id)
        if not func:
            return None
        update_data = update_in.model_dump(exclude_unset=True)
        return func_base_crud.update(db, db_obj=func, obj_in=update_data)

    @staticmethod
    def create_category(db: Session, category_in: Any):
        return func_category_crud.create(db, obj_in=category_in.model_dump())


func_service = FuncService()
