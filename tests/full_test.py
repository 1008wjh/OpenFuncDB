"""完整端到端API测试 — 自动从数据库获取Agent API Key"""
import requests
import json
import sys
from sqlalchemy import create_engine, text

# ── 数据库连接获取 Agent API Key ──
ENGINE = create_engine("mysql+pymysql://root:root@localhost:3306/openfunc_db?charset=utf8mb4", pool_pre_ping=True)

def get_agent_key():
    with ENGINE.connect() as conn:
        r = conn.execute(text("SELECT api_key FROM agent_api_key WHERE key_name='default' AND is_active=1 LIMIT 1"))
        row = r.fetchone()
        return row[0] if row else None

AGENT_KEY = get_agent_key()
if not AGENT_KEY:
    # fallback: try generating and inserting
    import secrets
    AGENT_KEY = secrets.token_hex(32)
    with ENGINE.connect() as conn:
        conn.execute(text("INSERT INTO agent_api_key (key_name, api_key, is_active) VALUES ('default', :k, 1)"), {"k": AGENT_KEY})
        conn.commit()

print(f"Agent API Key: {AGENT_KEY[:16]}...")
print()

# ── 测试框架 ──
BASE = "http://127.0.0.1:8000"
passed = 0
failed = 0
failures = []

# 一些标志
_HAD_401 = False  # 登录类端点的401也算通过

def test(name, method, path, expected_status=200, **kwargs):
    global passed, failed
    url = f"{BASE}{path}"
    try:
        resp = requests.request(method, url, timeout=15, **kwargs)
        ok = resp.status_code == expected_status
        if ok:
            passed += 1
            preview = resp.text[:120].replace("\n", " ")
            print(f"  [PASS] {name}  ({resp.status_code})")
            return resp
        else:
            failed += 1
            preview = resp.text[:300].replace("\n", " ")
            failures.append((name, f"status={resp.status_code} expected={expected_status}\n  {preview}"))
            print(f"  [FAIL] {name}  status={resp.status_code} expected={expected_status}")
            return resp
    except Exception as e:
        failed += 1
        failures.append((name, str(e)))
        print(f"  [FAIL] {name}: {e}")
        return None

print("=" * 60)
print("OpenFuncDB API 完整端到端测试")
print("=" * 60)

# ═══ 1-2. 健康检查 ═══
test("1. Health Check", "GET", "/health")
test("2. Root", "GET", "/")

# ═══ 3. 登录 ═══
r = test("3. Login", "POST", "/api/v1/auth/login",
         data={"username": "admin", "password": "admin123"}, expected_status=200)
if r and r.status_code == 200:
    token = r.json()["data"]["access_token"]
    user_headers = {"Authorization": f"Bearer {token}"}
    print(f"       Token: {token[:50]}...")
else:
    user_headers = {}

# ═══ 4-8. 函数 CRUD（需登录） ═══
test("4. Function List", "GET", "/api/v1/func/list?page=1&size=5", headers=user_headers)
test("5. Function Search", "GET", "/api/v1/func/search?keyword=length&page=1&size=5", headers=user_headers)
test("6. Function Detail", "GET", "/api/v1/func/detail/1", headers=user_headers)
test("7. Category List", "GET", "/api/v1/category/list", headers=user_headers)

# ═══ 9-12. Agent API（X-API-Key 认证） ═══
agent_headers = {"X-API-Key": AGENT_KEY}
test("8. Agent Tools (OpenAI格式)", "GET", "/api/v1/agent/tools?limit=5", headers=agent_headers)
test("9. Agent Tools Search (RAG)", "GET", "/api/v1/agent/tools/search?q=how to get length of string&top_k=5", headers=agent_headers)
test("10. Agent Call by Name", "GET", "/api/v1/agent/call/by-name?func_type=Python&func_name=len", headers=agent_headers)
test("11. Agent Call by ID", "GET", "/api/v1/agent/call/1", headers=agent_headers)

# ═══ 13-14. RAG 检索（人类用户） ═══
test("12. Human RAG Search", "GET", "/api/v1/rag/search?q=how to sort a list&top_k=5", headers=user_headers)
test("13. RAG Refresh", "POST", "/api/v1/rag/refresh", headers=user_headers)

# ═══ 15. 未认证保护 ═══
test("14. Unauthorized Access (no token)", "GET", "/api/v1/func/list?page=1&size=1", expected_status=401)
test("15. Bad Agent Key", "GET", "/api/v1/agent/tools?limit=1", expected_status=401,
     headers={"X-API-Key": "invalid-key-12345"})

print()
print("=" * 60)
print(f"结果: {passed}/{passed + failed} 通过")
if failures:
    print(f"\n失败详情 ({len(failures)}):")
    for name, detail in failures:
        print(f"  [{name}] {detail}")
print("=" * 60)

# 关键检查：简历核心功能
print()
print("── 简历核心功能验证 ──")
core_ok = True
r1 = r2 = None
try:
    r1 = requests.get(f"{BASE}/api/v1/agent/tools?limit=3", headers={"X-API-Key": AGENT_KEY})
    has_tools = "tools" in r1.json() and r1.status_code == 200
    print(f"  AI Agent Function Calling: {'[OK]' if has_tools else '[FAIL]'}")

    r2 = requests.get(f"{BASE}/api/v1/rag/search?q=string length", headers=user_headers)
    has_rag = "results" in r2.json().get("data", {}) and r2.status_code == 200
    print(f"  RAG Search Toolchain: {'[OK]' if has_rag else '[FAIL]'}")

    if has_tools and has_rag:
        print("\n*** All core features verified! ***")
    else:
        core_ok = False
        print("\n*** Core features need fixing ***")
except Exception as e:
    core_ok = False
    print(f"\n[FAIL] Verification error: {e}")

sys.exit(0 if (passed + failed > 0 and failed == 0 and core_ok) else 1)
