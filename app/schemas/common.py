from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar('T')


class ResponseBase(BaseModel, Generic[T]):
    code: int = 200
    msg: str = "success"
    data: Optional[T] = None


class PaginationParams(BaseModel):
    page: int = 1
    size: int = 10


class PaginationResult(BaseModel, Generic[T]):
    list: list[T]
    total: int
    page: int
    size: int
    pages: int
