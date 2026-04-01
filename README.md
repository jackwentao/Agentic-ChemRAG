# Agentic-ChemRAG 🔬

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![LangChain](https://img.shields.io/badge/LangChain-LCEL-green.svg)](https://python.langchain.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-BaaS-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-VectorStore-orange.svg)](https://www.trychroma.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Agentic-ChemRAG** 是一个专为材料科学与化学工程垂直领域打造的高级检索增强生成（Advanced RAG）全栈应用，支持多模态图文混排、多轮对话记忆与精准文献溯源。

---

## 📖 目录

- [背景 (Situation)](#-背景-situation)
- [目标 (Task)](#-目标-task)
- [实现 (Action)](#-实现-action)
- [成果 (Result)](#-成果-result)
- [快速启动 (Quick Start)](#-快速启动-quick-start)
- [未来规划 (Roadmap)](#-未来规划-roadmap)

---

## 🔍 背景 (Situation)

材料科学与化学工程领域的研究者在查阅专业文献时面临以下痛点：

- **通用大模型幻觉严重：** 面对高度专业的学术术语（如 XPS 峰位归属、MOF 拓扑结构），通用 LLM 极易产生"听起来正确"的错误答案，无法满足严格的科研需求。
- **多模态信息割裂：** 传统 RAG 系统仅能处理纯文本，丢失了论文中大量关键的实验谱图（SEM、XRD、UV-Vis 等），导致回答缺乏可视化依据。
- **缺乏精准溯源：** 现有工具只能给出段落级的参考，无法定位到具体文献的精确页码，严重影响研究者的验证效率。
- **多轮对话能力薄弱：** 在追问细节时（如"它的比表面积是多少"中的"它"），系统无法正确理解指代关系，导致对话上下文断裂。

---

## 🎯 目标 (Task)

针对上述问题，本项目设定了以下核心目标：

1. **多模态文献解析：** 精准解析双栏排版的学术 PDF，同步提取文本与 XPS、SEM 等实验谱图并与文本语义对齐。
2. **页码级精准溯源：** 回答中必须提供精确到页码的文献来源，供用户一键跳转验证。
3. **指代消解与多轮记忆：** 支持多轮追问中的指代消解（"它" → 具体专有名词），并隔离多用户并发会话。
4. **结构化前后端交互：** 后端强制约束大模型输出标准化 JSON（含文本解答、图片路径、参考文献），驱动前端卡片化渲染。

---

## ⚙️ 实现 (Action)

### 系统架构

本项目采用模块化前后端分离设计，分为四个核心层：

```
用户浏览器 (React 18)
      │  HTTP /api/chat
      ▼
FastAPI BaaS 微服务层
      │  Session 隔离 + 滑动窗口记忆
      ▼
双擎 LCEL 决策链
  ┌─────────────────────────────────┐
  │ 引擎 A: 指代消解 → 独立问题重写 │
  │ 引擎 B: 强约束结构化输出 (DTO)  │
  └─────────────────────────────────┘
      │
      ▼
双阶段检索核心
  ┌──────────────────────────────────────┐
  │ 粗排 (Bi-Encoder): BGE + Top-10 召回 │
  │ 精排 (Cross-Encoder): bge-reranker   │
  │                       → Top-3 精选  │
  └──────────────────────────────────────┘
      │
      ▼
ChromaDB 向量库
(由 PyMuPDF 多模态解析管道离线构建)
```

### 核心模块说明

| 模块 | 文件 | 职责 |
|------|------|------|
| 数据处理管道 | `backend/pdf_processor.py` | PyMuPDF 坐标感知解析、图像提取、O(N) 页码偏移映射 |
| 向量库构建 | `backend/build_vector_db.py` | BGE 向量化 + ChromaDB 内积空间持久化 |
| 双阶段检索 | `backend/retriever_engine.py` | Bi-Encoder 粗排 + Cross-Encoder 精排 |
| RAG 决策链 | `backend/rag_chain.py` | 指代消解链 + Pydantic 结构化输出链 |
| API 服务 | `backend/main.py` | FastAPI 异步接口、Session 管理、静态图片代理 |
| 前端交互 | `frontend/src/App.tsx` | React 聊天界面、图文卡片渲染、参考文献跳转 |

### 三大工程亮点

**1. 强约束结构化输出 (Structured Output)**

彻底摒弃不可控的 Markdown 纯文本拼接，利用 LangChain `with_structured_output` + Pydantic Schema 强制大模型返回标准化 DTO，实现业务逻辑与文本生成的彻底解耦。

**2. O(N) 级跨页页码追踪 (Offset Mapping)**

针对 RAG 切分丢失页码的业界痛点，自研全局偏移量映射算法，用单向递增双指针替代嵌套循环，在 O(N) 时间复杂度下完美绑定 Chunk 与物理 PDF 页码。

**3. 工业级多轮防爆机制 (Session & Context Control)**

基于轮数的滑动窗口切片（Sliding Window）彻底杜绝多轮对话导致的 Context Window 溢出，同时实现多用户 Session 完全隔离。

### 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | `FastAPI`, `Uvicorn`, `Pydantic` |
| AI 编排 | `LangChain` (LCEL), Function Calling |
| 文档解析 | `PyMuPDF` (`fitz`), 正则表达式 |
| 向量检索 | `ChromaDB`, `HuggingFaceEmbeddings` (BGE), `CrossEncoderReranker` |
| 大语言模型 | DeepSeek / GLM-4 兼容接口 (`langchain_deepseek`) |
| 前端 | `React 18`, `TypeScript`, `Vite`, `Axios` |

---

## 🏆 成果 (Result)

系统已成功实现对材料化学领域学术 PDF 的端到端智能问答，具备以下可量化成果：

- ✅ **多模态解析：** 支持双栏排版 PDF，可自动提取并关联实验谱图（SEM、XPS、UV-Vis 等）
- ✅ **精准溯源：** 每次回答附带精确页码，支持一键跳转至原始 PDF 对应位置
- ✅ **幻觉防控：** 双阶段检索 + 0.5 分数阈值硬拦截，有效过滤低相关性噪声
- ✅ **多轮对话：** 滑动窗口记忆（最近 3 轮）+ 指代消解，实现流畅的上下文追问

### 系统运行演示

**1. 极简主界面**

![主界面展示](./assets/demo.png)

**2. 多模态精准图文解析渲染**

![图文混排展示](./assets/demo-chat.png)
![图文混排展示](./assets/demo-image-render.png)

**3. 多轮记忆管理与精准溯源跳转**

![多轮记忆](./assets/demo-continue-chat.png)
![精准溯源](./assets/demo-jump1.png)
![精准溯源](./assets/demo-jump2.png)

---

## 🚀 快速启动 (Quick Start)

### 环境要求

- Python 3.10+
- Node.js 18+, npm 8+

### 步骤

**1. 后端：构建向量库并启动服务**

```bash
# 安装 Python 依赖
pip install fastapi uvicorn pydantic langchain-core langchain-deepseek \
            langchain-chroma langchain-huggingface langchain-community \
            langchain-classic pymupdf

# 将 PDF 文献放入 data/pdf/ 目录，然后构建向量库（仅需执行一次）
python backend/build_vector_db.py

# 启动后端服务（默认运行于 http://localhost:8000）
python backend/main.py
```

**2. 前端：启动交互界面**

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173 开始对话。

### API 接口

```
POST /api/chat
```

请求体：

```json
{
  "session_id": "唯一会话ID",
  "question": "化学问题"
}
```

响应体：

```json
{
  "answer": "详细的回答内容",
  "images": [{ "image_path": "data/extracted_images/xxx.png", "image_desc": "图片描述" }],
  "sources": [{ "file_name": "文献.pdf", "page": "12" }]
}
```

---

## 🗺️ 未来规划 (Roadmap)

- [ ] **多模态智能体 (Multimodal Agent)：** 对接 Qwen-VL 等视觉大模型，实现谱图自动解读与"以文找图"。
- [ ] **外部知识库融合 (Function Calling)：** 接入 PubChem / SciFinder 等外部 API，自动路由理化常数查询。
- [ ] **高并发推理加速：** 引入 vLLM PagedAttention + Redis Semantic Cache，提升 QPS 与响应速度。
