# OpenFuncDB API 接口文档

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API 前缀**: `/api/v1`
- **认证方式**: Bearer Token（JWT）
- **响应格式**:

```json
{
  "code": 200,
  "msg": "success",
  "data": {}
}
```

## 接口清单

### 1. 服务健康检查

无需认证。

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 服务状态 |
| GET | `/health` | 健康检查 |

### 2. 鉴权模块

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/auth/login` | 登录获取 Token | 否 |
| GET | `/api/v1/auth/me` | 获取当前用户信息 | 是 |
| POST | `/api/v1/auth/init-admin` | 初始化管理员账号 | 否 |

#### 登录示例

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your_admin&password=your_password"
```

#### 使用 Token 访问受保护接口

```bash
curl http://localhost:8000/api/v1/func/list \
  -H "Authorization: Bearer <your_token>"
```

### 3. 函数模块

所有接口需认证。

| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| GET | `/api/v1/func/list` | 函数列表 | func_type, is_safe, page, size |
| GET | `/api/v1/func/detail/{func_id}` | 函数详情 | func_id (path) |
| POST | `/api/v1/func/submit` | 提交新函数 | Body: func_type, func_name, func_content, func_desc |
| POST | `/api/v1/func/audit/{func_id}` | 审核函数（管理员） | Body: audit_status, audit_remark |

#### 函数列表查询

```bash
curl "http://localhost:8000/api/v1/func/list?func_type=Python&page=1&size=10" \
  -H "Authorization: Bearer <token>"
```

#### 提交新函数

```bash
curl -X POST http://localhost:8000/api/v1/func/submit \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "func_type": "Python",
    "func_name": "print",
    "func_content": "print(*objects, sep=' ', end='\\n')",
    "func_desc": "打印输出到控制台"
  }'
```

#### 审核函数

```bash
curl -X POST http://localhost:8000/api/v1/func/audit/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"audit_status": 1, "audit_remark": "审核通过"}'
```

### 4. 分类模块

所有接口需认证。

| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| GET | `/api/v1/category/list` | 分类列表 | func_type (可选) |

## 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证/Token 无效 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 422 | 参数校验失败 |
| 429 | 请求过于频繁（限流） |
| 500 | 服务器内部错误 |
