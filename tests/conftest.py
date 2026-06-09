import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from main import app

SQLITE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db():
    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers(client, db):
    """创建管理员并登录，返回带 token 的 headers"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    from app.models.user import User

    admin = User(
        username="admin",
        hashed_password=pwd_context.hash("admin123"),
        auth_level="super_admin",
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    resp = client.post("/api/v1/auth/login", data={"username": "admin", "password": "admin123"})
    token = resp.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
