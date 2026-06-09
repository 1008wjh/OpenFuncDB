"""RAG 检索端点 — 语义搜索函数"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_active_user
from app.services.rag_engine import rag_engine
from app.crud.func import func_base_crud
from app.schemas.common import ResponseBase

router = APIRouter()


def _refresh_index(db: Session):
    """刷新 RAG 索引 — 从数据库加载所有函数"""
    funcs = db.execute(
        db.query(func_base_crud.model).statement
    ).scalars().all()

    docs = [
        {
            "id": f.id,
            "func_type": f.func_type,
            "func_name": f.func_name,
            "func_content": f.func_content,
            "func_desc": f.func_desc or "",
            "func_params": f.func_params or "",
            "func_return": f.func_return or "",
            "is_safe": f.is_safe,
            "text": f"{f.func_name} {f.func_type} {f.func_desc or ''} {f.func_params or ''} {f.func_return or ''}",
        }
        for f in funcs
    ]
    rag_engine.build_index(docs)


@router.post("/refresh")
async def refresh_rag_index(db: Session = Depends(get_db)):
    """手动刷新 RAG 索引"""
    _refresh_index(db)
    return ResponseBase(msg=f"RAG index refreshed, {len(rag_engine._docs)} docs indexed")


@router.get("/search")
async def rag_search(
    q: str = Query(..., min_length=1, description="自然语言查询"),
    func_type: Optional[str] = Query(None),
    top_k: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """RAG 语义搜索 — 用自然语言描述需求，返回最相关的函数"""
    # 自动刷新索引（首次或空时）
    if not rag_engine._built:
        _refresh_index(db)

    results = rag_engine.search(q, top_k=top_k, func_type=func_type)
    return ResponseBase(data={
        "query": q,
        "total": len(results),
        "results": results,
    })
