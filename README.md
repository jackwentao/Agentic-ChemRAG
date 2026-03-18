\# Agentic-ChemRAG 🔬



\*\*Agentic-ChemRAG\*\* 是一个专为材料科学与化学工程垂直领域打造的智能体检索增强生成（Agentic RAG）系统。



该项目旨在解决通用大模型在面对极端细分领域（如特定无机基底改性、化学键合工艺）时产生的严重“幻觉”问题，为科研人员提供高准确率的文献溯源与精确的理化常数对比。



\## ✨ 核心特性



\* \*\*混合智能检索 (Hybrid Agentic Search):\*\* \* \*\*非结构化数据萃取：\*\* 基于本地 ChromaDB 向量库，精准检索 ZnO/CMP 物理混合与 ZnO-CMP 酰胺键连接的机理与表征数据（XPS, TGA, EIS 等）。

&#x20; \* \*\*结构化数据查询：\*\* 引入 Function Calling 机制，外接大语言模型的“触手”，自动调用 NCBI PubChem API 获取高精度化学试剂理化常数。

\* \*\*工业级解析链路:\*\* 采用 PyMuPDF 针对双栏复杂排版的化学学术论文进行精准的文本与反应式提取。

\* \*\*极速流式响应 (TTFT 优化):\*\* 后端基于 FastAPI 与异步生成器构建，实现低延迟的 SSE 流式输出，提供类似 ChatGPT 的打字机交互体验。



\## 🛠️ 技术栈

\* \*\*算法与大模型层:\*\* Python, LangChain, DeepSeek API

\* \*\*数据与存储层:\*\* ChromaDB, PyMuPDF, BGE-Embedding

\* \*\*后端服务与工具:\*\* FastAPI, Pydantic, Requests (PubChem API Integration)

\* \*\*前端交互:\*\* 待 Claude Code 自动生成 (React/Vue3)

