def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["msg"] == "OpenFuncDB API is running"


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "healthy"


def test_login_invalid(client):
    resp = client.post("/api/v1/auth/login", data={"username": "nobody", "password": "wrong"})
    assert resp.status_code == 401


def test_login_and_me(client, db, auth_headers):
    me_resp = client.get("/api/v1/auth/me", headers=auth_headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["data"]["username"] == "admin"


def test_func_list_empty(client, auth_headers):
    resp = client.get("/api/v1/func/list", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 0


def test_func_submit_and_detail(client, auth_headers):
    resp = client.post(
        "/api/v1/func/submit",
        json={
            "func_type": "Python",
            "func_name": "abs",
            "func_content": "abs(x)",
            "func_desc": "返回绝对值",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    func_id = resp.json()["data"]["id"]

    detail = client.get(f"/api/v1/func/detail/{func_id}", headers=auth_headers)
    assert detail.status_code == 200
    assert detail.json()["data"]["func_name"] == "abs"


def test_search(client, auth_headers):
    client.post(
        "/api/v1/func/submit",
        json={
            "func_type": "Python",
            "func_name": "abs",
            "func_content": "abs(x)",
            "func_desc": "返回绝对值",
        },
        headers=auth_headers,
    )
    resp = client.get("/api/v1/func/search?keyword=abs", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] >= 1


def test_audit_func(client, auth_headers):
    submit_resp = client.post(
        "/api/v1/func/submit",
        json={
            "func_type": "Python",
            "func_name": "print",
            "func_content": "print(*args)",
            "func_desc": "打印输出",
        },
        headers=auth_headers,
    )
    func_id = submit_resp.json()["data"]["id"]

    audit_resp = client.post(
        f"/api/v1/func/audit/{func_id}",
        json={"audit_status": 1, "audit_remark": "审核通过"},
        headers=auth_headers,
    )
    assert audit_resp.status_code == 200
    assert audit_resp.json()["data"]["is_safe"] is True


def test_update_func(client, auth_headers):
    submit_resp = client.post(
        "/api/v1/func/submit",
        json={
            "func_type": "Python",
            "func_name": "len",
            "func_content": "len(s)",
            "func_desc": "返回长度",
        },
        headers=auth_headers,
    )
    func_id = submit_resp.json()["data"]["id"]

    update_resp = client.put(
        f"/api/v1/func/update/{func_id}",
        json={"func_desc": "返回对象长度"},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["data"]["func_desc"] == "返回对象长度"


def test_category_crud(client, auth_headers):
    resp = client.post(
        "/api/v1/category/create",
        json={"category_name": "Python", "func_type": "Python", "category_desc": "Python内置函数"},
        headers=auth_headers,
    )
    assert resp.status_code == 200

    list_resp = client.get("/api/v1/category/list?func_type=Python", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()["data"]) >= 1
