"""AI Agent 自主函数调用接口
遵循 OpenAI Function Calling 协议 — AI Agent 可自主发现并调用函数
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.agent_auth import verify_agent_api_key
from app.crud.func import func_base_crud
from app.services.rag_engine import rag_engine
from app.schemas.common import ResponseBase

router = APIRouter()

# ── 类型映射 ──
TYPE_MAP = {
    "int": "integer", "float": "number", "bool": "boolean",
    "str": "string", "list": "array", "dict": "object",
    "None": "null", "number": "number",
}


def _build_openai_tool(func) -> dict:
    """将函数记录转换为 OpenAI tool 定义"""
    # 解析参数为 JSON Schema properties
    params_str = (func.func_params or "").strip()
    properties = {}
    required = []

    if params_str:
        parts = [p.strip() for p in params_str.split(",") if p.strip()]
        for p in parts:
            # 去掉 * 前缀和默认值
            p = p.lstrip("*")
            if "=" in p:
                p_name, default = p.split("=", 1)
                p_name = p_name.strip()
            else:
                p_name = p
                required.append(p_name)

            # 尝试从类型名推断
            p_lower = p_name.lower()
            if p_lower in TYPE_MAP:
                continue  # 不是参数名
            properties[p_name] = {
                "type": "string",
                "description": f"Parameter: {p_name}",
            }

    return {
        "type": "function",
        "function": {
            "name": f"{func.func_type}_{func.func_name}".lower().replace(".", "_"),
            "description": f"[{func.func_type}] {func.func_name}: {func.func_desc or ''}"[:1024],
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


# ── API 端点 ──

@router.get("/tools")
async def list_tools(
    func_type: Optional[str] = Query(None),
    is_safe: Optional[bool] = Query(True),
    limit: int = Query(200, le=500),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_agent_api_key),
):
    """
    获取 OpenAI 兼容的工具列表 (Function Calling)

    AI Agent 调用此接口获取所有可用函数，然后按需调用 /call 获取详情。
    兼容 OpenAI / LangChain / AutoGPT 等框架的 function calling 协议。
    """
    funcs = func_base_crud.get_multi_filtered(
        db, func_type=func_type, is_safe=is_safe, limit=limit
    )
    tools = [_build_openai_tool(f) for f in funcs]
    return {
        "tools": tools,
        "count": len(tools),
    }


@router.get("/tools/search")
async def search_tools(
    q: str = Query(..., min_length=1),
    top_k: int = Query(10, le=50),
    func_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_agent_api_key),
):
    """
    RAG 增强搜索工具列表

    AI Agent 用自然语言描述需求，返回最相关的函数作为 tool 列表。
    这让 Agent 不需要遍历所有工具，只获取相关的几个。
    """
    # 刷新索引
    if not rag_engine._built:
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

    results = rag_engine.search(q, top_k=top_k, func_type=func_type)

    # 加载完整函数对象构建 tool
    ids = [r["id"] for r in results]
    funcs = db.query(func_base_crud.model).filter(
        func_base_crud.model.id.in_(ids)
    ).all()
    func_map = {f.id: f for f in funcs}

    tools = []
    for r in results:
        f = func_map.get(r["id"])
        if f:
            tool = _build_openai_tool(f)
            tool["relevance"] = r["score"]
            tools.append(tool)

    return {"query": q, "tools": tools, "count": len(tools)}


@router.get("/call/by-name")
async def call_function_by_name(
    func_type: str = Query(..., description="函数类型"),
    func_name: str = Query(..., description="函数名"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_agent_api_key),
):
    """
    按类型+名称查询函数详情（供 Agent 精确调用）
    """
    func = db.query(func_base_crud.model).filter(
        func_base_crud.model.func_type == func_type,
        func_base_crud.model.func_name == func_name,
    ).first()

    if not func:
        raise HTTPException(status_code=404, detail="Function not found")

    return ResponseBase(data={
        "id": func.id,
        "name": func.func_name,
        "type": func.func_type,
        "signature": func.func_content,
        "description": func.func_desc,
        "parameters": func.func_params,
        "return_type": func.func_return,
        "is_safe": func.is_safe,
    })


@router.get("/call/{func_id}")
async def call_function(
    func_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_agent_api_key),
):
    """
    AI Agent 调用指定函数获取完整定义

    返回函数的完整签名、参数说明、返回值类型、安全标记，
    Agent 可据此生成正确的代码。
    """
    func = func_base_crud.get(db, func_id)
    if not func:
        raise HTTPException(status_code=404, detail="Function not found")

    return ResponseBase(data={
        "id": func.id,
        "name": func.func_name,
        "type": func.func_type,
        "signature": func.func_content,
        "description": func.func_desc,
        "parameters": func.func_params,
        "return_type": func.func_return,
        "is_safe": func.is_safe,
        "usage_example": f"# 调用方式\n{func.func_content}",
    })
