# Agentic-ChemRAG

Agentic-ChemRAG 是一个面向化学与材料文献问答的垂直 RAG 项目。
系统采用前后端分离架构，提供多轮问答、流式响应、引用来源与图片展示能力。

## 核心能力

- 基于本地 PDF 语料构建向量数据库
- 支持普通问答与流式问答两种接口
- 返回结构化结果：answer、images、sources
- 面向工程化交付：统一配置、测试脚本、启动脚本、文档规范

## 技术栈

- Backend: FastAPI, LangChain, ChromaDB, HuggingFace
- Frontend: React 18, TypeScript, Vite
- Runtime: Python 3.11+, Node.js 18+

## 仓库结构

```text
Agentic-ChemRAG/
├─ backend/                # 后端服务、检索链路、向量构建
├─ frontend/               # 前端应用
├─ data/                   # 本地数据（不入库）
│  ├─ pdf/
│  ├─ extracted_images/
│  └─ chroma_db/
├─ tests/                  # 集成测试与评测结果
├─ .env.example            # 配置模板
├─ SPEC.md                 # 架构与接口契约
├─ CLAUDE.md               # 协作流程与进度
└─ TEST_PLAN.md            # 评测方案
```

## 关联文档

- [SPEC.md](SPEC.md)：系统边界、运行时架构、配置约定
- [CLAUDE.md](CLAUDE.md)：交付流程、当前进度、下一步计划
- [TEST_PLAN.md](TEST_PLAN.md)：Recall/稳定性/速度/token 评测方法
- [STARTUP.md](STARTUP.md)：启动与排错说明

## 快速开始

### 1. 准备配置

将 .env.example 复制为 .env，并按本地环境填写。

Windows:

```powershell
Copy-Item .env.example .env
```

### 2. 安装依赖

Backend:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Frontend:

```powershell
cd frontend
npm install
```

### 3. 构建本地向量库

```powershell
cd backend
..\.venv\Scripts\python.exe build_vector_db.py
```

### 4. 启动服务

方式 A（推荐）：

```powershell
start_backend.bat
start_frontend.bat
```

方式 B（手动）：

```powershell
cd backend
..\.venv\Scripts\python.exe main.py
```

```powershell
cd frontend
npm run dev
```

默认地址：

- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

### 5. 运行集成测试

```powershell
..\.venv\Scripts\python.exe tests\integration_test.py --wait
```

测试会输出：

- 健康检查
- Chat/Stream 通路验证
- 中文回归问题集
- 时延基线与 JSON 结果文件

## API 契约

### POST /api/chat

Request:

```json
{
  "session_id": "user-session-id",
  "question": "你的问题"
}
```

Response:

```json
{
  "answer": "...",
  "images": [],
  "sources": []
}
```

### POST /api/chat/stream

Content-Type: text/event-stream

事件格式：

- {"type":"start"}
- {"type":"chunk","content":"..."}
- {"type":"end","answer":"...","images":[...],"sources":[...]}
- {"type":"error","error":"..."}

## 配置规范

- 所有运行时配置统一来自 .env
- 禁止在业务代码中硬编码模型名、路径、端口和阈值
- 推荐通过系统环境变量注入敏感信息（如 API Key）

## 安全与数据治理

- 不提交本地数据目录：data/pdf, data/extracted_images, data/chroma_db
- 不提交敏感配置：.env, *.pem, 私钥、token
- 分享演示数据时请脱敏并注明数据来源与许可

## 贡献规范

- 优先小步提交，避免一次性大改
- 改动接口时必须同步更新前端解析与测试
- 改动运行时契约时同步更新 SPEC 与 README
- 提交前至少执行一轮集成测试

## 常见问题

- 启动失败且端口占用：清理 8000/5173 端口后重启
- 流式请求超时：优先检查模型可用性和网络
- 命中率偏低：优先使用中文问题并检查向量库是否为最新构建