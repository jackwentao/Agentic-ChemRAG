# Profile Refactor 离线真实数据评测报告

## 评测配置

- 案例数量：12
- 真实 PDF 数量：11
- chunk 数量：419
- figure 证据数量：496
- profile 字段证据数量：66
- 数据库依赖：False
- LLM 依赖：False
- 索引构建耗时：32240.059 ms

## 核心指标

| 指标 | 数值 |
| --- | ---: |
| answer_llm_calls | 0.000 |
| answer_revision_applied | 0.000 |
| answer_revision_llm_calls | 0.000 |
| answer_revision_required | 0.000 |
| 答案术语覆盖率 | 0.625 |
| answer_verification_llm_calls | 0.000 |
| answer_verification_passed | 1.000 |
| answer_verification_triggered | 0.250 |
| aspect_coverage_rate | 0.486 |
| assessment_llm_calls | 0.000 |
| assessment_round_count | 0.000 |
| citation_page_hit | 0.917 |
| document_mrr@k | 0.619 |
| document_ndcg@k | 0.694 |
| document_precision@k | 0.625 |
| 文档召回@k | 0.875 |
| figure_hit | 0.833 |
| figure_mrr@k | 0.067 |
| figure_precision@k | 0.067 |
| 图片召回@k | 0.333 |
| first_round_success | 0.500 |
| image_selection_llm_calls | 0.000 |
| 限制披露命中率 | 1.000 |
| max_rounds_exhausted | 0.000 |
| missing_disclosure_count | 0.000 |
| no_new_evidence_stop | 0.000 |
| no_new_query_stop | 0.000 |
| observed_retry_success | 0.500 |
| page_mrr@k | 0.500 |
| page_ndcg@k | 0.586 |
| page_precision@k | 0.560 |
| 页码召回@k | 0.800 |
| 拒答正确率 | 1.000 |
| 检索行为命中率 | 0.750 |
| retrieval_round_count | 1.500 |
| retry_triggered | 0.500 |
| 路由命中率 | 1.000 |
| 来源链接有效率 | 1.000 |
| 目标命中率 | 0.917 |
| total_tracked_llm_calls | 0.000 |
| unsupported_claim_count | 0.000 |
| unsupported_claim_risk | 0.000 |
| wasted_retry | 0.000 |

## Profile 细粒度指标

| 指标 | 数值 |
| --- | ---: |
| chunk 证据数 | 2.083 |
| 文档级证据数 | 2.667 |
| figure 证据数 | 0.417 |
| 后续检索约束文档数 | 0.583 |
| 后续检索文档范围正确率 | 0.917 |
| 后续检索页命中率 | 0.917 |
| 画像后续检索触发率 | 0.500 |
| 页级证据数 | 2.500 |
| 画像文档命中率 | 0.833 |
| 画像证据数 | 2.667 |
| 画像字段数 | 1.917 |
| 画像单独支撑细节风险率 | 0.000 |

## 证据类型分布

| 类型 | 数量 |
| --- | ---: |
| document_profile | 32 |
| chunk | 25 |
| figure | 5 |

## Profile 字段分布

| 字段 | 数量 |
| --- | ---: |
| overview | 14 |
| abstract | 2 |
| conclusion | 4 |
| figures | 4 |
| entities | 7 |
| topics | 1 |

## 未命中案例

- `profile-cross-polymer-specific-001`：route=document_profile，followup=none，expected=document

## Profile-only 细节风险案例

无。
