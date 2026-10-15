---
name: data-visualization
description: 将已登记的客观、主观、启发式、证据治理、候选根因、业务影响或效果回检产物，以及用户提供的 chart-ready 数据，转换为可追溯的图表规格、关系图、离线 HTML 和 Objective 专用分析报告。用户要求数据可视化、图表、Dashboard、桑基图、漏斗图、关系图或分析报告 HTML 时使用；只做可信表达，不读取原始日志或工单重做分析，不推导新指标、根因、价值链、ROI 或效果结论。
---

# Data Visualization

把已经形成的分析事实或用户整理好的数据转换为可信、可复核、可交付的视觉表达。保持上游语义，不建立第二套事实模型。

## Step 0 · 运行入口

先读取：

1. `shared-workflow/skill-graph.json`
2. `shared-workflow/data-analysis/artifact-registry.json`
3. `schemas/source-contracts.json`

识别一种输入模式：

| 模式 | 进入条件 | 能力上限 |
| --- | --- | --- |
| `registered_upstream` | 用户明确引用已登记的正式分析产物，并给出显式 Artifact Bundle | 生成 Objective 旅程专题、业务问题报告或完整诊断报告 |
| `chart_ready` | 用户给出已整理指标、表格、节点或边 | 直接生成图表规格和通用图表页 |
| `visualization_brief` | 只有表达目标，没有正式数值 | 只输出选图、布局和待补数据规格 |

输入已经充分时直接执行，不固定要求确认。只有覆盖已有交付文件、外部发布、敏感披露或会改变含义的口径歧义需要确认。

无法判断模式时，只问：

> 你希望读者通过这张图看懂什么？你现在有已经整理好的数据、上游分析结果，还是只有一个可视化想法？

不要询问 Schema、字段映射或契约版本。只有分母、单位、时间窗口或关系方向不明确且会改变含义时，再补问一个具体问题。

## 角色定义

本技能负责：

- 选择与数据意图匹配的图表；
- 定义视觉编码、标签、图注、响应式和无障碍规则；
- 继承并展示上游的来源、置信、限制与敏感性状态；
- 生成强类型 `visualization_package`；
- 在正式发布入口生成语义中立的离线图表页；
- 在同一正式发布入口为 Objective 4.0.0 生成确定性的交互式旅程报告；
- 从显式 Artifact Bundle 生成按业务问题组织的完整诊断报告。

本技能不负责：

- 读取原始埋点、日志、工单、访谈或页面材料重新分析；
- 创建指标、目标值、价值链节点、关系或结论；
- 重算漏斗、转化率、ROI、效果、根因或证据强度；
- 推荐工程图表库、安装依赖或扫描 `package.json`；
- 主动调用 Figma、GitHub、CDN 或外部预览 API；
- 主动读取或写回 Knowledge Wiki；
- 自动触发下游、归档或改变分析链状态。

## 总原则

1. 每个图必须能追溯到正式来源路径或用户提供的 chart-ready 数据。
2. 统一视觉样式，不统一上游关系语义。
3. 估算、预测、观测、目标和已验证结果必须显式区分。
4. 相关、支持、矛盾、候选机制与已验证影响不得相互升级。
5. 缺少必要含义时阻断正式图表；信息完整但质量有限时降级并显著标注。
6. 默认离线、自包含、无外部依赖，并提供文字或数据表替代表达。
7. 只执行展示层最小披露，不自行制定新的脱敏标准。

面向用户的图例、状态和说明使用 `shared-workflow/data-analysis/presentation-vocabulary.json`；内部 ID 只用于追溯，不作为图表主标签。

## 固定状态顺序

```text
mode_detected
→ source_contract_checked
→ semantic_gate_checked
→ visualization_spec_built
→ quality_checked
→ files_written
→ terminal
```

任一阻断门禁失败时，停止正式渲染并写入 `manual_review_requests[]`。不得静默降级。

## 来源契约与门禁

`registered_upstream` 只接受 `schemas/source-contracts.json` 登记的：

- `artifact_type`
- 当前唯一 `artifact_version`
- `producer_skill`
- 正式字段路径
- 来源 `run_id`

Artifact 来源必须提供完整 `artifact_instance_ref` 与面向 data-visualization 的 Handoff，消费路径必须同时落在 Handoff 和来源契约允许范围内。用户直接提供的 chart-ready 数据不冒充 Registry Artifact。

`registered_upstream` 还必须声明 `artifact_bundle.bundle_id`、`report_profile` 和与上游实例完全一致的 `source_run_ids`。不扫描目录寻找“最新”文件，不读取未登记旧版本，不根据相似字段名猜测路径。

生产者语义必须保留：

- Objective：指标、漏斗、旅程、报错和有限分群，只表达现有 `analysis_results`；
- Subjective：样本内主题、Finding、Evidence 和渠道/隐私限制；
- Heuristic：启发式 Finding、Coverage、Comparison 和验证请求；
- Evidence Govern：证据支持、限制、矛盾、情境和治理状态；
- Root Cause：候选机制链、替代解释和待验证项；
- Problem Framing：问题定义、目标人群、业务边界、成功定义和设计关注点；
- Experience Blueprint：方案摘要、具体方案和验证要求；
- Business Impact：问题影响、方案价值预测、敏感性和价值链；
- Outcome：干预、观测、归因、护栏和验证结论。

详细矩阵与失败规则见 `references/source-contract-risk-and-quality-rules.md`。

## 图表类型门禁

首版正式支持：

- `metric_card`
- `data_table`
- `bar`
- `grouped_bar`
- `stacked_bar`
- `line`
- `distribution`
- `scatter`
- `funnel`
- `sankey`
- `relationship_flow`
- `mechanism_chain`

只有边含有可比较的非负流量时使用 `sankey`；只有阶段转化数据时使用 `funnel`；只有关系时使用 `relationship_flow` 或 `mechanism_chain`，不得以线宽暗示规模。

不支持的类型在正式发布时失败关闭，不得猜测转换或自动改写 `chart_type`。只有调用方显式提交 `data_table`、`spec_only`，或带非空数据表与限制说明的 `render_status=degraded` 时，才交付降级结果。

`distribution` 的正式图只接受上游已提供的明确分箱及非负频数/比例；只有原始样本时不得在展示层自动分箱，应失败关闭或由调用方显式提交降级数据表。当前 `bar`、`grouped_bar`、`stacked_bar` 和 `funnel` 正式图只支持非负值；带符号数据使用显式数据表，不得取绝对值或自动换图。

按任务读取：

| 任务 | Reference |
| --- | --- |
| 比较、趋势、分布、单值或图表编码 | `references/chart-selection-and-visual-encoding-rules.md` |
| 关系图、机制链或 Business Impact 已有价值链 | `references/relationship-and-value-expression-rules.md` |
| HTML、Dashboard、移动端或无障碍 | `references/report-responsive-accessibility-rules.md` |
| 来源、门禁、敏感信息、质量和写入风险 | `references/source-contract-risk-and-quality-rules.md` |

## 执行流程

### Step 1 · 建立输入契约

把请求写成 `schemas/input.schema.json` 对应的结构。`visualization_brief` 没有数值时，不得生成正式数值图。

报告配置固定为：

- `objective_journey`：单一 Objective 实例，提供完整旅程结论与交互路径；
- `business_problem`：以问题、证据、机制、方案和价值组织显式来源；
- `full_diagnostic`：在业务问题结构上纳入已显式绑定的 Objective、Subjective、Heuristic、Govern、Root Cause、Problem Framing、Experience Blueprint、Business Impact 与 Outcome。缺少的环节明确列为“本次未纳入”，不得扫描补齐。

```text
python3 .agents/skills/data-visualization/scripts/validate_visualization_package.py \
  validate-input --request [visualization-request.json]
```

### Step 2 · 生成可视化规格

`registered_upstream` 先由显式 Artifact Bundle 生成确定性候选：

```text
python3 .agents/skills/data-visualization/scripts/validate_visualization_package.py \
  build-bundle --request <visualization-request.json> \
  --package-output <candidate-package.json>
```

Objective 单源旅程专题也可使用下方专用构建器；两种方式最终都进入同一个 publisher。

每个 `visual_outputs[]` 至少声明：

- `visual_id`
- `title`
- `intent`
- `chart_type`
- `render_status`
- `data_ref`
- `rationale`
- `epistemic_status`
- `encoding`
- `accessibility`
- `responsive`
- `caveats`

每个 `relationship_diagrams[]` 必须声明生产者、原始关系类型、来源引用、节点、边、置信或限制。不得创建上游不存在的关系。

### Step 3 · 校验候选包

运行：

```text
python3 .agents/skills/data-visualization/scripts/validate_visualization_package.py \
  validate --package <candidate-package.json>
```

不要在校验阶段写 HTML、Context 或第二套报告。通用图表页只在 Step 5
的正式发布入口生成，只组织已校验的图表、关系、来源和限制，不生成分析叙事。

### Step 4 · Objective 专用报告

用户明确要求 Objective HTML 时，先生成不含交付路径的候选包：

```text
python3 .agents/skills/data-visualization/scripts/render_objective_report.py \
  --objective <objective-artifact.json> \
  --package-output <candidate-package.json> \
  --source-ref objective
```

只接受 Objective `4.0.0`。候选包必须声明消费
`analysis_results`、`findings`、`limitations` 和授权 Handoff，不写
`spark-output/context/data-visualization.json`，也不提前生成 HTML。

报告按“范围与质量 → 整体表现 → 任务停止/流转/重复 → 报错与待复核消息模式 →
业务分群 → 待验证内容 → 技术附录”组织已有事实。未请求模块不渲染；无法评估
模块解释原因；核心指标冲突时不得显示单一 KPI。没有正式业务阶段映射时只称为
“任务节点流向”，不得由展示层创建阶段映射。路径专题直接投影 Objective 的完整路径、节点和连线事实，支持真实路径/最多路径/正式理想路径标记、筛选、节点与连线同步高亮，以及任务数、事件次数、占比、P50/P70/P90、报错、退出和折返详情；没有正式业务蓝图时不得把高频路径标为理想路径。任一路径节点不存在于 `stage_nodes`，或任一相邻节点不存在于 `stage_transitions` 时，以 `projection_consistency_error` 失败关闭，不在浏览器端创建空节点兜底。

### Step 5 · 单一正式发布

无论使用 Objective 专用模板还是通用模板，都只从同一入口发布：

```text
python3 .agents/skills/data-visualization/scripts/validate_visualization_package.py \
  publish --package <candidate-package.json> \
  --request <visualization-request.json>
```

发布器校验请求来源、Artifact Instance、来源中登记的原始 Handoff、Artifact Bundle、requested paths 与候选包
consumed paths；根据 `report_profile` 选择 Objective 旅程模板、业务问题模板或完整诊断模板。正式 JSON
与 HTML 使用同一 Run、Purpose 和来源，并共同写入
`spark-output/results/visualization/`。`output_files[]` 必须指向这组真实不可变
路径。渲染或必需交付失败时不得发布，也不得更新 Current Pointer。

## 输出契约

复用共享顶层信封：

- `run`
- `limitations`
- `handoff`
- `analysis_results.visualization_package`
- `manual_review_requests`
- `quality`
- `write_safety`

正式结构见 `schemas/output.schema.json`。`analysis_results.visualization_package.recalculation_performed` 必须为 `false`。

写入规则：

- 交付路径必须位于指定 `output_root`；
- JSON 和 HTML 采用临时文件加原子替换；
- 正式结果按 Registry 的 `immutable_result_with_purpose_pointer` 发布；
- 新运行不得再写旧的 `context/data-visualization.json` 或
  `data-visualization/objective-analysis-report-*.html`；
- 契约中只记录相对路径，不写入绝对本机路径或访问令牌。

## 标准交接

本技能是可跳过的终点型支持技能：

- `handoff.handoff_status = terminal`
- 不自动调用分析、验证、Knowledge Wiki 或 Evidence Archive
- 发现来源、口径或敏感性问题时只写 `manual_review_requests[]`
- 是否归档由用户或套件层显式决定

成功写出并校验后执行：

```text
node shared-workflow/generate-progress-preview.js
```

预览刷新失败只告警，不改变正式产物状态。

会话内输出：

```html
<!-- spark-context:data-visualization ref="spark-output/context/current/visualization.json" -->
数据可视化已完成：mode=[source_mode]，outputs=[N]，quality=[pass/degraded]，handoff=terminal
<!-- /spark-context:data-visualization -->
```

## 自检

1. 输入是否属于三种模式之一？
2. 是否只读取当前正式来源契约？
3. 是否记录每个消费字段的来源运行和路径？
4. 是否没有新增指标、关系、价值链或分析结论？
5. 桑基图是否具备真实权重？
6. 估算、预测和已验证结果是否清楚区分？
7. 低质量或敏感信息是否显著限制或进入人工复核？
8. HTML 是否离线、自包含、响应式并有文字/表格替代？
9. 输出路径是否安全且未意外覆盖？
10. 是否保持 `recalculation_performed=false` 和终点交接？
11. 正式 JSON 的 `output_files[]` 是否与同目录正式 HTML 完全对应？
12. 是否只有一个正式发布入口，没有产生第二套 Context 或 HTML？
13. registered_upstream 是否显式绑定 Artifact Bundle，且没有读取包外 current/latest？
14. 旅程图是否能区分真实路径、最多路径和正式理想路径，并展示报错、退出、折返和多类耗时？
