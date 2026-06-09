# -*- coding: utf-8 -*-
"""
数据导入主脚本
流水线：解析 → 清洗 → 入库
支持多数据源：Python 内置 / 标准库 / 数据科学 / Linux / Git / Java
"""

import os
import sys
import json

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(CUR_DIR, ".."))

RAW_PATH = os.path.join(CUR_DIR, "source", "python_official_raw.json")
CLEANED_DIR = os.path.join(CUR_DIR, "cleaned")
SOURCE_DIR = os.path.join(CUR_DIR, "source")


def ensure_cleaned_dir():
    os.makedirs(CLEANED_DIR, exist_ok=True)


def step1_parse_python_builtins():
    """解析 Python 官方文档 → raw JSON"""
    if os.path.exists(RAW_PATH):
        print(f"  原始数据已存在: {RAW_PATH}")
        return
    from data.utils.official_parser import get_page_html, parse_functions_full, save_raw_data
    html = get_page_html()
    funcs = parse_functions_full(html)
    save_raw_data(funcs, RAW_PATH)


def step2_clean_and_import():
    """对所有数据源执行清洗+入库"""
    from data.utils.cleaner import run_clean, clean_list
    from data.utils.importer import import_list

    # ---------- 数据源 1: Python 内置函数 ----------
    print("\n" + "=" * 60)
    print("[PKG] 数据源 1/6: Python 内置函数")
    print("=" * 60)
    cleaned_path = os.path.join(CLEANED_DIR, "python_builtin.json")
    if os.path.exists(RAW_PATH):
        items = run_clean(RAW_PATH, cleaned_path)
    else:
        print("  ⚠️ 原始数据不存在，跳过")

    # ---------- 数据源 2: Python 标准库 ----------
    print("\n" + "=" * 60)
    print("[PKG] 数据源 2/6: Python 标准库 (os/sys/pathlib/re/json 等)")
    print("=" * 60)
    stdlib_path = os.path.join(SOURCE_DIR, "python_stdlib.json")
    if os.path.exists(stdlib_path):
        with open(stdlib_path, "r", encoding="utf-8") as f:
            items = json.load(f)
        items = clean_list(items)
        cleaned_path = os.path.join(CLEANED_DIR, "python_stdlib.json")
        with open(cleaned_path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        print(f"   清洗后: {len(items)} 条")

    # ---------- 数据源 3: Python 数据科学 ----------
    print("\n" + "=" * 60)
    print("[PKG] 数据源 3/6: Python 数据科学 (Pandas/NumPy)")
    print("=" * 60)
    ds_path = os.path.join(SOURCE_DIR, "python_datascience.json")
    if os.path.exists(ds_path):
        with open(ds_path, "r", encoding="utf-8") as f:
            items = json.load(f)
        items = clean_list(items)
        cleaned_path = os.path.join(CLEANED_DIR, "python_datascience.json")
        with open(cleaned_path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        print(f"   清洗后: {len(items)} 条")

    # ---------- 数据源 4: Linux 命令 ----------
    print("\n" + "=" * 60)
    print("[PKG] 数据源 4/6: Linux 命令")
    print("=" * 60)
    linux_path = os.path.join(SOURCE_DIR, "linux_commands.json")
    if os.path.exists(linux_path):
        with open(linux_path, "r", encoding="utf-8") as f:
            items = json.load(f)
        items = clean_list(items)
        cleaned_path = os.path.join(CLEANED_DIR, "linux_commands.json")
        with open(cleaned_path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        print(f"   清洗后: {len(items)} 条")

    # ---------- 数据源 5: Git 命令 ----------
    print("\n" + "=" * 60)
    print("[PKG] 数据源 5/6: Git 命令")
    print("=" * 60)
    git_path = os.path.join(SOURCE_DIR, "git_commands.json")
    if os.path.exists(git_path):
        with open(git_path, "r", encoding="utf-8") as f:
            items = json.load(f)
        items = clean_list(items)
        cleaned_path = os.path.join(CLEANED_DIR, "git_commands.json")
        with open(cleaned_path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        print(f"   清洗后: {len(items)} 条")

    # ---------- 数据源 6: Java 常用 ----------
    print("\n" + "=" * 60)
    print("[PKG] 数据源 6/6: Java 常用类和方法")
    print("=" * 60)
    java_path = os.path.join(SOURCE_DIR, "java_common.json")
    if os.path.exists(java_path):
        with open(java_path, "r", encoding="utf-8") as f:
            items = json.load(f)
        items = clean_list(items)
        cleaned_path = os.path.join(CLEANED_DIR, "java_common.json")
        with open(cleaned_path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        print(f"   清洗后: {len(items)} 条")


def step3_import_all():
    """将所有清洗后的数据入库"""
    from data.utils.importer import import_list

    total = {"inserted": 0, "updated": 0, "skipped": 0}
    files = [
        ("Python 内置函数", "python_builtin.json"),
        ("Python 标准库", "python_stdlib.json"),
        ("Python 数据科学", "python_datascience.json"),
        ("Linux 命令", "linux_commands.json"),
        ("Git 命令", "git_commands.json"),
        ("Java 常用", "java_common.json"),
    ]

    for name, filename in files:
        fpath = os.path.join(CLEANED_DIR, filename)
        if not os.path.exists(fpath):
            print(f"\n  ⚠️ {name}: 文件不存在，跳过")
            continue

        print(f"\n{'='*60}")
        print(f"[IMP] 入库: {name}")
        print(f"{'='*60}")

        with open(fpath, "r", encoding="utf-8") as f:
            items = json.load(f)

        stats = import_list(items)
        for k in total:
            total[k] += stats.get(k, 0)

    return total


if __name__ == "__main__":
    print("=" * 60)
    print(" OpenFuncDB 数据导入流水线")
    print("=" * 60)

    # Step 1: 解析官方文档
    print("\n[LIST] Step 1: 解析 Python 官方文档")
    step1_parse_python_builtins()

    # Step 2: 清洗所有数据源
    print("\n[LIST] Step 2: 清洗所有数据源")
    ensure_cleaned_dir()
    step2_clean_and_import()

    # Step 3: 入库
    print("\n[LIST] Step 3: 入库")
    totals = step3_import_all()

    print("\n" + "=" * 60)
    print(f"[DONE] 全部完成！")
    print(f"   新增: {totals['inserted']}, 更新: {totals['updated']}, 跳过: {totals['skipped']}")
    print("=" * 60)
