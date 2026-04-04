# CLAUDE.md

## 工作规则

- 涉及架构或运行时行为变更时，先阅读 `SPEC.md`。
- 保持项目本地优先，不提交 `data/pdf/`、`data/chroma_db/`、`data/extracted_images/`。
- 运行时配置统一使用 `.env`，业务逻辑中禁止硬编码模型名、端口、阈值和本地路径。
- 默认做小步、精准修改，除非任务明确要求，否则不破坏现有 API 合约。
- `/api/chat` 与 `/api/chat/stream` 的请求与响应结构需与前端保持一致。
- 运行时合约有变化时，同步更新文档。

## 期望目录结构

- `backend/`：FastAPI 服务、检索、入库、PDF 解析、运行时配置。
- `frontend/`：Vite + React 前端、聊天 UI、SSE 解析、引用渲染。
- `SPEC.md`：目标架构与接口合约。
- `TEST_PLAN.md`：召回、稳定性、速度和 token 成本评测方案。

## 备注

- 仓库已使用本地 `.claude/` 忽略规则，因此共享说明文件放在仓库根目录。
- 若改动涉及流式输出，需同一轮同时更新后端事件发射与前端事件解析。

## 交付计划（可运行优先）

### 目标

- 先把项目恢复到可运行状态，再做增量优化。

### 分步流程

1. 通过 `.env` 固化运行时配置，确保前后端端口和路径一致。
2. 校验后端（`requirements.txt`）与前端（`package.json`）依赖兼容性。
3. 启动后端并先验证 `/docs` 健康状态，再测试聊天链路。
4. 启动前端并验证开发/构建流程。
5. 用与接口契约一致的 payload 执行 `/api/chat` 与 `/api/chat/stream` 集成检查。
6. 记录风险与未解决阻塞点，进入下一轮迭代。

### 标准启动顺序

1. `start_backend.bat`
2. `start_frontend.bat`
3. `python tests/integration_test.py --wait`

## 进度状态（2026-04-04）

### 已完成

- 基于 `.env.example` 生成并校验了 `.env`。
- 确认并补齐本地目录：`data/pdf`、`data/extracted_images`、`tests`。
- 新增启动脚本：`start_backend.bat`、`start_frontend.bat`、`start_all.bat`。
- 新增集成测试骨架：`tests/integration_test.py`。
- 修正测试请求体以匹配后端 schema（`session_id`、`question`）。
- 后端 `/docs` 健康检查通过（HTTP 200）。
- 前端生产构建通过（`npm run build`）。
- 通过检索器懒加载降低了后端启动阻塞概率。
- 使用当前代码验证了后端进程可启动（`python backend/main.py`）。
- 使用 `backend/build_vector_db.py` 完成了图片提取与向量库构建流程验证。
- 使用系统环境变量中的 API Key 验证了 LLM 可返回内容（无需在代码中显式传 `api_key`）。
- 执行 `python tests/integration_test.py --wait` 完成一轮端到端联调，结果通过（4/4）。
- 集成测试脚本已升级为中文回归集 + 时延基线输出，并生成结果文件：`tests/results/integration_result_20260404_171049.json`。
- 首轮基线结果：Chat p50/p95/p99 = 18279.83/26360.89/26360.89 ms；Stream 首包约 20591.03 ms。

### 进行中

- 根据业务数据持续优化召回质量（当前联调可跑通，但示例英文问题命中资料不足，回答多为“无相关资料，无法回答”）。

### 下一步

1. 按 `TEST_PLAN.md` 继续扩展 20-50 条中文问题回归集，并补充人工标注页码用于 Citation 命中评估。
2. 为 `/api/chat` 与 `/api/chat/stream` 增加分阶段耗时日志（改写/检索/生成）。
3. 在不改变接口契约的前提下，评估并优化检索召回参数（`RETRIEVAL_K`、`RETRIEVAL_SCORE_THRESHOLD`、`RERANK_TOP_N`）。