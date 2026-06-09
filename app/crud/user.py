from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class CRUDUser(CRUDBase[User]):
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        query = select(self.model).where(self.model.username == username)
        return db.execute(query).scalar_one_or_none()

    def create_with_password(self, db: Session, *, username: str, password: str, auth_level: str = "user") -> User:
        hashed_password = pwd_context.hash(password)
        user_obj = {
            "username": username,
            "hashed_password": hashed_password,
            "auth_level": auth_level
        }
        return self.create(db, obj_in=user_obj)

    def authenticate(self, db: Session, *, username: str, password: str) -> Optional[User]:
        user = self.get_by_username(db, username=username)
        if not user:
            return None
        if not pwd_context.verify(password, user.hashed_password):
            return None
        return user


user_crud = CRUDUser(User)
