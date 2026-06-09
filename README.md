# OpenFuncDB

AI 智能体安全网络数据库 — 为 AI 智能体提供安全合规的 Linux/Python/Git/Shell 等技术数据 API

## 项目概述

OpenFuncDB 是一个面向 AI 智能体的安全结构化知识库，通过 RESTful API 提供经过安全审核的技术函数/命令数据。项目采用 FastAPI + SQLAlchemy + MySQL 技术栈，遵循标准分层架构设计。

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填写数据库连接信息

# 3. 初始化数据库
python -m alembic upgrade head

# 4. 启动服务
python main.py

# 5. 初始化管理员
curl -X POST http://localhost:8000/api/v1/auth/init-admin
```

默认管理员账号：`admin` / `admin123`

## 技术栈

| 组件 | 技术 |
|------|------|
| 框架 | FastAPI 0.104 |
| 数据库 | MySQL 8.0 + SQLAlchemy 2.0 |
| 迁移 | Alembic |
| 验证 | Pydantic 2.5 |
| 鉴权 | JWT + OAuth2 |
| 文档 | Swagger UI / Redoc |

## API 文档

服务启动后访问：
- Swagger UI: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

## 项目结构

```
OpenFuncDB/
├── app/                  # 应用核心代码
│   ├── api/v1/          # Controller 层
│   ├── core/            # 配置与安全
│   ├── crud/            # Repository 层
│   ├── db/              # 数据库会话
│   ├── models/          # ORM 模型
│   ├── schemas/         # 数据验证
│   └── services/        # 业务逻辑
├── alembic/             # 数据库迁移
├── data/                # 数据处理
├── docs/                # 项目文档
├── main.py              # 应用入口
└── requirements.txt     # 依赖清单
```

## 文档索引

| 文档 | 说明 |
|------|------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | 架构分层说明 |
| [docs/01-项目规划.md](docs/01-项目规划.md) | 项目规划与路线图 |
| [docs/02-数据库设计.md](docs/02-数据库设计.md) | 数据库表结构 |
| [docs/03-API接口文档.md](docs/03-API接口文档.md) | 接口清单与说明 |
| [docs/04-数据处理流程.md](docs/04-数据处理流程.md) | 数据清洗与导入 |
| [docs/05-环境配置与部署.md](docs/05-环境配置与部署.md) | 环境与部署指南 |

## License

MIT
