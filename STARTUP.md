# Agentic-ChemRAG 系统启动指南

本指南说明如何启动完整的Agentic-ChemRAG系统，包括后端FastAPI服务和前端React应用。

## 系统架构

- **后端**：FastAPI应用，运行在 http://localhost:8000
  - API端点：`POST /api/chat`
  - 静态文件：`/data` 目录
- **前端**：React应用，运行在 http://localhost:5173
  - 代理配置：通过Vite代理访问后端API

## 前提条件

### 1. Python环境（后端）
- Python 3.10+
- 安装所需包：
  ```bash
  pip install fastapi uvicorn pydantic langchain_core langchain_deepseek
  ```
  （具体依赖请参考后端代码中的import语句）

### 2. Node.js环境（前端）
- Node.js 16+ (推荐18+)
- npm 8+

## 启动步骤

### 第1步：启动后端服务

```bash
cd Agentic-ChemRAG
python backend/main.py
```

成功启动后，将看到消息：
```
🚀 Agentic-ChemRAG 后端服务已启动！API 地址: http://localhost:8000
```

### 第2步：启动前端应用

打开新的终端窗口：

```bash
cd Agentic-ChemRAG/frontend
npm install  # 如果尚未安装依赖
npm run dev
```

成功启动后，将看到消息：
```
➜  Local:   http://localhost:5173/
```

### 第3步：访问应用

在浏览器中打开：http://localhost:5173

## 功能测试

### 1. 测试后端API
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-123", "question": "卟啉是什么？"}'
```

### 2. 测试前端界面
1. 在浏览器中打开 http://localhost:5173
2. 在输入框中输入化学问题，如"二氧化钛纳米复合材料如何制备？"
3. 点击"发送"按钮
4. 查看回答、图片和参考资料

## 接口说明

### 请求格式
```json
POST /api/chat
{
  "session_id": "唯一会话ID",
  "question": "化学问题"
}
```

### 响应格式
```json
{
  "answer": "详细的回答内容",
  "images": [
    {
      "image_path": "data/extracted_images/xxx.jpeg",
      "image_desc": "图片描述"
    }
  ],
  "sources": [
    {
      "file_name": "文献文件名.pdf",
      "page": "页码"
    }
  ]
}
```

## 代理配置

前端开发服务器配置了代理：

| 前端路径 | 代理目标 | 用途 |
|---------|---------|------|
| `/api/*` | `http://localhost:8000/api/*` | API请求 |
| `/data/*` | `http://localhost:8000/data/*` | 静态资源（图片） |

## 故障排除

### 1. 后端启动失败
- 检查Python依赖是否安装
- 检查端口8000是否被占用
- 查看后端日志中的错误信息

### 2. 前端启动失败
- 检查Node.js版本：`node --version`
- 删除node_modules重新安装：
  ```bash
  cd frontend
  rm -rf node_modules package-lock.json
  npm install
  ```

### 3. 前后端连接失败
- 确保两个服务都在运行
- 检查后端CORS配置（已在代码中允许所有来源）
- 查看浏览器控制台错误信息

### 4. 图片无法加载
- 确保后端正确挂载了`/data`静态目录
- 检查图片文件是否存在于`data/extracted_images/`目录
- 查看网络面板中的图片请求状态

## 开发说明

### 修改后端API
- 编辑`backend/main.py`和`backend/rag_chain.py`
- 重启后端服务使更改生效

### 修改前端界面
- 编辑`frontend/src/App.tsx`和`frontend/src/App.css`
- 前端支持热重载，更改会自动刷新

### 添加新功能
1. 在后端添加新的API端点
2. 在前端添加对应的接口调用和UI组件
3. 更新类型定义（TypeScript接口）

## 目录结构

```
Agentic-ChemRAG/
├── backend/           # 后端Python代码
│   ├── main.py       # FastAPI主应用
│   ├── rag_chain.py  # RAG链定义
│   └── ...           # 其他后端模块
├── frontend/         # 前端React应用
│   ├── src/          # 源代码
│   ├── package.json  # 依赖配置
│   └── vite.config.ts # 构建配置
├── data/             # 数据目录
│   ├── pdf/          # PDF文献
│   └── extracted_images/ # 提取的图片
├── README.md         # 项目说明
└── STARTUP.md        # 本启动指南
```

## 注意事项

1. **会话管理**：后端使用内存存储会话历史，重启服务后会丢失
2. **图片路径**：确保图片路径使用正斜杠`/`，兼容Windows和Unix
3. **跨域访问**：开发阶段已配置CORS允许所有来源，生产环境应限制
4. **静态文件**：后端通过`/data`路径提供静态文件服务

## 下一步

- [ ] 添加用户身份验证
- [ ] 优化响应性能
- [ ] 添加文件上传功能
- [ ] 优化移动端体验
- [ ] 添加深色模式主题