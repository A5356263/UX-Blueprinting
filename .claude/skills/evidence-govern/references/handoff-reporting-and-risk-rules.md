read_frequency: on_demand
execution_critical: true

# Handoff, Reporting and Risk Rules

## Handoff 与 Access

- `downstream_handoffs[]`：面向具体消费者的 Payload、用途、限制和审核门禁。
- `downstream_handoffs[]`：本次运行的实际交接决定。
- Handoff 必须引用 payload，不能复制证据正文。
- 下游不能删除 `forbidden_uses[]` 或审核依赖。

## 消费者矩阵

| 消费者 | 允许 | 禁止 |
|---|---|---|
| Root Cause | 治理问题、关系、反证、情境、readiness | 把 single source 写成确认根因 |
| Business Impact | 问题、影响范围成熟度、分母限制 | 反写证据或用 ROI 提高可信度 |
| Outcome | Evidence/Baseline 引用 | 缺 Root/Hypothesis/Intervention 时验证效果 |
| Data Visualization | 表达正式结构 | 新增关系、删 caveat、重算 |
| Evidence Archive | 获准持久化的 Patch/重要案例引用；Handoff 必须显式包含 `persist_in_archive` | 自动归档全部运行、把 Handoff ready 当作写入授权 |

Archive Handoff 只有同时满足以下条件时才可作为正式写入依据：

- `target_skill=evidence-archive`
- `handoff_status=ready|ready_with_caveats`
- `allowed_uses[]` 包含 `persist_in_archive`
- `payload_refs[]` 精确引用可持久化 Patch 或重要案例
- `required_review_ids[]` 均已有 approved Review Decision

Archive Handoff 只描述可申请归档的范围，不等于长期写入批准。Evidence Archive 仍需验证本地 Archive Request 与明确授权。
| Knowledge Wiki | 获准审阅的候选引用 | 直接发布、扩大范围、复制原始证据 |
| Objective/Subjective/Heuristic | 精确补证或重分析请求 | 模糊要求“全部重跑” |

## Root Cause Readiness

```text
multi_source_corroborated → ready
single_source             → exploratory_only
contested                 → conflict_first
insufficient              → blocked
```

`single_source` 必须具备可追溯来源和安全解释所需范围；否则是 `insufficient`。

## Knowledge Wiki 白名单

Evidence Govern 只放行 Subjective 的：

- `qa_candidate`
- `answer_pattern`
- `guidance_seed`

必须引用 `approve_for_knowledge_submission`。Handoff 只批准候选审阅，不批准正式入库。

Objective 指标与 Baseline、Heuristic 页面风险、Business Impact ROI、单次 Root Cause 和单次 Outcome 都不得直接成为 Wiki Handoff。

## 风险

- low：保留 caveat，不中断。
- medium：阻断强用途，允许探索性读取。
- high：阻断受影响的 Root、Wiki 或 Store 消费。
- critical：阻断相关正式下游并要求人工裁决。

只阻断受影响证据和消费者，不把局部风险升级为包级失败。

## 可读表达

不生成独立 Markdown。对话摘要只报告运行模式、证据数量、关系覆盖、主要限制、审核项和已允许下游，不得新增 JSON 中不存在的判断。
