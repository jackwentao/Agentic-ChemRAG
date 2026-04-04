# 启动说明

本文件提供 Agentic-ChemRAG 的标准启动流程、最小验证步骤与排障清单。

## 一、前置条件

- Python 3.11+（建议使用仓库内 .venv）
- Node.js 18+
- 根目录已存在 .env（由 .env.example 复制而来）
- 文献已放入 data/pdf

## 二、标准启动顺序

1. 启动后端
2. 启动前端
3. 执行集成测试

推荐直接使用脚本：

```powershell
start_backend.bat
start_frontend.bat
..\.venv\Scripts\python.exe tests\integration_test.py --wait
```

## 三、首次初始化（仅首次或环境重建时）

### 1）准备配置

```powershell
Copy-Item .env.example .env
```

### 2）安装依赖

```powershell
cd backend
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

```powershell
cd frontend
npm install
```

### 3）构建向量库（含图片提取）

```powershell
cd backend
..\.venv\Scripts\python.exe build_vector_db.py
```

## 四、手动启动方式

### 后端

```powershell
cd backend
..\.venv\Scripts\python.exe main.py
```

检查地址：

- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### 前端

```powershell
cd frontend
npm run dev
```

检查地址：

- UI: http://localhost:5173

## 五、最小连通性验证

### 非流式接口

```powershell
curl -X POST http://localhost:8000/api/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"session_id\":\"local-test\",\"question\":\"卟啉是什么？\"}"
```

### 流式接口

```powershell
curl -N -X POST http://localhost:8000/api/chat/stream ^
  -H "Content-Type: application/json" ^
  -d "{\"session_id\":\"local-test\",\"question\":\"卟啉的作用是什么？\"}"
```

期望出现 start/chunk/end 三类事件。

## 六、常见问题与排障

### 1）端口占用

- 现象：8000/5173 无法绑定
- 处理：结束占用进程后重启服务

### 2）模型调用超时

- 先检查系统环境变量中的 API Key 是否可用
- 再检查网络可达性与模型服务状态

### 3）命中率偏低

- 确认问题语言与语料语言一致（建议中文）
- 重新执行 build_vector_db.py，确保向量库为最新

### 4）图片不显示

- 确认后端已挂载 /data
- 确认 data/extracted_images 下存在对应图片

## 七、数据治理

以下目录为本地资产，不应提交：

- data/pdf
- data/chroma_db
- data/extracted_images

如需共享结果，请共享脚本、配置和指标，不直接共享全量原始数据。