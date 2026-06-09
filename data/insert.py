# -*- coding: utf-8 -*-
"""
数据导入主脚本
严格按照三步流水线执行：
  1. 官方源解析（如果 raw 数据不存在）
  2. 数据清洗 → cleaned/
  3. ORM 入库
"""

import os
import sys

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(CUR_DIR, ".."))

RAW_PATH = os.path.join(CUR_DIR, "source", "python_official_raw.json")
CLEANED_PATH = os.path.join(CUR_DIR, "cleaned", "python_cleaned.json")


def step1_parse():
    """若 raw 数据不存在则解析官方文档"""
    if os.path.exists(RAW_PATH):
        print(f"原始数据已存在: {RAW_PATH}")
        return
    from data.utils.official_parser import get_page_html, parse_functions_full, save_raw_data
    html = get_page_html()
    funcs = parse_functions_full(html)
    save_raw_data(funcs, RAW_PATH)


def step2_clean():
    from data.utils.cleaner import run_clean
    run_clean(RAW_PATH, CLEANED_PATH)


def step3_import():
    from data.utils.importer import import_data
    import_data(CLEANED_PATH)


if __name__ == "__main__":
    print("=" * 50)
    print("OpenFuncDB 数据导入流水线")
    print("=" * 50)

    step1_parse()
    step2_clean()
    step3_import()

    print("\n数据导入流水线执行完毕!")
