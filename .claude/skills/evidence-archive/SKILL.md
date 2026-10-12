---
name: evidence-archive
description: 显式、获批地长期保存已治理证据、重要情境、Root Cause 候选、Outcome 结论、脱敏 Business Impact 决策快照和已批准 Baseline。用于用户明确说“归档/长期保留/保存历史证据”，或正式 Handoff 已批准 `persist_in_archive` 时；生成不可变最小快照并写入两个惰性 JSONL Store。不得自动扫描、分析、互证、审批生命周期、发布知识或归档每次运行。
---

# Evidence Archive

## Step 0 · 启动条件与产物状态

先读取：

1. `shared-workflow/skill-graph.json`
2. `shared-workflow/data-analysis/artifact-registry.json`
3. `shared-workflow/data-analysis/references/context-handoff-protocol.md`
4. `schemas/archive_request.schema.json`
5. `schemas/archive_record.schema.json`
6. `schemas/archive_summary.schema.json`
7. 归档 Baseline 时再读取 `shared-workflow/data-analysis/schemas/baseline_item.schema.json`

只接受：

- 用户明确指定需要长期保存的产物或记录；
- 面向 `evidence-archive`、状态为 `ready|ready_with_caveats`、包含 `persist_in_archive` 且审核已完成的正式 Handoff。

没有唯一目标时返回 `needs_user_input`。禁止扫描 `spark-output`、Store 或历史聊天猜测目标。日常下游仍读取按分析目的维护的 Current Pointer；Archive Store 不是当前上下文。

## 角色

本技能是显式持久化边界：

- 验证目标、来源版本、用户/Handoff 授权、治理 Patch、人工审核和敏感等级；
- 从已登记来源形成类型化不可变最小快照；
- 将普通归档记录写入统一历史归档账本；
- 将已批准 Shared Baseline Item 写入 Baseline Store；
- 返回可精确读取的 Record Ref 和轻量归档回执。

不负责：

- 分析、标准化、跨源匹配、因果判断、效果判断或业务估值；
- 修改 Evidence ID、业务口径、计算结果或来源血缘；
- 审批 Evidence/Baseline 生命周期；
- 自动写 Knowledge Wiki；
- 自动归档全部运行、建立索引、分类 Store、Profile 或运行历史。

## 核心原则

1. **显式授权**：普通 ready Handoff 不等于长期写入授权。
2. **不可变快照**：不得只保存 Current Pointer 或可变化路径。
3. **来源钉住**：写前复核 Artifact 版本、run ID、稳定 Item ID 和内容摘要。
4. **最小披露**：只保存来源白名单和本次授权共同允许的字段。
5. **身份分离**：Evidence 身份、来源指纹、Payload 指纹和 Archive Event ID 各自承担单一职责。
6. **语义 append-only**：旧记录不修改；纠正或状态变化追加 superseding 记录。
7. **精确读取**：只按 Archive Record ID 或 Baseline ID/version 读取，不提供 list、latest、模糊搜索。
8. **生命周期分离**：执行归档不等于把生命周期改为 `archived`。

用户回执使用 `shared-workflow/data-analysis/presentation-vocabulary.json` 的中文状态；Record ID、run ID 和状态码保留在结构化回执或明细区，不占据主结论。

## 调用模式

### explicit_user_request

用户本轮明确指定目标和长期保存范围。目标清楚且不涉及 confidential 新确认时，说明归档内容后直接执行，不重复询问。

Business Impact 决策快照还必须包含：

```text
approve_archive_decision_snapshot
```

### approved_handoff

正式 Handoff 必须同时满足：

```text
target_skill = evidence-archive
source_artifact_instance_ref = 完整且摘要匹配的已发布实例
handoff_status = ready | ready_with_caveats
allowed_uses[] contains persist_in_archive
payload_refs[] are absolute JSON Pointers and precisely identify this target
required_review_request_ids[] are all approved
```

Evidence/Baseline Patch 还必须满足 `can_persist=true`，且 `decision_status=not_required|approved`。

外部 `review_decisions[]` 还必须绑定同一 Artifact、run、Handoff 和全部 payload，并明确批准 `persist_in_archive`；只给 Review ID 不构成授权。

## 输入与归档资格

| record_kind | 唯一允许来源 | 最大快照 | 永久禁止 |
| --- | --- | --- | --- |
| `evidence` | Evidence Govern Canonical Evidence Item + 获准 Patch | 完整 Canonical Evidence Item | 因归档升级为根因或效果事实 |
| `context_factor` | Govern `context_factor_assessments[]` | 情境类型、范围、重叠、方向、处置、置信度、理由和来源 | 原始服务日志、工单或变更正文 |
| `root_cause` | `analysis_results.root_cause_candidates[]` | 当前候选、结构化证据链、causal confidence、反证、替代解释与限制 | 改写成确认根因或 Wiki 模式 |
| `outcome` | `analysis_results.validation_assessment` | 验证对象、阶段、聚合结果、判断、attribution、guardrail、限制和 Patch 引用 | 明细 ID 或跨案例规律 |
| `business_decision_snapshot` | Business Impact | 用户明确批准的 run、portfolio summary、limitations 最小决策快照 | Evidence/Baseline/Wiki 用途、客户/企业明细、成本收入明细和中间参数 |
| `baseline` | Objective Shared Baseline Item Candidate + Govern Patch | 完整 Shared Baseline Item | Archive 补字段、裁剪或重算 |

Objective、Subjective、Heuristic 的普通 Findings/Comparison/Coverage/Validation Requests/knowledge candidate 不得直接归档。Subjective/Heuristic 只有进入 Evidence Govern 后形成的 Canonical Evidence 才能归档。

## 敏感数据边界

- `internal`：在明确授权范围内保存；
- `confidential`：上游必须先形成 `upstream_redacted` 或 `archive_safe_projection`；
- `restricted`：当前明文 JSONL Store 禁止保存，返回 `blocked`；
- Archive 只验证脱敏状态，不自行修改、模糊或猜测敏感字段；
- Store 已存在但权限宽于 `0600` 时阻止写入，不静默修复。

Evidence 的 `lifecycle_status=restricted` 与 Payload 的 `sensitivity=restricted` 不是同一概念。前者可在归档快照本身安全时保存，后者当前禁止内联持久化。

## 用户沟通

不要让用户填写 Schema、字段映射或技术门禁。

目标不明确时：

```text
你希望长期保留哪一项结果？可以告诉我结果名称或记录编号。
```

confidential 快照需要确认时：

```text
这次会长期保存以下聚合字段，并排除这些敏感明细。确认后我会保存这份固定快照。
```

门禁不足时：

```text
这项结果还缺少长期保存批准。我会保留当前分析不变，等审核通过后再归档。
```

## 执行状态机

```text
target_resolved
→ authorized
→ prepared
→ validated
→ committed
→ verified
→ summarized
```

任一阶段失败时停止后续动作。Store 已成功、Summary 失败时不得回滚 Store；返回实际 Record Ref，并通过同一请求幂等重建 Summary。

### 1. 形成并钉住请求

请求必须遵守 `schemas/archive_request.schema.json`，记录：

- 明确目标和最大字段范围；
- Artifact ID/version、run ID、稳定 Item ID；
- 来源内容摘要；
- 授权模式和授权引用；
- Handoff、Patch、Review Decision；
- 敏感等级、脱敏状态和允许/禁止用途。

准备请求：

```bash
python3 .claude/skills/evidence-archive/scripts/archive_evidence.py prepare \
  --request <draft-request.json>
```

请求和计划通过标准输入或系统临时文件传递，不写入工作区。

### 2. 校验

```bash
python3 .claude/skills/evidence-archive/scripts/archive_evidence.py validate \
  --request <prepared-request.json>
```

脚本必须从 Artifact Registry 解析路径、版本、Schema 和策略。Registry 未登记、来源已变化、授权扩大、Patch 不可持久化、审核未批准或敏感等级不允许时 fail closed。

### 3. 原子提交

```bash
python3 .claude/skills/evidence-archive/scripts/archive_evidence.py archive \
  --request <prepared-request.json>
```

只持久化：

```text
spark-output/results/archive-summary/ 与 spark-output/context/current/archive-summary.json
spark-output/context/stores/archived-evidence-store.jsonl
spark-output/context/stores/baseline-store.jsonl
```

Store 首次获批写入时才创建。同一 Store 的同批记录在锁内校验，写入同目录临时文件并原子替换。Evidence Store 与 Baseline Store 跨文件分别提交；一个成功、一个失败时 Summary 标记 `partial`。

### 4. 精确读取与校验

```bash
python3 .claude/skills/evidence-archive/scripts/archive_evidence.py get \
  --kind evidence \
  --archive-record-id <id>

python3 .claude/skills/evidence-archive/scripts/archive_evidence.py get \
  --kind baseline \
  --baseline-id <id> \
  --baseline-version <version>

python3 .claude/skills/evidence-archive/scripts/archive_evidence.py verify-store \
  --kind evidence
```

不提供列表、模糊搜索或“取最新一条”。

## 身份、重复与纠正

- `evidence_id`：观察事实身份，原样继承；
- `lineage_fingerprint`：来源与规范化内容指纹；
- `payload_fingerprint`：Archive 对不可变快照计算；
- `archive_record_id`：来源、快照、治理、策略和动作共同形成的确定性事件 ID；
- `logical_object_ref`：同一 superseding 链的逻辑对象身份；
- `comparison_key`：允许为空；仅在确有可比对象时保留。

完全相同 Archive Event 返回 `duplicate` 并返回已有 Record Ref。内容或治理状态发生合法变化时追加 `superseding` 记录。`supersedes_ref` 必须指向同 Store、更早、同类型、同逻辑对象记录；禁止断链、跨类型和双后继分叉。

普通持久化保持原生命周期。只有 Govern Patch 明确给出 `action=archive` 和 `to_status=archived` 时，才保存 archived 生命周期快照。Archive 不修改 Govern latest 中的 `patch.applied=false`；归档记录以 `persistence_applied=true` 表示持久化已完成。

## 输出

`schemas/archive_summary.schema.json` 是轻量审计回执，不复制 Payload：

```text
run
data_quality
authorization
archive_target_refs[]
archive_results[]
store_updates[]
limitations[]
handoff
```

每个结果必须返回目标、record kind、结果、精确 Record Ref、Payload 指纹、授权引用、治理/审核引用和敏感等级。

只有至少一条记录成功或合法重复时才更新固定 Summary。全部失败、目标不明确或授权不足时不得覆盖最后一次有效 Summary。`handoff.handoff_status=terminal`。

完成 Summary 后运行：

```bash
node shared-workflow/generate-progress-preview.js
```

预览失败只告警，不回滚 Store 或 Summary。

## 自检

1. 目标是否唯一、已登记且属于允许的来源类型？
2. 用户授权或 Handoff 是否精确覆盖目标和字段？
3. 所有 required review 是否 approved？
4. Evidence/Baseline Patch 是否 `can_persist=true`？
5. 来源版本、run、稳定 ID 和摘要是否与计划一致？
6. Snapshot 是否只含类型白名单字段？
7. confidential 是否已形成归档安全快照？restricted 是否已阻断？
8. Payload 指纹和 Archive Event ID 是否由脚本计算？
9. superseding 链是否存在、同类型、同逻辑对象且无分叉？
10. Store、Summary 和返回的 Record Ref 是否经过写后复核？

## 运行边界

当前实现面向项目本地、显式低频、单工作区 POSIX 文件系统。它不是多主机数据库、加密保险库或法规删除系统。不增加索引、轮转或分片；当真实规模、并发或合规需求超出 JSONL 能力时，替换 Store Adapter，保持 Archive Request、Record Ref 和 Summary 合同不变。
