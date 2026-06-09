from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_active_user, require_admin
from app.services.func_service import func_service
from app.schemas.func import (
    FuncBaseSimple, FuncBaseDetail, FuncBaseCreate, FuncBaseUpdate,
    FuncAuditCreate, FuncCategory
)
from app.schemas.common import ResponseBase, PaginationResult

router = APIRouter()


@router.get("/list", response_model=ResponseBase[PaginationResult[FuncBaseSimple]])
async def get_func_list(
    func_type: Optional[str] = Query(None, description="Function type filter"),
    is_safe: Optional[bool] = Query(None, description="Safety filter"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    result = func_service.get_func_list(
        db, func_type=func_type, is_safe=is_safe, page=page, size=size
    )
    return ResponseBase(data=result)


@router.get("/detail/{func_id}", response_model=ResponseBase[FuncBaseDetail])
async def get_func_detail(
    func_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    func = func_service.get_func_detail(db, func_id)
    if not func:
        raise HTTPException(status_code=404, detail="Function not found")
    return ResponseBase(data=func)


@router.post("/submit", response_model=ResponseBase[FuncBaseSimple])
async def submit_func(
    func_in: FuncBaseCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    func = func_service.submit_func(db, func_in, current_user.username)
    return ResponseBase(data=func, msg="Function submitted successfully, pending review")


@router.get("/search", response_model=ResponseBase[PaginationResult[FuncBaseSimple]])
async def search_funcs(
    keyword: str = Query(..., min_length=1, description="Search keyword"),
    func_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    result = func_service.search_funcs(db, keyword=keyword, func_type=func_type, page=page, size=size)
    return ResponseBase(data=result)


@router.post("/audit/{func_id}", response_model=ResponseBase[FuncBaseSimple])
async def audit_func(
    func_id: int,
    audit_in: FuncAuditCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    require_admin(current_user.auth_level)
    func = func_service.audit_func(db, func_id, audit_in, current_user.username)
    if not func:
        raise HTTPException(status_code=404, detail="Function not found")
    return ResponseBase(data=func, msg="Audit completed")


@router.put("/update/{func_id}", response_model=ResponseBase[FuncBaseSimple])
async def update_func(
    func_id: int,
    update_in: FuncBaseUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    require_admin(current_user.auth_level)
    func = func_service.update_func(db, func_id, update_in)
    if not func:
        raise HTTPException(status_code=404, detail="Function not found")
    return ResponseBase(data=func, msg="Function updated")
