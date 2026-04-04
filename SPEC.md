# Agentic-ChemRAG 规格说明

版本：v1.1
更新日期：2026-04-04

## 1. 目标

构建一个面向化学与材料文献问答的本地优先 MVP，重点解决：

- 专业语料召回不足
- 多轮上下文指代不清
- 结果引用与来源不稳定

## 2. 系统边界

### 输入

- 用户自然语言问题
- 可选历史会话
- 本地 PDF 文献库

### 输出

- 结构化答案
- 相关图片路径与描述
- 文献来源文件名与页码
- 流式事件序列

### 非目标

- 多租户权限体系
- 云端文献同步平台
- 生产级监控与账单系统

## 3. 运行时架构

1. 前端发起 /api/chat 或 /api/chat/stream 请求。
2. 后端加载 .env 配置并挂载 data 静态目录。
3. RAG 链路执行：问题改写 -> 检索 -> 重排 -> 结构化生成。
4. 前端渲染答案、图片与引用。

## 4. 接口契约

### POST /api/chat

Request:

```json
{
	"session_id": "string",
	"question": "string"
}
```

Response:

```json
{
	"answer": "string",
	"images": [
		{
			"image_path": "string",
			"image_desc": "string"
		}
	],
	"sources": [
		{
			"file_name": "string",
			"page": "string"
		}
	]
}
```

### POST /api/chat/stream

返回类型：text/event-stream

事件：

- start
- chunk
- end
- error

兼容性要求：

- 后端事件结构变更必须与前端解析同轮发布。
- chat 与 stream 的最终结构字段必须一致。

## 5. 配置与安全

- 所有配置来自 .env
- 敏感信息优先来自系统环境变量
- 禁止在业务逻辑硬编码模型、阈值、端口、路径
- .env 不入库，.env.example 必须保持可用

## 6. 数据治理

以下目录视为本地资产，不应入库：

- data/pdf
- data/extracted_images
- data/chroma_db

## 7. 非功能要求

- 可用性：基础链路可跑通，集成测试可复跑
- 可维护性：配置集中化，文档与代码同步
- 可观测性：关键链路具备可统计的时延数据

## 8. 验收标准

- 启动：README 和 STARTUP 文档可独立指导新同学完成启动
- 功能：/api/chat 和 /api/chat/stream 均可返回有效结果
- 稳定：集成测试通过并生成结果文件
- 质量：测试计划中的核心指标可量化输出