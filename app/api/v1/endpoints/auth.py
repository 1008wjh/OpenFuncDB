from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.config import settings
from app.core.security import create_access_token, get_current_active_user
from app.crud.user import user_crud
from app.schemas.user import Token, User
from app.schemas.common import ResponseBase

router = APIRouter()


@router.post("/login", response_model=ResponseBase[Token])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = user_crud.authenticate(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "auth_level": user.auth_level},
        expires_delta=access_token_expires
    )
    token_data = Token(
        access_token=access_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return ResponseBase(data=token_data)


@router.get("/me", response_model=ResponseBase[User])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return ResponseBase(data=current_user)


@router.post("/init-admin")
async def init_admin(db: Session = Depends(get_db)):
    """Initialize admin account. Safe to call multiple times — only creates if not exists."""
    existing = user_crud.get_by_username(db, settings.ADMIN_USERNAME)
    if existing:
        return ResponseBase(msg="Admin already exists")
    user = user_crud.create_with_password(db, username=settings.ADMIN_USERNAME, password=settings.ADMIN_PASSWORD, auth_level="super_admin")
    return ResponseBase(msg="Admin created successfully")
