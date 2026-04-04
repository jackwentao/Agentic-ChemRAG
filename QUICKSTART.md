# Quick Start

本文档面向首次接手项目的同学，目标是 10 分钟内跑通本地环境。

## 1）最短路径（Windows）

在仓库根目录按顺序执行：

```powershell
Copy-Item .env.example .env
start_backend.bat
start_frontend.bat
..\.venv\Scripts\python.exe tests\integration_test.py --wait
```

成功标志：

- 后端 Docs 可访问：http://localhost:8000/docs
- 前端页面可访问：http://localhost:5173
- 集成测试显示 Passed: 4/4

## 2）首次初始化（脚本前）

如果是新机器或环境重建，请先执行：

```powershell
cd backend
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

```powershell
cd frontend
npm install
```

若语料更新，需重建向量库：

```powershell
cd backend
..\.venv\Scripts\python.exe build_vector_db.py
```

## 3）手动启动（无脚本场景）

后端：

```powershell
cd backend
..\.venv\Scripts\python.exe main.py
```

前端：

```powershell
cd frontend
npm run dev
```

## 4）关键检查项

- 已配置 .env
- 系统环境变量中已有模型 API Key
- data/pdf 下有可索引 PDF
- data/chroma_db 已完成构建

## 5）快速排障

### 端口占用

- 现象：后端或前端无法启动
- 处理：释放 8000/5173 端口后重试

### 模型无响应或超时

- 处理顺序：检查 API Key -> 检查网络 -> 缩小问题集验证

### 回答总是无相关资料

- 优先使用中文问题
- 重新构建向量库
- 确认语料内容与问题主题一致

## 6）文档入口

- 项目总览与契约：README.md
- 启动与联调流程：STARTUP.md
- 架构边界：SPEC.md
- 测试方法：TEST_PLAN.md
- 协作进度：CLAUDE.md
