---
name: evidence-govern
description: >
  内部证据处理与治理技能。在单一流程中完成来源标准化、证据关联与情境评估、生命周期治理、
  人工审核和消费者专属放行。消费 Objective、Subjective、Experience Heuristic 的正式证据包，
  或吸收 Outcome Patch 与人工审核决定。不得绕过输入门禁，不做根因、效果重判、价值估算或知识写入。
---

# Evidence Govern 6.0.0

## Step 0：定位项目与合同

1. 读取 `shared-workflow/skill-graph.json`。
2. 读取 `shared-workflow/data-analysis/artifact-registry.json`。
3. 读取 `shared-workflow/data-analysis/references/context-handoff-protocol.md`。
4. 只解析本次请求显式提供的 Artifact、Archive Record、Baseline、Context、Outcome Patch 或 Review Decision 引用。跨技能 Artifact 必须同时给出完整 Artifact Instance Ref、正式 Handoff 引用和绝对 JSON Pointer `payload_refs[]`。
5. 不扫描 `spark-output`、Store、Knowledge Wiki 或用户目录寻找可能相关材料。

正式输出固定为：

```text
spark-output/results/governed/ 与 spark-output/context/current/governed.json
```

只有这一份 latest；不创建 Normalize、Triangulate、中间 latest、per-run 目录或默认历史副本。

## 角色

Evidence Govern 是一个内部技能，包含三个不可跳过的阶段：

```text
Phase 1  输入标准化与血缘
Phase 2  证据关联、变化与情境评估
Phase 3  生命周期、审核与消费者放行
```

它回答：

- 输入证据是否可追溯、是否重复、能否比较；
- 多条证据是否在描述同一现象，是否互相支持、限制或冲突；
- 故障、版本、运营、规则、口径和样本变化是否干扰解释；
- 每条证据可以被哪些下游以什么用途消费；
- 哪些处置需要人工审核或显式归档。

它不回答：

- 问题为什么发生；
- 哪个机制是最终根因；
- 某方案是否有效；
- 优化价值或 ROI 是多少；
- 应采用什么具体体验方案；
- 哪条内容应直接写入 Knowledge Wiki。

## 核心原则

1. 证据变化信号与生命周期处置分离。
2. 证据关联置信度不等于因果置信度或效果归因置信度。
3. 缺少情境资料不等于不存在混杂因素。
4. 单一来源可以进入探索性究因，但不能包装成多源互证。
5. 同源派生报告不能虚增证据强度。
6. 审核只局部阻断受影响证据和消费者，不默认中断整个运行。
7. Handoff 表示允许或建议交接，不表示目标技能已经执行。
8. Archive 保存证据历史；Knowledge Wiki 保存经过独立门禁的可复用知识表达。

用户摘要使用 `shared-workflow/data-analysis/presentation-vocabulary.json` 的中文标签、含义和下一步；Evidence ID、Review ID 与机器状态码只在结构化输出和引用明细中出现。

## 项目状态与读取路由

按运行模式选择输入，不额外补读无关 reference：

| 模式 | 必需输入 | 可选输入 |
|---|---|---|
| `evidence_governance` | 至少一个 Objective、Subjective 或 Heuristic 正式产物 | prior Govern、显式 Archive Record、Baseline、Context |
| `outcome_patch_absorption` | prior Govern + Outcome Patch | Review Decision、相关 Baseline |
| `review_decision_absorption` | prior Govern + Review Decision | 审核要求明确引用的补充材料 |

自动推断：

- 有分析证据引用：`evidence_governance`
- 有 Outcome Patch：`outcome_patch_absorption`
- 有 Review Decision：`review_decision_absorption`

只有多种模式同时满足且会改变执行范围时，才用业务语言询问用户要处理“新分析证据”“效果回检结果”还是“审核决定”。不要要求用户回答 Schema、字段映射或内部模式名。

## 输入与权限

输入 Schema：

```text
.agents/skills/evidence-govern/schemas/input.schema.json
```

支持：

```text
requested_mode
source_mode
upstream_artifact_refs[]
prior_govern_result_ref
archived_evidence_refs[]
baseline_refs[]
context_inputs[]
outcome_patch_refs[]
review_decisions[]
```

`context_inputs[]` 只接受：

- `structured_package`
- `raw_file`
- `upstream_ref`
- `user_statement`

原始服务日志只提取时间、活动类型、模块、聚合分群、区域和来源引用；不得复制客户原话、企业明细或设计链接。

## 输入门禁

- 只接受 Artifact Registry 当前版本，或存在真实适配器的显式 Legacy 版本。
- 未登记版本或没有真实适配器的旧产物不能进入正式消费。
- 缺少血缘、来源 ID 或必要隐私状态时，只局部限制对应证据。
- 缺少全部正式上游时输出 `blocked`，不生成正常治理结论。
- 缺少情境资料时继续执行，但将相关混杂判断标为 `unknown`。
- Outcome Patch 吸收不得重判效果、重算指标或重跑 Root Cause。
- Review Decision 只能处理 prior Govern 中存在且尚未关闭的 Review ID。

## Phase 1：输入标准化与血缘

执行前读取：

```text
references/normalization-and-lineage-rules.md
```

1. 读取上游正式 `evidence_items[]`，不得读取行级原始数据补做分析。
2. 保留上游 Evidence ID 和 JSON Pointer。
3. 生成稳定 `evidence_id`、`lineage_fingerprint` 和可选 `comparison_key`。
4. 将 Objective、Subjective、Heuristic 映射为共享 Canonical Evidence Item。
5. 判断完全重复、同源派生、跨时间可比较或信息不足。
6. 只输出标准证据，不把 Findings、Comparison、Knowledge Candidate、Validation Request 当成 Evidence Item。

Phase 1 不做跨源互证、因果解释、生命周期发布或知识候选判断。

## Phase 2：证据关联、变化与情境评估

执行前读取：

```text
references/evidence-link-context-and-change-rules.md
```

### 证据关系

只允许：

```text
corroborates
counterevidence
contradicts
qualifies_scope
non_independent
unresolved_match
```

检查用户/企业范围、任务或旅程、可观察现象、时间、产品版本或场景、指标或问题口径。输出 `evidence_link_confidence`，不得输出 Evidence 阶段的 `attribution_confidence`。

### 情境因素

只评估显式提供的：

```text
service_incident
product_change
operation_or_training
policy_or_process
measurement_or_data_change
population_or_scope_change
seasonality_or_external_event
other
```

只判断情境是否可能干扰证据解释，不判断其是否真正导致问题。需要重算时向对应上游发出精确请求。

### 变化信号

只允许：

```text
strengthened
weakened
stable
resolved
stale
contradicted
```

变化信号描述事实变化，不直接修改生命周期。

## Phase 3：生命周期、审核与放行

执行前读取：

```text
references/lifecycle-review-and-patch-rules.md
references/handoff-reporting-and-risk-rules.md
```

### 生命周期

Evidence：

```text
candidate
released
restricted
superseded
archived
```

Baseline：

```text
proposed
active
stale
superseded
archived
```

`needs_review` 属于审核状态，`blocked` 属于发布门禁；二者都不是生命周期。

### Root Cause 门禁

```text
multi_source_corroborated → ready
single_source             → exploratory_only
contested                 → conflict_first
insufficient              → blocked
```

单一来源只能支持候选机制。Root Cause 负责 `causal_confidence`，Evidence Govern 不生成因果解释。

### Knowledge Wiki

Evidence Govern 只可放行 Subjective 已生成的 `knowledge_candidates[]` 审阅请求。必须存在 `approve_for_knowledge_submission` 审核决定。Handoff 类型为：

```text
knowledge_candidate_review_request
```

放行只允许 Knowledge Wiki 读取和审阅，不表示已批准入库。Knowledge Wiki 仍执行候选、冲突、隐私、适用范围和用户确认门禁。

Root Cause 模式知识不经过本技能回流；完整路径为：

```text
Outcome reviewed cases
→ Govern 吸收回检变化
→ Root Cause pattern learning
→ 模式发布人工审查
→ Knowledge Wiki
```

## 确定性校验与原子写入

唯一脚本：

```text
.agents/skills/evidence-govern/scripts/evidence_govern_contract.py
```

执行：

```text
python3 .agents/skills/evidence-govern/scripts/evidence_govern_contract.py prepare <request.json>
python3 .agents/skills/evidence-govern/scripts/evidence_govern_contract.py validate <candidate.json>
python3 .agents/skills/evidence-govern/scripts/evidence_govern_contract.py write <candidate.json>
```

`prepare` 只处理确定性映射、ID 和血缘；语义关系、情境和治理判断由本 Skill 完成。`write` 只有在核心不变量和可选完整 Schema 校验全部通过后才原子替换 latest。

## 输出

正式输出必须符合：

```text
.agents/skills/evidence-govern/schemas/output.schema.json
```

顶层固定为：

```text
run
analysis_contract
data_quality
evidence_items[]
evidence_relationships[]
evidence_change_signals[]
context_factor_assessments[]
evidence_patches[]
baseline_patches[]
manual_review_queue[]
review_decisions[]
downstream_handoffs[]
limitations[]
handoff
```

不生成独立 Markdown。需要人工快速审阅时，在对话中以简短表格呈现审核项；结构化 JSON 始终是事实源。

## 标准 Handoff

- Root Cause：治理后的问题证据、readiness、用途和限制。
- Business Impact：问题证据、受影响范围成熟度和分母限制；不得把价值反写证据。
- Outcome：只有 Root、Hypothesis、Intervention 已登记时交付证据与 Baseline 引用。
- Data Visualization：只交付结构化结果引用，禁止新增关系。
- Evidence Archive：只交付允许持久化的 Patch 或重要案例引用；正式 Handoff 必须面向 `evidence-archive`、包含 `persist_in_archive`、精确 payload ref，并满足全部审核要求。Handoff ready 不自动执行写入。
- Knowledge Wiki：只交付已获准审阅的候选引用。
- Objective、Subjective、Heuristic：只交付精确重分析或补证请求。
- Experience Blueprint 不从本技能直接触发；应在 Root Cause 形成候选机制和干预方向后接入。

## 用户沟通

不要询问用户内部字段映射、Schema 或阶段名。缺少必要信息时说明：

```text
我已经完成能安全判断的部分。要继续判断这些证据是否描述同一个问题，还需要补充：
- 哪个时间范围；
- 哪类用户或企业；
- 是否在这段时间发生过版本、故障、运营或口径变化。
```

正常运行不因低风险审核项中断。只有模式冲突、正式效果判断、发布依赖强情境信息或用户必须裁决的高风险事项才询问。

## 自检

- 所有 Evidence ID、source refs 和 fingerprint 可解析。
- 同源派生未计为多源互证。
- 变化信号未直接修改生命周期。
- 未批准 Patch 未进入 Archive Handoff。
- 单一来源未生成 ready 根因门禁。
- Evidence 阶段未输出因果或效果归因置信度。
- Knowledge Wiki Handoff 只允许候选审阅。
- 所有消费者只能读取自己的 Handoff 和 Access。
- 输出通过契约工具校验并原子写入。

## 硬边界

- 不做 Root Cause、效果重判、方案设计、ROI 或正式知识写入。
- 不遍历 Store 或 Wiki 猜测历史。
- 不复制原始日志、工单正文、企业 ID 或用户 ID。
- 不自动应用 Evidence Store 或 Baseline Store Patch。
- 不创建第二份中间事实源。
- 不调用其他证据处理技能；标准化、关联、情境评估与放行都在本技能内完成。
