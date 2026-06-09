from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.db.session import SessionLocal, engine, Base
from app.api.v1.api import api_router
from app.schemas.common import ResponseBase
from app.crud.user import user_crud
from app.models.user import User
from app.models.func import FuncBase, FuncCategory, FuncCategoryRelation, FuncAudit


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == settings.ADMIN_USERNAME).first()
        if not admin:
            user_crud.create_with_password(
                db, username=settings.ADMIN_USERNAME, password=settings.ADMIN_PASSWORD, auth_level="super_admin"
            )
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS_LIST,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ResponseBase(code=500, msg=f"Server error: {str(exc)}").model_dump()
    )


@app.get("/", response_model=ResponseBase)
@limiter.limit("100/minute")
async def root(request: Request):
    return ResponseBase(msg="OpenFuncDB API is running")


@app.get("/health", response_model=ResponseBase)
@limiter.limit("100/minute")
async def health_check(request: Request):
    return ResponseBase(data={"status": "healthy"})


app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
