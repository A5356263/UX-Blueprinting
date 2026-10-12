---
name: business-impact
description: 问题影响与具体方案价值评估技能。用于从客观、主观、启发式、证据治理或候选根因的结构化结论中判断影响哪些企业或用户、产生什么影响、不处理会损失什么；在存在 Experience Blueprint 或用户明确具体方案时评估价值—投入、预测收益和 ROI；在 Outcome Validation 放行效果后重估实际价值。可单独调用或显式承接上游，但不读取原始日志、工单、企业 ID 明细或截图，不重新分析指标、验证因果、生成具体方案、承诺预算排期或把预测写成已验证收益。
---

# 业务影响与方案价值

把已识别的问题和具体方案翻译成可审阅的业务决策信息。一个技能覆盖三个时点：问题影响、方案上线前价值预测、效果验证后价值重估。

## Step 0 · 运行入口

### Step 0.1 · 本 Skill 产物状态

执行前只检查以下正式 latest 是否存在：

- `spark-output/results/business-impact/ 与 spark-output/context/current/business-impact.json`
- `spark-output/business-impact/business-impact-report.md`

存在时只提示“检测到本 Skill 已有正式产物（已产出）”。禁止读取正文、解析 JSON、自动比较旧结果或据此改变本轮模式。只有用户或正式 Handoff 明确要求承接上一版时才读取。

### Step 0.2 · 正式输入与上下文模式

本轮输入只来自用户明确提供或正式 Handoff 明确引用的内容：

- `independent`：只消费本轮问题、方案、业务指标、规则、成本或财务参数；不扫描工作区。
- `chain_context`：只消费显式 Artifact Instance Ref、正式 Handoff 与字段引用；Artifact Registry 只校验身份、生产者和当前契约版本。

读取前核对项目、问题、方案、人口口径、时间窗口和 `run_id`。存在 Evidence Govern 放行问题时以其问题边界为准，不再读取原始分析包重新拼问题。未经治理的多个来源分别形成 preliminary Case，不做跨源匹配或合并。

### Step 0.3 · 裸激活

用户只调用 `/business-impact` 时固定回复：

```text
请把已经识别的问题或分析结果发给我。我会先判断影响哪些企业或用户、造成什么影响，以及不处理的损失。
如果已经有具体优化方案，也可以一起提供；具备方案和投入依据时，我会进一步评估投入产出。
```

随后等待正式输入，不扫描历史聊天或目录。

## 角色定义

- 负责 Problem Impact：影响对象、影响链、cost of inaction 与 addressable opportunity。
- 负责 Solution Value：具体方案的指标价值映射、投入、收益、ROI 与敏感性。
- 负责 Validated Revaluation：消费 Outcome Validation 结果后重估价值。
- 不负责原始数据分析、跨源互证、候选根因生成、具体体验方案、效果验证、预算审批或路线图排期。

`root-cause-synthesis` 判断“为什么发生”；`experience-blueprint` 形成“具体怎么优化”；`outcome-validation-recheck` 判断“是否真的改善”；本 Skill 判断“影响多大、方案是否值得”。

## 总原则

1. 问题、方案、指标、成本和价值全部显式引用，禁止补造数字。
2. 企业级数据只能表述为企业，不能写成自然人用户。
3. 相关、预测和已验证结果分开表达。
4. 业务价值不得提高证据成熟度、根因置信度或效果可信度。
5. 所有正式数值由标准库脚本计算，Markdown 不自行计算。
6. 高 ROI 不能抵消合规、安全、公平性或关键分群受损。
7. 缺少输入时优先降级，不把执行做成问卷。

用户报告按 `shared-workflow/data-analysis/presentation-vocabulary.json` 展示中文状态、含义和下一步；稳定 ID 与状态码只保留在 JSON、引用明细或调试附录中。

## 项目与状态

`project_name` 优先使用显式输入，其次继承正式 Handoff；无法确定时使用问题主题。一次运行固定一个项目，跨项目输入直接阻断。

状态顺序：

```text
INIT
→ INPUT_RESOLUTION
→ MODE_AND_GATE
→ PROBLEM_IMPACT
→ SOLUTION_VALUE（条件式）
→ VALIDATED_REVALUATION（条件式）
→ DERIVE_AND_VALIDATE
→ OUTPUT_COMMIT
→ HANDOFF
```

本 Skill 可重复调用，但不得自动读取上一版。

## 先读什么

启动时读取：

1. `shared-workflow/skill-graph.json`
2. `shared-workflow/data-analysis/artifact-registry.json`
3. `shared-workflow/data-analysis/references/context-handoff-protocol.md`
4. `references/source-and-problem-impact-rules.md`（每次）
5. `references/enterprise-transition-and-metric-value-rules.md`（涉及企业/用户状态转化或指标价值时）
6. `references/cost-roi-and-sensitivity-rules.md`（存在具体方案、投入或 ROI 请求时）
7. `references/reporting-handoff-and-risk-rules.md`（生成输出前）

不通读无关 references。

## 上游职责与输入权限

| 来源 | 允许消费 | 禁止替代 |
| --- | --- | --- |
| Objective | evidence、显式引用的 baseline/segment/metrics | 不读取行级数据，不重新算指标 |
| Subjective | evidence；finding 仅作 preliminary signal | 不外推总体发生率 |
| Experience Heuristic | promoted evidence | 不当作真实行为或规模 |
| Evidence Govern | 放行问题、用途、限制、人工门禁 | 不放宽治理边界 |
| Root Cause | 候选机制、方向、指标假设、限制 | 方向不是具体方案或效果 |
| UXB | 角色、业务边界、正式规则 | 不替代问题证据 |
| Experience Blueprint | 具体方案、范围、状态与限制 | 不直接推导工程成本 |
| Journey Metrics | 指标与埋点口径 | 不替代实际 baseline |
| Outcome Validation | 放行的效果变化与 guardrail | 不重新验证效果 |
| Knowledge Wiki | 有来源、范围和有效期的正式业务规则 | candidate 或过期规则不能支撑量化 |
| 用户/正式计划 | 明确问题、具体方案、成本和财务参数 | 临时参数不自动沉淀为知识 |

原始企业状态表、任务明细和方案曝光明细先交给 Objective；用于效果判断的覆盖组/前后数据先交给 Outcome Validation。本 Skill 只读结构化聚合结论。

人口、基线、指标价值链和效果输入都必须携带 `measurement_scope`，至少声明 grain、dimensions、time_window 和 population_definition。企业及企业×板块人口来自 Objective；NPS 效果来自 Subjective 与 Outcome，保持 `survey_response` 粒度。只有显式业务规则才能把企业状态变化或 NPS 点数连接到货币价值；粒度、维度或窗口不一致时失败关闭，不做隐式换算。

读取 Registry Artifact 时必须验证完整 Artifact Instance Ref；案例字段必须落在该来源正式 Handoff 已放行的 Payload 内。摘要、项目、版本、run、producer 或用途任一不匹配时 fail closed。

### Knowledge Wiki 条件读取

仅当角色范围、业务规则、指标口径、单位价值或成本政策会改变结论时读取。按 UXB 协议执行：`index → 命中领域入口 → 命中 raw/章节 → 停止`。记录来源、适用范围、有效期和敏感等级；不遍历、不猜目录、不自动写回。

## 运行模式与门禁

### `problem_impact`

输入至少包含一个结构化问题或用户明确的问题描述。输出 affected population、影响组件、cost of inaction 和 addressable opportunity。没有具体方案时到此结束。

### `solution_value`

必须存在 Experience Blueprint、用户明确提供的具体方案或显式正式计划。Root Cause
的 `intervention_direction_candidate` 只能限定目标和约束，不能单独触发本模式。输出
上线前 `forecast`。

正式数据分析主链中，只接受 Registry 登记的 Experience Blueprint `4.0.0`，并要求
精确 `solution_ref` 指向 `readiness=valuation_ready` 的方案。先运行
`scripts/validate_business_impact.py validate-input <request-json>`；版本、Run ID、
Pointer、方案用途许可或估值输入状态不匹配时失败关闭。不得扫描 Blueprint latest
猜测方案，也不得把 Root Cause 方向补写成方案。

### `validated_revaluation`

必须显式引用上一版预测和 Outcome Validation 已放行的效果结果。只更新价值估算，不重新判断效果。使用轻量 `prior_valuation_snapshot` 保留预测—实际差异。

同一运行可顺序执行 `problem_impact → solution_value`，或显式执行 `validated_revaluation`。`break_even_analysis` 不属于当前能力。

## 用户沟通

输入充分时直接执行，不询问是否开始。缺少信息时先完成可完成部分并自动降级。只有以下情况硬停：

- 无法确定要评估哪个问题；
- 多个具体方案存在实质分叉且未指定；
- 项目、币种、企业口径或时间窗口冲突；
- 用户要求 decision-ready ROI，但关键财务参数未确认；
- 引用跨项目或跨运行。

一次只问一个用户能回答的问题，使用“评估多长时间的收益”“是否有大致投入范围”等表达，不展示内部字段名。未确认预测标记 `provisional_forecast`；正式来源或关键假设确认后才可标记 `decision_ready_forecast`。

## Step 1 · 输入解析与血缘

为每项输入建立 `valuation_inputs[]`，记录语义角色、来源 Skill/字段、版本、人口口径、时间窗口、单位、来源状态、允许用途和敏感等级。优先级：显式正式上游 → 正式业务规则 → 用户补充 → 情景假设。

规则所有权：

```text
分析方法 → 本 Skill references
稳定业务事实 → Knowledge Wiki
项目参数与临时假设 → 本轮输入 / assumption_ledger
```

没有 Evidence Govern 时，每个单源问题分别标记 `preliminary`。只有治理放行问题可标记 `evidence_backed`。成熟度按 Case 记录，不设置包级 `candidate_multi_source`。

## Step 2 · Problem Impact

每个不同问题生成一个 `problem_impact_case`：

1. 固定问题、任务、场景与来源边界。
2. 区分 eligible population、observed sample、observed affected 与 estimated range。
3. 没有总体分母或代表性依据时禁止外推。
4. 人群规模来自多表关联时必须记录 `join_coverage`；零匹配、未知覆盖或没有正向
   匹配率时不得生成 measured/derived 投影。单一正式聚合来源可标记
   `not_required`，但必须说明原因。
5. 按适用性评估用户、产品、服务、业务、组织影响；缺证据写 `not_evaluable`。
6. 每项影响标注 `fact | inference | assumption`、关系类型、来源和去重组。
7. 计算或描述 `cost_of_inaction`。
8. 评估可触达机会 `addressable_opportunity`；它与 cost of inaction 禁止相加。

不得为同一证据分别估值，不得把多个未治理来源静默合并。

## Step 3 · Solution Value

一个“问题 × 具体方案”生成一个 `solution_value_case`。同一问题可有多个方案，但只有存在多个明确方案时才条件式派生比较视图；本 Skill 不生成替代方案。

估值层级：

1. `impact_only`：没有可评估具体方案，只保留问题价值。
2. `value_vs_effort`：有具体方案，以 `qualitative_value_links[]` 记录价值方向、相关指标和依据，可比较相对投入，但不输出量化指标价值链、金额收益或 ROI。
3. `quantified_roi`：方案范围、人口、baseline、效果情景/验证结果、转化、采用、单位价值、归因、成本、币种和窗口均有引用。

`metric_value_links[]` 是量化计算事实源，每条必须引用 baseline；程序从它派生 `impact_value_chains[]`。指标分析属于 Objective，指标定义属于 Journey Metrics，效果判断属于 Outcome Validation，本 Skill 只做指标变化到价值的映射。

同时记录：

- benefit components；
- disbenefit components；
- guardrail impacts；
- distributional effects；
- 不可用收益抵消的风险；
- effort profile 与来源；
- 敏感性和估值可信度。

没有正式成本时只输出相对投入，不生成工期、人天、报价或预算。总体正收益不得掩盖关键分群受损。

## Step 4 · 确定性计算与校验

将候选 JSON 写入会话临时位置，执行：

```bash
python3 .claude/skills/business-impact/scripts/validate_business_impact.py normalize <candidate-json-path> --output <normalized-json-path>
python3 .claude/skills/business-impact/scripts/validate_business_impact.py validate <normalized-json-path>
python3 .claude/skills/business-impact/scripts/validate_business_impact.py commit <normalized-json-path> --output spark-output/results/business-impact/ 与 spark-output/context/current/business-impact.json
```

脚本负责企业占比、三情景收益、成本、负向影响、净收益、ROI、回收周期、敏感性入口检查、派生链、摘要和 latest 原子提交。禁止模型在 Markdown 中另算数字。

只有通过 Schema 形状与语义校验的 normalized JSON 才原子替换 latest。失败时保留上一版，候选文件不进入下游。

## Step 5 · 输出

正式 JSON：

```text
spark-output/results/business-impact/ 与 spark-output/context/current/business-impact.json
```

Independent 默认同时生成：

```text
spark-output/business-impact/business-impact-report.md
```

报告是否生成只由 `requested_deliverables[]` 决定；Chain Context 与 Independent 都不得隐式取消用户要求的报告。报告章节与敏感数据规则见 `references/reporting-handoff-and-risk-rules.md`。HTML、图表和 Dashboard 交给 `data-visualization`。

不创建 per-run 目录、历史日志、Profile Registry、agents、subskills 或独立配置目录。需要长期保留的决策版本由用户显式交给 Evidence Archive。

## Handoff

- 高价值但证据弱：建议补证或进入 Root Cause。
- 值得解决但没有具体方案：建议 Experience Blueprint。
- 有方案但效果未知：建议 Outcome Validation。
- 已完成价值判断：可进入人工决策评审、Data Visualization 或显式 Evidence Archive。

本 Skill 不自动执行下游。`downstream_handoffs[]` 按目标技能、Payload 与用途声明最小权限；Evidence Govern 和 Root Cause 不得反向读取本产物改变证据或因果结论。

Evidence Archive 只可在用户明确批准 `approve_archive_decision_snapshot` 后读取正式 Handoff 放行的 `run`、`portfolio_summary` 和 `limitations`，形成聚合决策快照。企业 ID、逐客户价值、收入/成本明细、受限估值参数和计算中间量不得归档；决策快照不得被当作 Evidence、Baseline、Outcome 事实或 Wiki 知识。

完成写入后运行：

```bash
node shared-workflow/generate-progress-preview.js
```

失败只告警，不改变正式产物状态。

## 自检

1. 输入：是否全部显式引用、同项目、同口径、同时间窗口？
2. 问题：是否按 Case 记录成熟度，未做跨源匹配？
3. 人群：是否区分样本、总体、企业与自然人？
4. 方案：是否为具体方案，而非 Root Cause 方向？
5. 效果：预测、描述性差异和 Outcome 验证是否分开？
6. 价值：cost of inaction、addressable opportunity、收益是否未重复相加？
7. 财务：量化门禁、成本来源、币种、窗口、三情景是否齐全？
8. 风险：负向影响、关键分群与不可补偿风险是否检查？
9. 输出：所有数字是否来自脚本，摘要是否程序派生？
10. 交接：是否未反向改变证据、根因或效果结论？

## 硬边界

- 不读取原始日志、工单、截图、企业 ID 明细或预算明细补做上游分析。
- 不输出 validated root cause、实际效果声明、具体体验方案、最终立项、预算或排期。
- 不把主观比例或启发式严重度换算成总体发生率或金额。
- 不自动读取旧 latest、写 Knowledge Wiki、归档或执行下游。
- 不输出 `break_even_analysis`。
