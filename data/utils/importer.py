# -*- coding: utf-8 -*-
"""
数据导入器
功能：将清洗后的 JSON 数据通过 ORM 事务写入数据库
  - 自动创建分类（如果不存在）
  - 去重：func_name 已存在则跳过
  - 同时写入 func_base、func_category_relation
  - 输出入库报告
"""

import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.func import FuncBase, FuncCategory, FuncCategoryRelation


def get_or_create_category(db: Session, func_type: str) -> int:
    """获取或创建分类，返回 category_id"""
    cat = db.query(FuncCategory).filter(
        FuncCategory.category_name == func_type,
        FuncCategory.func_type == func_type,
    ).first()
    if cat:
        return cat.id
    cat = FuncCategory(
        category_name=func_type,
        func_type=func_type,
        category_desc=f"{func_type} 内置函数",
    )
    db.add(cat)
    db.flush()
    return cat.id


def import_data(input_path: str) -> dict:
    """将清洗后的 JSON 写入数据库"""
    print(f"\n{'='*50}")
    print("数据导入开始")
    print(f"{'='*50}")
    print(f"输入: {input_path}")

    if not os.path.exists(input_path):
        print(f"文件不存在: {input_path}")
        return {}

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"待导入: {len(data)} 条")

    db = SessionLocal()
    stats = {"created": 0, "skipped": 0, "errors": 0}

    try:
        for item in data:
            func_name = item["func_name"]

            existing = db.query(FuncBase).filter(
                FuncBase.func_name == func_name,
                FuncBase.func_type == item["func_type"],
            ).first()
            if existing:
                stats["skipped"] += 1
                continue

            try:
                func = FuncBase(
                    func_type=item["func_type"],
                    func_name=func_name,
                    func_content=item.get("func_content", ""),
                    func_desc=item.get("func_desc", ""),
                    func_params=item.get("func_params"),
                    func_return=item.get("func_return"),
                    is_safe=item.get("is_safe", False),
                    create_time=datetime.now(timezone.utc),
                    update_time=datetime.now(timezone.utc),
                )
                db.add(func)
                db.flush()

                cat_id = get_or_create_category(db, item["func_type"])
                relation = FuncCategoryRelation(
                    func_id=func.id,
                    category_id=cat_id,
                )
                db.add(relation)
                stats["created"] += 1

            except Exception as exc:
                stats["errors"] += 1
                print(f"  错误 [{func_name}]: {exc}")

        db.commit()
        print(f"\n入库结果: 新建 {stats['created']}, 跳过 {stats['skipped']}, 错误 {stats['errors']}")
    except Exception as e:
        db.rollback()
        print(f"导入失败，已回滚: {e}")
        raise
    finally:
        db.close()

    print(f"{'='*50}")
    return stats


if __name__ == "__main__":
    import_data("../cleaned/python_cleaned.json")
