# 前端开发文档

前端工程基于 React + TypeScript + Vite，负责聊天交互、流式渲染、图片与引用展示。

## 1. 启动方式

```powershell
cd frontend
npm install
npm run dev
```

默认地址：http://localhost:5173

## 2. 与后端的接口契约

### 请求入口

- 非流式：POST /api/chat
- 流式：POST /api/chat/stream

### 流式事件

- start：流开始
- chunk：文本增量
- end：最终结果（包含 answer/images/sources）
- error：异常事件

说明：前端 SSE 解析逻辑与后端事件结构必须同轮变更。

## 3. 环境变量

前端通过根目录 .env 获取联调配置：

- FRONTEND_PORT
- BACKEND_ORIGIN
- VITE_API_BASE_URL
- VITE_DATA_BASE_URL

其中代理与端口由 vite.config.ts 统一读取。

## 4. 常用命令

```powershell
npm run dev
npm run build
npm run preview
```

## 5. 关键文件说明

- src/App.tsx：消息状态、SSE 解析、内容渲染
- src/App.css：布局、消息样式、流式光标动画
- vite.config.ts：端口与代理配置

## 6. 质量门禁

- 变更前后需保证 npm run build 通过
- 与后端联调至少跑一轮集成测试
- 文档更新需反映接口或配置变化

## 7. 常见问题

### 页面可打开但无回答

- 检查后端服务是否可访问
- 检查 /api/chat/stream 是否返回 start/chunk/end

### 图片链接打不开

- 检查 VITE_DATA_BASE_URL
- 检查后端 /data 静态目录挂载和路径分隔符

### 构建时报 node 类型错误

- 确认已安装 @types/node
