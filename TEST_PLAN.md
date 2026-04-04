# 测试与评估计划

版本：v1.1
更新日期：2026-04-04

## 1. 目标

建立可复跑、可对比、可审计的测试机制，避免只凭主观体验判断改动优劣。

## 2. 测试分层

### A. 连通性回归（每日）

- 范围：健康检查、chat/stream 通路、SSE 事件完整性
- 命令：

```powershell
..\.venv\Scripts\python.exe tests\integration_test.py --wait
```

### B. 评测回归（迭代）

- 范围：召回、稳定性、时延、token
- 输入：固定中文问题集（目标 20-50 条）

## 3. 指标定义

### 3.1 召回率

- Recall@K：正确证据是否出现在 Top-K
- Citation Hit Rate：回答中的页码是否命中人工标注

### 3.2 稳定性

- 请求成功率
- SSE 完整结束率
- Schema 验证通过率
- 重试恢复率

### 3.3 速度

- Chat 总时延
- Stream 首包时延
- Stream 总时延
- 统计口径：p50 / p95 / p99

### 3.4 Token 成本

- Prompt Tokens
- Completion Tokens
- 单问答平均总 token

## 4. 执行方法

1. 固定问题集，保持问法和顺序一致。
2. 运行 integration_test.py 生成结果文件。
3. 记录结果路径和执行命令。
4. 对比前后两次结果文件，输出变化结论。

## 5. 数据与结果落盘

### 输入数据

- 语料：data/pdf
- 问题集：tests/integration_test.py 中 REGRESSION_QUESTIONS

### 输出数据

- 结果目录：tests/results
- 文件格式：integration_result_YYYYMMDD_HHMMSS.json

## 6. 验收阈值（当前阶段）

- 连通性：Health/Chat/Stream/Stress 全通过
- 时延：必须可输出 p50/p95/p99
- 结果：必须生成可追溯 JSON 文件

说明：召回质量阈值在问题集扩展到 20+ 且完成人工标注后启用。

## 7. 下一步完善项

- 扩展中文问题集到 20-50 条
- 引入人工标注页码，纳入 Citation 评估
- 增加后端分阶段耗时日志（改写/检索/生成）
- 增加 token 采集字段并入结果文件