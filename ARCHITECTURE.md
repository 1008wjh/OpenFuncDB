# OpenFuncDB 标准架构

## 项目结构

```
OpenFuncDB/
├── app/
│   ├── __init__.py
│   ├── api/                    # Controller 层
│   │   └── v1/
│   │       ├── api.py         # 路由聚合
│   │       └── endpoints/     # 具体接口
│   │           ├── auth.py
│   │           ├── func.py
│   │           └── category.py
│   ├── core/                  # 核心配置
│   │   ├── config.py          # 配置管理
│   │   └── security.py        # 安全、JWT
│   ├── db/                    # 数据库
│   │   └── session.py         # 会话管理
│   ├── models/                # Model 层 (SQLAlchemy ORM)
│   │   ├── __init__.py
│   │   ├── func.py
│   │   └── user.py
│   ├── schemas/               # Schema 层 (Pydantic)
│   │   ├── __init__.py
│   │   ├── common.py
│   │   ├── func.py
│   │   └── user.py
│   ├── crud/                  # Repository 层 (数据访问)
│   │   ├── __init__.py
│   │   ├── base.py            # 基础 CRUD
│   │   ├── func.py
│   │   └── user.py
│   └── services/              # Service 层 (业务逻辑)
│       ├── __init__.py
│       └── func_service.py
├── alembic/                   # 数据库迁移
│   └── env.py
├── alembic.ini
├── main.py                    # 应用入口
├── requirements.txt
└── .env
```

## 架构分层 (类似 Spring Boot)

### 1. Models (Entity 层)
- SQLAlchemy ORM 模型
- 对应数据库表结构
- 位置: `app/models/`

### 2. Schemas (DTO 层)
- Pydantic 模型
- 请求/响应数据验证
- 位置: `app/schemas/`

### 3. CRUD (Repository 层)
- 基础数据访问操作
- 继承自 CRUDBase 基类
- 位置: `app/crud/`

### 4. Services (业务逻辑层)
- 复杂业务逻辑
- 事务管理
- 位置: `app/services/`

### 5. API (Controller 层)
- 路由定义
- 参数绑定
- 响应包装
- 位置: `app/api/v1/endpoints/`

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
复制 `.env.example` 为 `.env` 并修改配置

### 3. 初始化数据库迁移
```bash
# 创建迁移脚本
alembic revision --autogenerate -m "init"

# 执行迁移
alembic upgrade head
```

### 4. 启动服务
```bash
python main.py
```

### 5. 初始化管理员
访问: `POST /api/v1/auth/init-admin`

默认账号: `admin` / `admin123`

## API 文档
启动服务后访问: `http://127.0.0.1:8000/docs`
