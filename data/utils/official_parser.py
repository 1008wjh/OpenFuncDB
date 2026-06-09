# -*- coding: utf-8 -*-
"""
Python 官方内置函数完整解析器（最终稳定版 · 不漏抓）
功能：从 docs.python.org 解析所有内置函数，无遗漏
输出：data/source/python_official_raw.json
"""
import json
import requests
from bs4 import BeautifulSoup

# ===================== 固定配置 =====================
URL = "https://docs.python.org/zh-cn/3/library/functions.html"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
OUTPUT_PATH = "../source/python_official_raw.json"

# ===================== 获取页面 =====================
def get_page_html():
    print("正在获取 Python 官方文档...")
    resp = requests.get(URL, headers=HEADERS, timeout=(5, 15))
    resp.encoding = "utf-8"
    resp.raise_for_status()
    return resp.text

# ===================== 核心：完整解析规则（不漏） =====================
def parse_functions_full(html):
    soup = BeautifulSoup(html, "html.parser")
    function_list = []
    seen_names = set()  # 去重

    # ===== 策略1：抓所有带 dt > 函数名的节点（全覆盖）=====
    for dt in soup.find_all("dt"):
        # 取出 dt 里的文字（如 print(*args)）
        func_text = dt.get_text(strip=True)
        if not func_text:
            continue

        # 提取纯函数名：去掉括号和参数
        # 例子：print(*args, ...) → print
        func_name = func_text.split("(")[0].strip()

        # 只保留合法 Python 标识符
        if not func_name.isidentifier():
            continue

        # 去重
        if func_name in seen_names:
            continue
        seen_names.add(func_name)

        # 找对应的说明 dd
        dd = dt.find_next_sibling("dd")
        func_desc = dd.get_text(strip=True).replace("\n", " ").replace("  ", " ") if dd else ""

        function_list.append({
            "func_name": func_name,
            "func_desc": func_desc
        })

    print(f"✅ 本次共解析：{len(function_list)} 个内置函数")
    return function_list

# ===================== 保存 JSON =====================
def save_raw_data(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 原始数据已保存：{path}")

# ===================== 执行 =====================
if __name__ == "__main__":
    html = get_page_html()
    funcs = parse_functions_full(html)
    save_raw_data(funcs, OUTPUT_PATH)
    print("\n🎉 第一步：官方数据抓取 —— 全部完成！")