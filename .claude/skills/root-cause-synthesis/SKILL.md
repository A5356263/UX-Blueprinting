---
name: root-cause-synthesis
description: 候选根因综合技能。仅在 Evidence Govern 已形成面向本技能的消费者专属 Handoff 时使用；将已治理证据综合为可反驳的候选根因、机制链、因果置信度、治理方向和验证假设，也可在 Govern 吸收 reviewed Outcome 后刷新候选生命周期，或基于至少两个可比 reviewed cases 形成跨案例模式候选。不得直接读取原始数据或绕过 Evidence Govern，不得输出已验证根因、具体方案、效果判断、ROI 或自动状态变更。
---

# 候选根因综合

把 Evidence Govern 已治理的证据组织成可追溯、可反驳、可人工复核的候选机制。不要重新分析原始材料，不要设计具体方案，也不要把候选写成已验证根因。

## Step 0 · 运行入口

### 0.1 检查正式输入

启动时读取：

1. `shared-workflow/skill-graph.json`
2. `shared-workflow/data-analysis/artifact-registry.json`
3. `shared-workflow/data-analysis/references/context-handoff-protocol.md`
4. 用户本轮明确指定的输入或正式 Handoff

只接受 `.claude/skills/root-cause-synthesis/schemas/input.schema.json` 定义的输入。正式输入必须包含 Evidence Govern 面向 `root-cause-synthesis` 的消费者专属 Handoff。

不得扫描 `spark-output/context/`、Archive Store 或历史目录寻找“最新”输入。

### 0.2 已有产物状态

正式 latest：

```text
spark-output/results/root-cause/ 与 spark-output/context/current/root-cause.json
```

已有产物只表示曾经运行，不得自动沿用正文、改变本轮模式或跳过输入门禁。

### 0.3 独立调用沟通

有有效 Govern Handoff 时直接执行。只有原始数据或分析报告时，用业务语言说明：

> 我可以综合候选根因，但这些结论需要先确认是否在同一时间、范围和口径下能够一起使用。请先完成证据治理，避免把相似现象误当成同一个原因。

不要询问用户 `payload_refs`、Schema、字段映射或内部状态名。一次只确认一个会改变范围、规则解释或运行模式的问题。

## 角色与边界

负责：

- 候选根因与候选机制链；
- 反证和替代解释；
- `causal_confidence`；
- 非具体方案的治理方向；
- 轻量、可证伪的 `validation_hypotheses[]`；
- Govern 吸收 Outcome 后的候选生命周期 Patch；
- 至少两个 reviewed cases 的跨案例模式候选。

不负责：

- 原始客观、主观或启发式分析；
- Evidence 规范化、互证、情境治理和放行；
- 具体 UI、文案、服务脚本或发布方案；
- 验证设计、效果判断和回归监测；
- 业务影响、收益、投入、ROI 或优先级；
- 自动修改 Evidence、Root Cause、知识库或策略资产。

## 总原则

1. 所有根因保持 candidate。
2. 每个正常候选必须有反证检查和至少一个替代解释。
3. 三种置信度不得混用：这里只使用 `causal_confidence`。
4. 只消费 Govern Handoff 允许的引用和用途。
5. 变化信号、生命周期状态和 Patch 动作必须分开。
6. JSON 是唯一结构化事实源；报告不能增加新结论。

用户报告使用 `shared-workflow/data-analysis/presentation-vocabulary.json` 的中文状态；候选 ID、Handoff ID 和状态码只保留在 JSON 与追溯明细。
7. 人工审核只局部阻断受影响候选、用途或交接。

## 运行模式

一次运行只使用一种模式：

| 模式 | 触发条件 | 核心输出 |
| --- | --- | --- |
| `candidate_synthesis` | Govern 放行候选根因综合 | 候选、机制链、方向、验证假设 |
| `outcome_feedback_refresh` | reviewed Outcome 已被 Govern 吸收并精确回流 | 根因生命周期 Patch |
| `pattern_candidate_learning` | 至少两个可比、已审查且已被 Govern 吸收的 Outcome Case | 相似性与模式候选 |

假设登记并入 `candidate_synthesis`；验证计划和回归监测归 Outcome；不得多模式组合执行。

## 输入门禁

目标 Handoff 必须满足：

```text
source_skill = evidence-govern
govern_artifact_instance_ref = 完整且摘要匹配的 Govern 已发布实例
target_skill = root-cause-synthesis
handoff_status = ready | ready_with_caveats
allowed_uses contains causal_synthesis
payload_refs[] are absolute JSON Pointers and all resolve
```

`required_review_request_ids[]` 非空时，只接受与同一 Artifact Instance Ref、`handoff_id` 和全部 `payload_refs[]` 绑定的已批准 `review_decisions[]`；否则 fail closed。

按模式读取：

- Candidate：Canonical Evidence、Evidence Relationship、Context Assessment、Business Rule Basis、Evidence Basis 和 Root Cause Readiness。
- Feedback：Govern 吸收后的 reviewed Outcome Case 引用。
- Pattern：至少两个 Govern 放行的 reviewed Outcome Case 引用。

不得直接读取 Objective、Subjective、Heuristic 或未经 Govern 的 Outcome 包。信息不足时请求 Govern 补证，不得绕过治理。

门禁状态：

- `blocked`：不生成正常候选；
- `needs_user_input`：只请求会改变判断的关键确认；
- `partial`：列出已完成和被阻断范围；
- `ready_with_caveats`：继承所有 caveat；
- `ready`：允许完整运行，但不表示根因已验证。

## Reference 路由

- `candidate_synthesis` 必读 `references/candidate-synthesis-rules.md`
- 候选可进入方案探索或验证准备时读 `references/intervention-and-validation-hypothesis-rules.md`
- Feedback 或 Pattern 模式读 `references/lifecycle-and-pattern-rules.md`
- 每次输出和交接前读 `references/handoff-reporting-and-risk-rules.md`

真实业务规则正文仍来自 Knowledge Wiki、正式上游或用户输入。本技能默认不扫描 Wiki，只沿精确 `business_rule_basis_ref` 最小读取。

## 执行步骤

### Step 1 · 校验输入合同

运行：

```bash
python3 .claude/skills/root-cause-synthesis/scripts/validate_and_write.py validate \
  --input <input.json> \
  --candidate <candidate-output.json>
```

生成候选前先检查 Handoff、Evidence Basis、Readiness、允许/禁止用途和审核依赖。输入 blocked 时只形成阻断说明和精确补证需求。

### Step 2 · 分离症状、事实、机制和候选

按固定顺序推理：

```text
observed_symptom
→ evidence_fact
→ mechanism_hypothesis
→ candidate_root_cause
```

不要把指标下降、报错、求助增加、启发式风险或用户“不理解”直接写成根因。

### Step 3 · 内聚候选卡片

每个候选在同一对象内记录：

- 范围和症状；
- 证据事实与推理链；
- 反证；
- 替代解释；
- 因果置信度及上限原因；
- 业务规则引用；
- 审核状态、补证需求和 caveat。

单一来源、未解决冲突、强反证、强混杂、更强替代解释或禁止 causal claim 时，置信度最高为 `low`。`high` 仍是高置信候选，不是确认根因。

### Step 4 · 生成候选机制链

为每个非 rejected、非 insufficient 候选生成 `candidate_mechanism_chains[]`。链必须显式包含反证、替代解释和验证假设节点，并只表达 candidate 关系。

### Step 5 · 生成治理方向与验证假设

治理方向只表达需要改善或验证的能力，不给具体方案。低置信候选只能进入
`validation_only`。经审核且达到 `design_ready_after_review` 的方向必须通过
`Root Cause → Problem Framing` 精确 Handoff 进入方案设计；不得直接跳到
Business Impact 的方案价值模式。

`validation_hypotheses[]` 只记录机制、指标方向、baseline/观察要求、guardrail、分群和可证伪条件。不得设计实验执行、输出提升百分比或估值。

### Step 6 · 条件反馈与模式学习

Feedback 模式只在 Govern 已吸收 Outcome 后提出 `root_cause_lifecycle_patches[]`；Patch 必须人工批准且不能自动应用。

Pattern 模式至少使用两个可比 reviewed cases，记录共同机制、适用/不适用情境、反例、失败条件和 publication review。不得自动发布。

### Step 7 · 生成交接

只允许以下 Skill 目标：

```text
evidence-govern
problem-framing
business-impact
outcome-validation-recheck
data-visualization
knowledge-wiki
evidence-archive
```

人工审核写入 `manual_review_requests[]`，不得伪装成 Skill。Outcome Handoff 必须同时提示需要正式 Intervention Contract。Knowledge Wiki 只接收跨案例模式候选；Archive 需要 `persist_in_archive` 和显式审核。

### Step 8 · 校验并写入

先生成临时候选 JSON，再运行合同工具。只有 Input Schema、Output Schema 和核心语义门禁全部通过，才执行：

```bash
python3 .claude/skills/root-cause-synthesis/scripts/validate_and_write.py write \
  --input <input.json> \
  --candidate <candidate-output.json>
```

正式发布写入不可变结果，并只按 `analysis_purpose.purpose_key` 更新 Current Pointer；失败不覆盖已有正式结果。

## 输出

正式 JSON 顶层：

```text
run
analysis_contract
data_quality
limitations
handoff
analysis_summary
analysis_results
manual_review_requests
downstream_handoffs
quality
write_safety
```

只接受 Registry 登记的 `5.0.0` 契约；其他版本没有真实适配器时必须重跑。

是否生成 Markdown 由 `requested_deliverables` 决定，与独立或链式调用无关。需要可视化时交给 Data Visualization，不在本技能重算或生成 HTML。

## 标准交接

完成后读取 `shared-workflow/next-skill.md`，只按本次 Handoff、用途许可和门禁给出下一步。

写入成功后运行：

```bash
node shared-workflow/generate-progress-preview.js
```

刷新失败只告警，不改变分析结果。

## 内部自检

完成前确认：

- 输入只来自 Root Cause 专属 Govern Handoff；
- 候选、反证、替代解释和置信度内聚且可追溯；
- 没有 validated/final root cause；
- 没有具体方案、效果判断、回归监测或 ROI；
- Feedback 先经过 Govern；
- Pattern 至少两个 reviewed cases；
- 人工审核和 Handoff 引用可解析；
- JSON 与 Markdown 无原始正文、明细 ID 或敏感信息；
- Schema、语义门禁和原子写入成功。

能修复的问题直接修复；不能修复时降级、局部阻断或提出精确补证，不生成冗长自检报告。
