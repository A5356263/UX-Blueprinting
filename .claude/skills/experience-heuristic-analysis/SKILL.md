---
name: experience-heuristic-analysis
description: 基于截图、原型、页面、流程、体验蓝图、前端代码、DOM、Accessibility Tree 或 runtime 材料执行不评分的体验启发式走查，生成可追溯的 Findings、受控启发式 Evidence 和可读报告。适用于现状发现、限定范围检查和改版前后风险回检；不分析行为数据或主观反馈，不做界面评分、完整无障碍合规、跨源互证、根因、具体方案、效果、投入或 ROI。
---

# 体验启发式分析

将本轮明确提供或实际采集的界面材料转成体验风险观察。JSON 是唯一事实源，Markdown 只呈现 JSON 中允许披露的内容。

## Step 0 · 运行入口

### Step 0.1 · 正式产物

- `spark-output/results/heuristic/ 与 spark-output/context/current/heuristic.json`
- `spark-output/experience-heuristic-analysis/experience-heuristic-report.md`

只在 4.0.0 包校验成功后更新 latest。失败、输入不足或不可评估时保留上一份成功结果。不建立每次运行目录，不自动归档。

### Step 0.2 · 正式输入

只使用：

- 用户本轮提供的截图、原型、链接、文件、代码或结构化材料；
- 用户明确授权读取的目录或项目材料；
- 本轮由工具实际取得并登记的界面证据；
- Chain Context 下用户明确引用的上游材料；
- 判断确实需要时，从 Knowledge Wiki 最小充分读取的规则。

禁止自行扫描工作区寻找可能相关的历史材料。链接或工具内容未实际取得时，不得声称已经检查。

### Step 0.3 · 裸激活沟通

用户未提供可观察材料时，只需用大白话说明：

```text
请发我想检查的页面、流程、原型、截图、代码或文件路径。也可以直接说只想检查哪个页面或改版内容。
```

用户已给出材料和目标时直接执行。只有范围会实质改变结论、回检缺少前后材料、读取需要额外授权或规则冲突无法判断时，才补问最少必要问题。

### Step 0.4 · 运行模式

- `source_mode=independent`：只使用本轮输入。
- `source_mode=chain_context`：只读取明确引用的上游。
- `analysis_mode=discovery`：发现当前可观察风险。
- `analysis_mode=intervention_recheck`：比较明确的前后材料，只描述风险变化。

至少需要一个可观察来源。只有业务问题、客观数据或主观反馈而没有界面材料时，不生成正式分析包。

## 角色定义

本 Skill 负责：

- 识别可观察的界面、流程与设计风险；
- 分开记录观察、风险假设和补证需求；
- 将通过门禁的 Finding 转成供 Evidence Govern 使用的启发式 Evidence；
- 对明确可比的前后材料做风险差异回检。

本 Skill 不负责评分、真实用户行为判断、发生率、跨源互证、根因、具体体验方案、业务价值、投入或正式效果判断。

## 总原则

1. 一个可观察问题只保留一个 Finding；多个分析透镜不得重复计数。
2. `confidence` 只表示观察可靠性，不表示因果置信度。
3. 启发式 Evidence 固定不是强证据，并且需要人工复核。
4. 风险等级只表示设计风险，不表示频率、人数、业务价值或实施优先级。
5. 项目正式规范优先于通用启发式；业务判断必须保留规则依据。
6. 回检只描述风险变化，固定 `effect_claim=not_claimed`。
7. Objective、Subjective 等结论只能作为明确的检查范围提示，不能支持 Finding 或提高置信度。
8. 原始截图、受限内容和未脱敏文本不得自动进入报告、可视化、归档或 Knowledge Wiki。

用户侧使用 `shared-workflow/data-analysis/presentation-vocabulary.json` 的中文表达。ID、状态码和用途码只保留在 JSON 或追溯明细。

## 触发边界

适用：视觉清晰度、信息架构、流程连续性、组件、边缘状态、文案、响应式、反馈、基础可访问性和 Brief 一致性观察。

不适用：

- 行为指标、漏斗、日志和路径：`objective-data-analysis`
- 工单、评论、访谈和群聊：`subjective-feedback-analysis`
- 跨源关系、情境评估和治理放行：`evidence-govern`
- 候选根因：`root-cause-synthesis`
- 具体体验方案：`experience-blueprint`
- 投入与价值：`business-impact`
- 正式效果：`outcome-validation-recheck`
- 评分型界面诊断或批量 UI CI：`interface-audit`
- 完整 WCAG 或法律合规：专项人工审计

## 固定状态顺序

```text
INIT
→ INPUT_GATE
→ SOURCE_REGISTER
→ PRIVACY_GATE
→ SCOPE_BUILD
→ HEURISTIC_REVIEW
→ FINDING_DEDUP
→ EVIDENCE_PROMOTION
→ OUTPUT_VALIDATE
→ WRITE
→ HANDOFF
```

## 先读什么

执行前读取：

1. `shared-workflow/skill-graph.json`
2. `shared-workflow/data-analysis/artifact-registry.json`
3. `shared-workflow/data-analysis/references/context-handoff-protocol.md`
4. 本轮明确输入

再按任务只读取必要 reference：

| 任务 | Reference |
| --- | --- |
| 分类、严重度、去重、Coverage、Promotion | `references/heuristic-review-rules.md` |
| Web/Mobile、视觉、响应式、基础可访问性 | `references/platform-accessibility-rules.md` |
| 来源能力、材料边界、Scene Descriptor | `references/interface-evidence-guide.md` |
| 置信度、隐私、规则依据、补证、下游用途 | `references/confidence-and-boundary-rules.md` |

`references/method-provenance.md` 只在维护方法来源时读取。

## Knowledge Wiki 条件消费

纯视觉、可见状态、响应式和可访问性线索默认不读 Wiki。只有业务规则、角色权限、预期流程、字段语义、异常机制或设计规范会改变判断时才读取：

```text
knowledge/wiki/index.md
→ 实际路由入口
→ 命中的 raw 文件或章节
→ 达到最小充分依据后停止
```

Index 和 README 只负责路由，不作为规则事实。知识的适用范围或版本无法确认时，生成 Validation Request，不自行裁决。本 Skill 只读 Wiki，不生成或提交知识候选。

## Step 1 · 输入与隐私门禁

根据 `schemas/input.schema.json` 建立 4.0.0 Request，并先运行：

```bash
python3 .claude/skills/experience-heuristic-analysis/scripts/validate_heuristic_package.py validate-input <request.json>
```

逐项登记来源类型、引用、获取方式和预期范围。不得在引用中保存本机绝对路径、凭证或带密钥的 URL。

读取材料后，在 `run.sources[]` 中记录：

- 实际加载状态和指纹；
- 本轮确实可观察的能力；
- 材料限制；
- 敏感级别、隐私状态、是否已脱敏和披露限制。

隐私状态：

- `safe`：可以按允许用途展示；
- `restricted`：内容受限，只能使用脱敏结论；
- `needs_review`：是否可披露尚未确定；
- `blocked`：不得进入 Evidence 或可读输出。

Finding 和 Evidence 必须独立记录隐私状态。来源受限但结论已可靠去标识化时，结论可以是 `safe`；无法确认时使用 `needs_review` 并请求人工复核。

## Step 2 · 范围与来源能力

`analysis_scope.review_areas` 明确本次检查领域：

```text
flow-continuity | ia | components | visual-hierarchy | edge-states
copy | responsive | feedback | accessibility | brief-consistency
```

- `full_review` 必须覆盖全部 10 类；
- `scoped_review` 只覆盖明确范围；
- `diff_driven_review` 只覆盖前后变化影响的范围。

截图只能支持静态可见判断；源码不等于最终界面；只有实际读取的 DOM、A11Y Tree、runtime 或 Figma 内容才能声明对应能力。具体能力白名单见 `references/interface-evidence-guide.md`。

## Step 3 · 统一走查与 Findings

每个 Finding 只有一个主 category。认知负担、可发现性、平台原则等作为 lens 或 tag。

每条 Finding 分开记录：

- 可直接观察到的内容；
- 基于观察提出的风险假设；
- 设计后续必须解决的关注点；
- 来源、位置、状态、可靠性和适用规则；
- 隐私状态、允许用途、禁止用途；
- 是否通过 Evidence Promotion，或未通过原因。

没有正式规则时，不把业务或 Brief 一致性写成确定结论。没有可靠颜色值时不输出精确对比度。不得输出完整合规结论、整体评分、覆盖率百分比或 pass/fail。

Coverage 使用：

```text
evaluated_with_findings
evaluated_no_finding
not_evaluable
not_in_scope
```

`evaluated_no_finding` 只表示现有材料下未发现明显风险，不表示完整审计通过。

## Step 4 · 补证与 Evidence Promotion

补证统一写入 `validation_requests[]`。`gap_type` 表示缺少什么，`blocks_evidence_promotion` 决定是否阻止对应 Finding 进入 Evidence。

Finding 只有同时满足以下条件才生成一个 Evidence：

- 至少一个已读取、具备相应观察能力的证据来源；
- 页面、流程、位置和状态可定位；
- Observation 与 Risk Hypothesis 已分开；
- 规则依据、置信度、隐私和用途边界明确；
- 不依赖未确认规则形成确定结论；
- 没有阻断性的 Validation Request。

每个 promoted Finding 恰好对应一个 Evidence。Evidence 的 `claim_type` 只允许：

```text
heuristic_observation | risk_hypothesis
```

所有 Evidence 固定：

```text
can_be_used_as_strong_evidence=false
manual_review_required=true
causal_claim_allowed=false
```

## Step 5 · 回检

`intervention_recheck` 必须使用结构化 `baseline_ref` 和 `current_ref`，两者指向明确 Artifact + Run + JSON Pointer，或明确 Source + Fingerprint。

只输出：

- 已消失的 Finding Key；
- 仍存在的 Finding Key；
- 新增 Finding Key；
- 可比 Finding 的风险等级变化；
- 范围是否可比。

Comparison 不生成 Evidence，不直接交给 Outcome，也不声明方案有效。

## Step 6 · 校验、写入与报告

先由 Agent 完成分析，再用确定性工具补全指纹、Finding Key 和派生汇总：

```bash
python3 .claude/skills/experience-heuristic-analysis/scripts/validate_heuristic_package.py normalize --input <request.json> <candidate.json> --output <normalized.json>
python3 .claude/skills/experience-heuristic-analysis/scripts/validate_heuristic_package.py validate --input <request.json> <normalized.json>
```

只有 `completed` 或 `completed_with_caveats` 可以正式发布并更新对应分析目的的 Current Pointer：

```bash
python3 .claude/skills/experience-heuristic-analysis/scripts/validate_heuristic_package.py write --input <request.json> <normalized.json>
```

Independent 默认写 JSON 与完整 Markdown；Chain Context 可以只消费 JSON；回检报告聚焦差异。受限或待复核内容在 Markdown 中只显示受限提示，不披露原文。

## Handoff

正式证据出口只有 `evidence-govern`：

```text
artifact_instance_ref = 已发布 Heuristic 实例的完整引用
payload_refs = promoted evidence_items 的绝对 JSON Pointer
```

没有 promoted Evidence 时，Handoff 必须 blocked。不得从本 Skill 直接进入 Root Cause、Outcome、Archive 或 Knowledge Wiki。

Data Visualization 可以在用户明确要求时表达 Findings、Coverage 或 Comparison，但必须继承隐私与用途限制，不得重判分析结论。Business Impact 只能把 promoted Evidence 当作初步问题信号，不得据此推算受影响人数或价值。

写入成功后运行：

```bash
node shared-workflow/generate-progress-preview.js
```

刷新失败只告警，不改变已校验产物。

## 自检

完成前检查：

- Request、来源和输出是否绑定到同一批输入；
- full/scoped/diff 范围与 Coverage 是否一致；
- 来源能力是否只声明本轮实际取得的内容；
- Finding 是否去重，Key 是否稳定；
- Evidence 是否与 promoted Findings 一一对应；
- 隐私、人工复核、允许用途和禁止用途是否完整；
- 规则冲突和阻断性补证是否阻止 Promotion；
- Summary、Comparison、JSON Pointer 和 Handoff 是否可确定性校验；
- 可读报告是否没有新增结论或泄露受限内容。

能修正的直接修正；不能修正的降级、阻断 Promotion 或写入 Validation Request。
