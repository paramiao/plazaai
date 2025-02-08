# 个人知识助手

一个基于 DeepSeek R1 和 Search1API 的智能问答助手，支持实时联网搜索和上下文对话。

## 主要功能

- 🔍 实时联网搜索：使用 Search1API 获取最新信息
- 🤖 智能对话：基于 DeepSeek R1 模型的自然语言处理
- 💬 上下文理解：支持多轮对话和上下文记忆
- 📝 搜索结果展示：清晰展示相关的搜索结果和来源链接
- 📚 会话管理：支持会话历史记录和查看

## 技术栈

### 后端
- FastAPI：高性能异步 Web 框架
- SQLite + SQLAlchemy：数据持久化
- DeepSeek R1：AI 模型服务
- Search1API：实时搜索服务
- Python 3.8+：开发语言

### 前端
- React 18：用户界面框架
- TypeScript：类型安全
- ChatUI：聊天界面组件
- Axios：HTTP 客户端

## 快速开始

### 后端设置

1. 创建并激活虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

2. 安装依赖：
```bash
cd backend
pip install -r requirements.txt
```

3. 配置环境变量：
创建 .env 文件并设置：
```
SILICONFLOW_API_KEY=your_api_key
SEARCH1API_KEY=your_api_key
```

4. 启动服务：
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 前端设置

1. 安装依赖：
```bash
cd frontend
npm install
```

2. 启动开发服务器：
```bash
npm start
```

## API 文档

启动后端服务后访问：http://localhost:8000/docs

### 主要接口

- POST /chat/
  - 发送消息并获取 AI 回复
  - 支持搜索结果和上下文理解

- GET /sessions/
  - 获取会话列表
  - 支持历史记录查看

- GET /sessions/{session_id}/messages/
  - 获取特定会话的消息记录
  - 包含完整的对话历史

## 开发说明

### 目录结构
```
personal-assistant/
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   ├── ai_service.py    # AI服务
│   │   │   └── search_service.py # 搜索服务
│   │   ├── models.py            # 数据模型
│   │   ├── database.py          # 数据库配置
│   │   ├── config.py            # 应用配置
│   │   └── main.py              # 主应用
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.tsx              # 主应用组件
    │   └── index.tsx            # 入口文件
    ├── package.json
    └── tsconfig.json
```

## 注意事项

- 需要有效的 DeepSeek API 和 Search1API 密钥
- 建议在生产环境中使用更安全的数据库（如 PostgreSQL）
- 前端的 API_BASE_URL 需要根据部署环境调整
- 建议添加适当的速率限制和缓存机制

## 后续计划

- [ ] 添加用户认证系统
- [ ] 支持更多 AI 模型选择
- [ ] 优化搜索结果展示
- [ ] 添加对话导出功能
- [ ] 实现更好的错误处理机制 