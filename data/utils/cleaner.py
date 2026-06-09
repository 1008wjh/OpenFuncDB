# -*- coding: utf-8 -*-
"""
数据清洗器
功能：对原始 JSON 数据进行三层清洗
  - 去噪：去除空白、HTML 标签残留、格式乱码
  - 规则过滤：去除非函数条目（如类构造器 class*）、修复名称
  - 质量清洗：去重、补缺失字段
"""

import json
import re
import os


def clean_text(text: str) -> str:
    """去除多余空白和 HTML 残留"""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def filter_non_functions(items: list) -> list:
    """过滤掉非函数条目（如 classbool, classbytearray 等类构造器）"""
    skipped_prefixes = ("class", "awaitable")
    clean_items = []
    removed = []
    for item in items:
        name = item.get("func_name", "")
        if name.startswith(skipped_prefixes):
            removed.append(name)
            continue
        clean_items.append(item)
    if removed:
        print(f"  过滤非函数条目 {len(removed)} 个: {removed}")
    return clean_items


def fix_func_names(items: list) -> list:
    """修复函数名称（去掉 class/awaitable 前缀等）"""
    name_map = {
        "classbool": "bool",
        "classbytearray": "bytearray",
        "classbytes": "bytes",
        "classcomplex": "complex",
        "classdict": "dict",
        "classfloat": "float",
        "classfrozenset": "frozenset",
        "classint": "int",
        "classlist": "list",
        "classmemoryview": "memoryview",
        "classobject": "object",
        "classproperty": "property",
        "classrange": "range",
        "classreversed": "reversed",
        "classset": "set",
        "classslice": "slice",
        "classstaticmethod": "staticmethod",
        "classstr": "str",
        "classtuple": "tuple",
        "classtype": "type",
    }
    for item in items:
        name = item.get("func_name", "")
        if name in name_map:
            item["func_name"] = name_map[name]
    return items


def dedup(items: list) -> list:
    """按 func_name 去重，保留第一次出现"""
    seen = set()
    unique = []
    for item in items:
        name = item.get("func_name", "")
        if name not in seen:
            seen.add(name)
            unique.append(item)
    return unique


def build_standard_record(item: dict) -> dict:
    """将原始记录映射为标准化 schema"""
    func_name = item.get("func_name", "")
    func_desc = clean_text(item.get("func_desc", ""))
    return {
        "func_type": "Python",
        "func_name": func_name,
        "func_content": f"{func_name}()",
        "func_desc": func_desc,
        "func_params": "",
        "func_return": "",
        "is_safe": True,
    }


def run_clean(input_path: str, output_path: str):
    """执行完整清洗流程"""
    print(f"\n{'='*50}")
    print("数据清洗开始")
    print(f"{'='*50}")
    print(f"输入: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    print(f"原始数据: {len(raw_data)} 条")

    data = filter_non_functions(raw_data)
    data = dedup(data)
    data = [build_standard_record(item) for item in data]
    print(f"清洗后: {len(data)} 条")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"输出: {output_path}")
    print(f"{'='*50}")
    return data


if __name__ == "__main__":
    run_clean(
        input_path="../source/python_official_raw.json",
        output_path="../cleaned/python_cleaned.json",
    )
