# -*- coding: utf-8 -*-
"""
数据清洗器
三层清洗流水线：
  1. 去噪：HTML残留、空白字符、乱码
  2. 规则清洗：规范化函数名、生成签名、安全判定
  3. 质量清洗：去重、补全、排序
"""

import json
import re
import os
from typing import Any


# ============================================================
# Python 内置函数签名库
# ============================================================
PYTHON_BUILTIN_SIGNATURES = {
    "abs":        ("abs(x)", "x", "number"),
    "aiter":      ("aiter(async_iterable)", "async_iterable", "async_iterator"),
    "all":        ("all(iterable)", "iterable", "bool"),
    "any":        ("any(iterable)", "iterable", "bool"),
    "ascii":      ("ascii(object)", "object", "str"),
    "bin":        ("bin(x)", "x", "str"),
    "bool":       ("bool(x=False)", "x", "bool"),
    "breakpoint": ("breakpoint(*args, **kws)", "*args, **kws", "None"),
    "bytearray":  ("bytearray(source=b'')", "source, encoding, errors", "bytearray"),
    "bytes":      ("bytes(source=b'')", "source, encoding, errors", "bytes"),
    "callable":   ("callable(object)", "object", "bool"),
    "chr":        ("chr(i)", "i", "str"),
    "classmethod":("classmethod(function)", "function", "classmethod"),
    "compile":    ("compile(source, filename, mode, flags=0, dont_inherit=False, optimize=-1)",
                   "source, filename, mode, flags, dont_inherit, optimize", "code object"),
    "complex":    ("complex(real=0, imag=0)", "real, imag", "complex"),
    "delattr":    ("delattr(object, name)", "object, name", "None"),
    "dict":       ("dict(**kwargs)", "**kwargs", "dict"),
    "dir":        ("dir(object=None)", "object", "list"),
    "divmod":     ("divmod(a, b)", "a, b", "tuple"),
    "enumerate":  ("enumerate(iterable, start=0)", "iterable, start", "enumerate"),
    "eval":       ("eval(expression, globals=None, locals=None)", "expression, globals, locals", "Any"),
    "exec":       ("exec(object, globals=None, locals=None)", "object, globals, locals", "None"),
    "filter":     ("filter(function, iterable)", "function, iterable", "iterator"),
    "float":      ("float(x=0.0)", "x", "float"),
    "format":     ("format(value, format_spec='')", "value, format_spec", "str"),
    "frozenset":  ("frozenset(iterable=())", "iterable", "frozenset"),
    "getattr":    ("getattr(object, name, default=None)", "object, name, default", "Any"),
    "globals":    ("globals()", "", "dict"),
    "hasattr":    ("hasattr(object, name)", "object, name", "bool"),
    "hash":       ("hash(object)", "object", "int"),
    "help":       ("help(object=None)", "object", "None"),
    "hex":        ("hex(x)", "x", "str"),
    "id":         ("id(object)", "object", "int"),
    "input":      ("input(prompt='')", "prompt", "str"),
    "int":        ("int(x=0, base=10)", "x, base", "int"),
    "isinstance": ("isinstance(object, classinfo)", "object, classinfo", "bool"),
    "issubclass": ("issubclass(cls, classinfo)", "cls, classinfo", "bool"),
    "iter":       ("iter(object, sentinel=None)", "object, sentinel", "iterator"),
    "len":        ("len(s)", "s", "int"),
    "list":       ("list(iterable=())", "iterable", "list"),
    "locals":     ("locals()", "", "dict"),
    "map":        ("map(function, iterable, *iterables)", "function, iterable, *iterables", "iterator"),
    "max":        ("max(iterable, *, key=None, default=None)", "iterable, key, default", "Any"),
    "memoryview": ("memoryview(object)", "object", "memoryview"),
    "min":        ("min(iterable, *, key=None, default=None)", "iterable, key, default", "Any"),
    "next":       ("next(iterator, default=None)", "iterator, default", "Any"),
    "object":     ("object()", "", "object"),
    "oct":        ("oct(x)", "x", "str"),
    "open":       ("open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None)",
                   "file, mode, buffering, encoding, errors, newline, closefd, opener", "file object"),
    "ord":        ("ord(c)", "c", "int"),
    "pow":        ("pow(base, exp, mod=None)", "base, exp, mod", "number"),
    "print":      ("print(*objects, sep=' ', end='\\n', file=None, flush=False)",
                   "*objects, sep, end, file, flush", "None"),
    "property":   ("property(fget=None, fset=None, fdel=None, doc=None)", "fget, fset, fdel, doc", "property"),
    "range":      ("range(start, stop, step=1)", "start, stop, step", "range"),
    "repr":       ("repr(object)", "object", "str"),
    "reversed":   ("reversed(seq)", "seq", "iterator"),
    "round":      ("round(number, ndigits=None)", "number, ndigits", "number"),
    "set":        ("set(iterable=())", "iterable", "set"),
    "setattr":    ("setattr(object, name, value)", "object, name, value", "None"),
    "slice":      ("slice(start, stop, step=None)", "start, stop, step", "slice"),
    "sorted":     ("sorted(iterable, *, key=None, reverse=False)", "iterable, key, reverse", "list"),
    "staticmethod":("staticmethod(function)", "function", "staticmethod"),
    "str":        ("str(object='')", "object", "str"),
    "sum":        ("sum(iterable, start=0)", "iterable, start", "number"),
    "super":      ("super(type, object_or_type=None)", "type, object_or_type", "super"),
    "tuple":      ("tuple(iterable=())", "iterable", "tuple"),
    "type":       ("type(object)", "object", "type"),
    "vars":       ("vars(object=None)", "object", "dict"),
    "zip":        ("zip(*iterables, strict=False)", "*iterables, strict", "iterator"),
    "__import__": ("__import__(name, globals=None, locals=None, fromlist=(), level=0)",
                   "name, globals, locals, fromlist, level", "module"),
}

UNSAFE_FUNCTIONS = {"eval", "exec", "compile", "__import__", "open", "input"}

NAME_MAP = {
    "classbool": "bool", "classbytearray": "bytearray", "classbytes": "bytes",
    "classcomplex": "complex", "classdict": "dict", "classfloat": "float",
    "classfrozenset": "frozenset", "classint": "int", "classlist": "list",
    "classmemoryview": "memoryview", "classobject": "object",
    "classproperty": "property", "classrange": "range", "classset": "set",
    "classslice": "slice", "classstaticmethod": "staticmethod",
    "classstr": "str", "classtuple": "tuple", "classtype": "type",
    "classreversed": "reversed",
}


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_standard_record(item: dict, func_type: str = "Python") -> dict | None:
    func_name = item.get("func_name", "").strip()
    func_desc = item.get("func_desc", "").strip()

    if not func_name or not func_desc:
        return None

    # 修复类名前缀
    if func_name in NAME_MAP:
        func_name = NAME_MAP[func_name]

    # 过滤无效
    if func_name.startswith("class") or not func_name.isidentifier():
        return None
    if func_name in ("awaitableanext",):
        return None

    func_desc = clean_text(func_desc)
    if not func_desc or len(func_desc) > 2500:
        return None

    # 签名
    sig = PYTHON_BUILTIN_SIGNATURES.get(func_name)
    if sig:
        func_content, func_params, func_return = sig
    else:
        func_content = f"{func_name}()"
        func_params = ""
        func_return = ""

    is_safe_val = func_name not in UNSAFE_FUNCTIONS

    return {
        "func_type": func_type,
        "func_name": func_name,
        "func_content": func_content,
        "func_desc": func_desc[:500],
        "func_params": func_params,
        "func_return": func_return,
        "is_safe": is_safe_val,
    }


def dedup(items: list) -> list:
    seen = set()
    result = []
    for item in items:
        key = (item["func_type"], item["func_name"])
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def run_clean(input_path: str, output_path: str) -> list:
    print(f"\n{'='*50}")
    print(f" 数据清洗: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    print(f"   原始: {len(raw)} 条")

    cleaned = [r for item in raw if (r := build_standard_record(item))]
    cleaned = dedup(cleaned)
    cleaned.sort(key=lambda x: x["func_name"])

    print(f"   清洗后: {len(cleaned)} 条")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)
    print(f"   输出: {output_path}")
    return cleaned


def clean_list(items: list) -> list:
    """清洗已标准化的列表（去重+排序）"""
    return sorted(dedup([i for i in items if i.get("func_name") and i.get("func_content")]),
                  key=lambda x: x["func_name"])
