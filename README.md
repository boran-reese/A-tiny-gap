# A-tiny-gap Backend

“帮你过完今天”的轻量叙事 + 治愈模拟游戏的 FastAPI 后端骨架，实现了用户体系、每日 Session、心象小镇、成长统计与「星光信箱」。

## 快速开始

1. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```
2. 设置数据库，默认使用 PostgreSQL：
   ```bash
   export DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/littlegap
   ```
   也可以在 `.env` 中写入 `DATABASE_URL`。
3. 启动服务
   ```bash
   uvicorn app.main:app --reload
   ```

首次启动会自动创建所有表（示例环境下使用 SQLAlchemy `create_all`）。线上环境建议改用 Alembic 迁移。

## 目录结构

```
app/
├─ main.py            # FastAPI 入口
├─ config.py          # 配置管理
├─ database.py        # SQLAlchemy 引擎与 Session
├─ deps.py            # FastAPI 依赖（当前用户、DB）
├─ models/            # SQLAlchemy ORM 模型
├─ routers/           # 各功能路由：auth/session/world/starlight/profile
├─ schemas/           # Pydantic 数据模型
└─ services/          # 情绪推断、AI 导演等业务逻辑
```

## 已实现的 API 概览

- `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/me`
- `/session/start`, `/session/{id}/interaction`, `/session/{id}/director/recommend`, `/session/{id}/complete`
- `/world/state` (GET/PATCH)
- `/starlight/send`, `/starlight/draw`
- `/me/profile` (GET/PATCH), `/me/growth`, `/me/history/mood`

所有非公开接口均需携带 `Authorization: Bearer <token>`。

## 后续扩展建议

- 将 `services/director.py` 的 `call_llm` 对接真实 LLM，丰富剧情计划。
- 用 Alembic 管理迁移，并将 `create_all` 替换掉。
- 在 `GrowthEvent`、`PlaySession` 结束逻辑里补充更复杂的成长统计。
- 根据前端需求扩展剧情模型、小游戏交互等更多表结构。
