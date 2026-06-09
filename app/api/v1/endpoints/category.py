from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_active_user, require_admin
from app.services.func_service import func_service
from app.schemas.func import FuncCategory, FuncCategoryCreate
from app.schemas.common import ResponseBase

router = APIRouter()


@router.get("/list", response_model=ResponseBase[list[FuncCategory]])
async def get_category_list(
    func_type: Optional[str] = Query(None, description="Filter by function type"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    categories = func_service.get_category_list(db, func_type=func_type)
    return ResponseBase(data=categories)


@router.post("/create", response_model=ResponseBase[FuncCategory])
async def create_category(
    category_in: FuncCategoryCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    require_admin(current_user.auth_level)
    cat = func_service.create_category(db, category_in)
    return ResponseBase(data=cat, msg="Category created")
