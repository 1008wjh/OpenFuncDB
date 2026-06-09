from fastapi import APIRouter

from app.api.v1.endpoints import auth, func, category

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(func.router, prefix="/func", tags=["Functions"])
api_router.include_router(category.router, prefix="/category", tags=["Categories"])
