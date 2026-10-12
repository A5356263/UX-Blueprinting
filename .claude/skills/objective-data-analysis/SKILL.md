---
name: objective-data-analysis
description: 基于客观行为数据执行指标、任务漏斗、旅程路径、报错、有限业务分群、历史基线和功能使用分析，并生成可追溯的结构化结果与客观分析报告。用于用户要求分析埋点、前端日志、任务明细、漏斗、桑基路径、报错、历史异动、功能采用率，或要求独立生成客观数据分析报告时。默认使用“指标-2026”体验指标体系；不处理主观反馈原文，不声明根因、策略或 ROI。
---

# 客观数据分析

这个 Skill 负责把用户提供或明确授权的客观行为数据转换为可复核的指标、路径事实、问题线索和正式客观证据。默认输出统一 Context JSON；完整或报告意图增加 Markdown。需要 HTML、图表或桑基图时，交给 data-visualization。

## Step 0 · 运行入口

### Step 0.1 · 本 Skill 产物状态

执行前只检查正式产物是否存在：

- spark-output/results/objective/ 与 spark-output/context/current/objective.json
- spark-output/objective-data-analysis/objective-analysis-report.md

只允许检查是否存在。不得把上一份 latest 自动当成本次输入，不得因为已有产物改变任务范围或跳到下游；只有用户明确要求“对比上次结果”或提供 baseline_ref 时，才按登记路径读取相应历史资产。

若正式产物存在，先提示：

~~~text
检测到客观数据分析已有正式产物；本次成功后会更新 latest，失败时保留上一份成功结果。
~~~

### Step 0.2 · 正式输入获取

本次分析只使用用户本轮明确提供或明确指定的输入：

- 文件路径或上传文件；
- 正式发布时，文件必须能保留为 workspace 内相对引用；workspace 外文件可以用于现有非正式级别的临时分析，但在形成正式定位契约前不得发布为正式 Objective，失败时只返回 `external_source_reference_unresolved` 和来源标识，不回显本机绝对路径；
- 用户直接提供的结构化数据；
- 用户明确指定的 UXB、需求分析、业务配置或旅程定义；
- 用户明确授权读取的 Knowledge Wiki 内容；
- 用户明确指定的 baseline ID/version。

禁止：

- 扫描工作区寻找“可能相关”的数据；
- 因文件存在自动读取主观反馈或启发式分析结果；
- 把历史聊天中的零散口径自动当成正式合同；
- 为执行分析先复制一份原始数据到其他目录；
- 扫描 spark-output 或归档目录猜测最新版本。

### Step 0.3 · 输入模式与门禁

先确定输入模式：

- independent：只使用本次客观数据和明确业务口径，禁止读取主观分析、启发式分析和其他探索结论。
- chain_context：只读取用户明确指定的 UXB、需求分析、旅程定义或业务知识引用，用于补足字段含义、完成规则、步骤、分群和基线口径。

没有客观数据时，不输出客观分析结论。只有原始主观反馈时，交给 subjective-feedback-analysis；只有页面或设计稿时，交给 experience-heuristic-analysis。

## 角色定义

- 作为客观行为数据的独立分析入口；
- 负责指标、固定漏斗、实际旅程、报错、有限业务分群、历史基线和功能使用；
- 负责统一生成 findings、evidence_items、限制和血缘；
- 作为 Evidence Govern Phase 1 的正式客观证据上游；
- 作为 business-impact 和显式 data-visualization 的结构化输入。

本 Skill 不负责主观反馈分析、体验启发式走查、根因综合、优化策略、ROI、回检结论、证据治理或 Store 写入。

## 总原则

- 默认使用“指标-2026”，不要询问是否启用。
- 全程使用业务语言，不把 Schema、字段映射或内部模块名称当成用户问题。
- 先理解数据和业务边界，再计算。
- 描述性分析默认执行，并同时说明样本可靠性与影响规模。
- 统计推断按需执行，不默认套显著性检验。
- 用户报告使用 `shared-workflow/data-analysis/presentation-vocabulary.json` 的中文状态；run ID、Evidence ID 和状态码只保留在 JSON 与追溯附录。
- 只执行有业务依据的有限分群，不运行探索聚类。
- 当前窗口不得参与自身历史基线。
- 一个 Context JSON 是唯一事实源；Markdown 和 HTML 只表达它。
- 不把异常、差异、报错相关性或路径共现写成因果。

## 触发边界

在用户要求以下任务时使用：

- 分析埋点、前端日志、任务明细或客观行为表；
- 计算任务指标、漏斗、流失、时长或功能采用率；
- 分析实际旅程、路径流向、回退、循环或桑基数据；
- 分析安全报错模式、影响任务和步骤分布；
- 比较有业务依据的用户/场景分群；
- 建立或比较历史基线、识别基线异动；
- 独立生成客观数据分析报告。

不得因为工作区中存在数据文件而自动触发，也不得在用户明确要求主观分析、根因分析、业务影响或可视化时替代对应技能。

## 项目名确定

按以下优先级确定 project_name：

1. 用户明确指定；
2. 上游正式上下文明确提供；
3. 从本次分析对象提炼简短名称；
4. 无法确定时使用数据所描述的核心任务名称。

项目名确定后，在 run、scene_descriptor、Markdown 和下游交接中保持一致。

## 固定状态顺序

~~~text
INIT
→ INPUT_RECEIVED
→ CONTRACT_BUILDING
→ WAIT_CRITICAL_CONFIRMATION（仅关键口径无法可靠确定时）
→ PREPROCESSING
→ OBJECTIVE_ANALYSIS
→ EVIDENCE_CONVERGENCE
→ OUTPUT_GENERATION
→ HANDOFF
~~~

与 UXB 的区别是：本 Skill 不设置固定的逐阶段人工停顿。只有缺口会改变分子、分母、任务边界、完成条件或分析范围时，才进入 WAIT_CRITICAL_CONFIRMATION；其余情况直接执行。

## 当前结构

~~~text
正式输入与模式门禁
→ 上下文与最小充分业务知识
→ 本次 effective_analysis_contract
→ 统一预处理与质量门禁
→ 指标/漏斗/旅程/错误/分群/基线/功能使用
→ findings 与 evidence_items
→ 唯一 JSON 事实源
→ 条件 Markdown
→ evidence-govern（内部完成标准化、证据关联与治理）
→ 用户明确要求时并行 data-visualization
~~~

内部脚本只是计算模块，没有独立调用、确认、输出或下游交接资格。

## 先读什么

按任务读取，不要一次性加载全部参考：

| 场景 | 读取 |
| --- | --- |
| 指标-2026、分子分母、一次完成、样本与推断 | references/metric-rules.md |
| 文件读取、字段、任务实例、去重、事件分类、脱敏 | references/preprocessing-and-privacy-rules.md |
| 漏斗、路径、分群、功能使用、基线、发现与证据 | references/analysis-rules.md |

需要读取套件上下游时，先读：

1. shared-workflow/skill-graph.json
2. shared-workflow/data-analysis/artifact-registry.json
3. shared-workflow/data-analysis/references/context-handoff-protocol.md

## 上下文承接分支

### 模式 A · Independent

只使用本次客观数据和用户明确口径。禁止读取 subjective-feedback-analysis、experience-heuristic-analysis、root-cause-synthesis 或 business-impact 产物，即使这些文件已经存在。

### 模式 B · UXB / 需求上下文承接

用户明确要求基于 UXB 或需求分析继续时：

1. 按 artifact registry 读取指定正式产物；
2. 只提取任务对象、角色、步骤、状态、完成条件、异常规则和场景特殊口径；
3. 不继承上游的主观问题判断、方案偏好或未经验证假设；
4. 把实际采用规则及来源写入 effective_analysis_contract；
5. 数据事实与上游预期冲突时，保留数据事实并记录差异。

### 模式 C · 已确认业务配置承接

用户提供字段、事件、分群、功能或基线配置时直接采用，并保留依据与版本。通用指标公式不写进场景配置；场景特殊规则只保存在本次 effective_analysis_contract，不维护 Profile Registry。

## Knowledge Wiki 消费协议

仅当业务含义缺失且会改变分析口径时读取，沿用 UXB 的最小充分方式：

1. 读取 knowledge/wiki/index.md，定位能直接回答问题的主域实际入口。
2. 按入口逐层缩小范围，只读取命中的 raw 文件或章节。
3. 仅当依赖会改变规则、状态、责任、异常或审计时补读依赖域。
4. 达到当前判断所需的最小充分事实后停止。

硬规则：

- index 与 README 只负责路由，raw 才是正式事实；
- 不猜目录、不遍历 raw、不按相邻关键词扩读；
- 每项已读知识必须能说明它支持了哪个口径；
- 未命中时记录知识缺口，不得把推断写成确认事实；
- independent 模式未获用户授权时不得自动读取 Knowledge Wiki。

## Step 1 · 输入理解与合同建立

### Step 1.1 · 支持格式

支持 CSV、TSV、JSON、JSONL 和 XLSX。XLSX 需要可选依赖 openpyxl>=3.1。非关键 XLSX 不可读时继续处理其他来源并记录 source-level limitation；唯一来源或 `critical=true` 的关键来源不可读时整次失败，不更新该分析目的的 Current Pointer。

不支持 Parquet。需要时请用户导出为受支持格式，不安装 pandas 或 pyarrow 扩大依赖。

### Step 1.2 · 用户沟通

先从字段名、数据样例和明确上下文推断。不要把问题原样丢给用户，也不要让用户从零解释数据结构。先说出系统当前的理解和建议，再让用户确认或纠正。

默认采用“确认式沟通”：

1. 先用业务对象说明系统准备怎么理解；
2. 给出推荐口径及推荐原因；
3. 告诉用户最简单的回复方式；
4. 一次只确认一个真正会改变结果的问题。

例如，确认“什么算一次办理”：

~~~text
我先按下面的方式理解：

- 每张报销单算一次办理，不把每次点击单独计算；
- 同一张单据从开始填写到结束，都算在同一次办理里。

如果这样符合实际，直接回复“可以”就行；如果不对，请告诉我你们通常把什么算作一次办理。
~~~

例如，确认“走到哪一步算办完”：

~~~text
这份数据里同时有“提交成功”和“审批通过”。

如果你想看提单过程是否顺畅，我建议把“提交成功”算作办完；
如果你想看完整报销流程，我建议用“审批通过”。

你可以直接回复“按提单”或“按全流程”。
~~~

如果系统已经能形成高置信理解，只做一句轻量确认：

~~~text
我会把每张报销单当作一次办理，并以“提交成功”作为完成。这个口径如果没问题，我就直接继续分析。
~~~

如果用户也不确定，提供低负担出口：

~~~text
如果你现在不确定，可以回复“按你的建议先分析”。我会把采用的理解写进报告并标为待确认口径，不会把它当成已经确认的业务规则。
~~~

沟通规则：

- 说“每张单据、每次办理、走到哪一步算办完”，不要先说“任务粒度、主键、完成事件”；
- 能给推荐时必须给推荐，不让用户面对没有上下文的开放题；
- 能让用户回复“可以”或二选一时，不要求用户重新描述整套规则；
- 只有多个编号都可能代表同一业务对象时，才展示具体字段，并解释每个字段会怎样影响结果；
- 用户接受建议后，把来源标记为 analyst_proposed_user_accepted；用户没有确认时标记为 analyst_proposed_pending_confirmation；
- 待确认口径允许用于探索性描述，但必须进入 limitations，禁止用于强结论、基线入库或正式证据升级。

不要默认询问“字段映射情况”或“是否允许查看 schema/表头”。检查用户已提供文件的表头属于理解输入的正常步骤，不需要单独取得许可。

### Step 1.3 · effective_analysis_contract

合同按任务实际需要记录：

- 字段映射与任务粒度；
- 进入、提交、完成、草稿、退出、回退和报错事件；
- 固定漏斗或预期旅程步骤；
- 排除、去重和任务推导规则；
- 分群定义及其业务依据；
- 功能入口、曝光、使用和完成事件；
- 历史/当前窗口、指标字段、粒度和比较指纹；
- 规则来源与统计策略。

递归移除目标参考值、健康分、旧异动指标说明和旧异常规则。业务阈值必须有明确来源、版本、范围和时间窗，且不得冒充历史基线。

## Step 2 · 预处理与质量门禁

使用 scripts/input_adapter.py：

1. 读取明确列出的数据源和工作表；
2. 记录来源、行数、字段、大小和内容指纹；
3. 按来源应用明确映射、字段回退或高置信字段候选；来源粒度独立识别；
4. 按字段组合识别汇总指标、任务汇总、完整旅程节点、报错上下文、业务蓝图或通用事件；显式语义与字段能力冲突时停止，报错上下文不得替代完整旅程；
5. 应用排除、源内去重、排序和条件式事件分类；错误文本存在不等于报错事件；只有明确声明来源为重复副本并提供稳定事件键时才允许跨源去重；
6. 缺少任务 ID 时按 session/user、终态、明确重启事件或已确认超时阈值推导任务实例；活跃任务中的重复进入事件不自动拆单；
7. 输出数据质量、缺失映射、无效时间、排除和去重数量；
8. 默认不落盘行级中间数据。

关键任务边界无法可靠形成时，不计算任务级比例。任务边界存在但没有显式完成标记、已确认成功事件或正式允许终态时，完成指标同样标记为 not_evaluable，分子和比例保持 null；不得把未知完成状态写成 0，但其他输入充分的路径、报错和耗时分析继续。

## Step 3 · 客观分析

### Step 3.1 · 指标、漏斗、分群与功能使用

使用 scripts/task_analyzer.py：

- 默认计算任务完成率、一次完成率、报错任务率、草稿率、退出率和任务时长分位数；
- 同一指标存在汇总与明细来源时核对时间窗、粒度、总体和分母；同口径冲突失败关闭，不同口径并列说明；正式汇总缺少分母时可展示报告值但不得反推计数或生成计数型证据；
- 有固定步骤时计算进入、逐步/整体转化、绝对流失、步骤时长和同深度报错对比；步骤报错只能归因到错误事件实际所在步骤，未知步骤单列 UNKNOWN；
- 分群只使用 user_confirmed、uxb、business_config 或 upstream_requirement 依据；
- 分群复用核心指标的归一化完成状态，并强制互斥、UNKNOWN、最小样本量、任务数及完成数对账；少于两个样本充足的业务群体时不生成比较结论；
- 任务内分群字段默认要求一致，或使用明确声明的 first_non_empty/last_non_empty；
- 企业类型等维表只能通过显式 dimension_joins 关联；校验关联键唯一性、覆盖率和适用窗口，冲突重复键失败关闭，未匹配进入 UNKNOWN；
- 有明确功能口径时计算入口→使用、曝光→使用、使用→完成和合格用户/企业→使用；资格只能来自明确事件、字段规则或已确认名单。

### Step 3.2 · 实际旅程

使用 scripts/journey_analyzer.py：

- 优先使用完整旅程节点明细，其次使用任务汇总中的完整路径，再次使用具备任务、时间和节点的通用事件；报错上下文只用于定位和报错后行为；
- 按任务实例和时间或已声明路径顺序构造路径；
- 任务汇总已提供完整路径但未声明分隔符时，只在至少 80% 非空样本中识别明确结构分隔符（如 `->`、`→`、`>`）；同等覆盖优先较长分隔符，避免把 `->` 错拆成 `>`。无法稳定识别时才关闭路径分析；
- 任务耗时字段名明确携带 min/ms/s/hour 单位且各任务汇总来源一致时自动归一为秒，并记录单位识别依据；字段单位冲突或不明确时不计算耗时分位数；
- 输出成功/未成功路径、回退/循环、报错后行为，以及缺步、绕行、乱序、回退、重复步骤和意外终止等预期旅程偏差；
- 在报错任务与无报错任务都可识别时输出同窗口路径队列对比，只描述差异，不声明报错因果；
- 输出阶段 nodes、transitions 和终态；
- 输出完整路径分布及单路径任务数、占比和 P50/P70/P90；节点与连线同时保留任务数、事件次数、覆盖占比、报错任务和 P50/P70/P90，供报告直接投影；
- 校验任务总数与终态总数对账。
- 简单线性旅程使用 expected_steps；存在分支时使用有明确适用条件、必经/可选/替代节点和允许终态的 journey_blueprints。节点登记没有明确且唯一的顺序字段时只作为 `registered_nodes_only`，不得按行序或 Excel 内部行号推断正式顺序；没有正式蓝图时只分析实际路径，高频真实路径只能标为观察候选，不输出正式蓝图偏差。

固定漏斗负责业务声明步骤的同口径转化；Journey 负责真实路径和流向。不要重复计算同一事实。

### Step 3.3 · 错误分析

使用 scripts/error_analyzer.py：

- 先脱敏凭证、Token、Cookie、API Key、邮箱、手机号、证件号、支付卡号、IP、UUID、个人或单据 ID、URL 参数、文件路径和长数字；企业编号和企业名称可在授权范围内用于关联与分群；
- 先区分可行动错误、警告、确认、信息、成功状态和未知；确认、信息和成功状态不进入可行动错误排行，但保留排除数量与规则；
- 再按安全化报错信息、错误码和展示形式生成错误签名，并输出安全标签、类别、影响任务/用户/企业、重复密度、短时突发和步骤分布；触发操作的事件 ID 不参与错误签名；
- 脱敏状态分为 safe、uncertain 和 blocked；只有 safe 可保留剩余可读错误语义，其他状态只输出稳定签名、类别和通用安全标签；
- 不输出原始敏感参数，不把报错相关性写成因果。

### Step 3.4 · 历史基线

使用 scripts/baseline_analyzer.py：

- 严格排除当前窗口；
- 多行属于同一周期时，优先按分子/分母重算周期指标；否则必须声明 sum/mean/median/latest 聚合，缺失聚合口径时 not_evaluable；
- 校验指标合同、粒度、场景和比较指纹；
- 有 baseline_ref 时，只从共享 baseline store 精确读取该 ID/version；
- 输出 definition、comparability、comparisons 和可选 candidate；candidate 直接遵守共享 `baseline_item.schema.json`，以 `lifecycle_status=proposed`、`review_status=pending` 交给 Govern；
- 历史不足或口径不可比时不强行比较。

Objective 负责选择、计算并形成完整 Shared Baseline Item 候选；Evidence Govern 校验可比性、审核版本与生命周期，Evidence Archive 只应用获准 Patch 并原样写入 baseline store。后续阶段不得重新匹配、补字段或重算基线。

### Step 3.5 · 企业状态与板块人口

使用 `scripts/enterprise_state_analyzer.py`：

- 仅在来源显式声明 `enterprise_state_type`，或宽表包含明确企业状态标记时识别月活、深度月活、存续等状态；
- 以企业和企业×业务板块为两个独立粒度输出同窗人口快照、跨期进入/退出/持续及关联覆盖；
- 不默认这些状态互斥，不把状态名称或文件先后解释为转化层级；只有显式业务规则允许时才形成转化口径；
- 只交付聚合人口事实，不把企业 ID 明细复制给下游。

## Step 4 · 发现与正式证据

父技能统一生成：

- findings[]：本次客观结果的可读发现；
- evidence_items[]：允许跨技能消费的正式客观证据；
- limitations[]：数据、口径、样本和可比性限制；
- handoff：标准化、基线和显式可视化交接。

每个已完成且口径已确认的分析维度至少形成一条描述性 finding。只有同时具备样本量、影响规模、可靠性信息且不存在待确认口径时才生成 evidence_item；Top 1 本身不得自动称为问题或异常。各 analysis_results 子结果内聚自己的 status、reliability 和局部 limitations，顶层 limitations 只汇总影响解释或交接的限制。

每条 evidence_item 必须包含稳定 ID、statement、claim_type、metric_refs、完整 scene_descriptor、allowed_uses、forbidden_uses、run_id 和输入指纹。

禁止把 findings 绕过 evidence_items 和 Evidence Govern 直接写入 Store。

## Step 5 · 输出生成

使用 scripts/run_objective_analysis.py 汇总为唯一结构：

~~~text
run
scope
effective_analysis_contract
data_quality
analysis_results
  metrics
  funnel
  journey
  errors
  segments
  baseline
  feature_usage
  enterprise_states
findings
evidence_items
limitations
handoff
~~~

始终写入：

~~~text
spark-output/results/objective/ 与 spark-output/context/current/objective.json
~~~

完整或报告意图同时写入：

~~~text
spark-output/objective-data-analysis/objective-analysis-report.md
~~~

交付载体由 `requested_deliverables[]` 决定，与 `source_mode`、`analysis_intent` 分离。单独调用或聚焦分析只要请求 Markdown，就必须生成完整且可读的 Markdown；HTML、图表和桑基图交给 data-visualization。

输入先通过不可跳过的核心契约门禁；环境存在 jsonschema 时再做完整 Schema 校验。必需交付物全部成功后，将 JSON 与报告作为同一不可变结果发布，并只更新该分析目的的 Current Pointer。失败不得覆盖已发布实例。

执行入口：

~~~text
python3 .claude/skills/objective-data-analysis/scripts/run_objective_analysis.py \
  --request /absolute/path/to/request.json \
  --output-root spark-output
~~~

### Independent 报告结构

1. 执行摘要；
2. 范围与数据来源；
3. 预处理与数据质量；
4. 指标口径与核心 KPI；
5. 阶段与固定漏斗；
6. 终态、实际路径与桑基数据；
7. 报错与报错后行为；
8. 有业务依据的有限分群；
9. 历史基线与当前差异；
10. 功能使用；
11. 企业状态与板块人口；
12. 客观发现与证据；
13. 限制与下游交接；
14. 合同与血缘附录。

未请求或不可评估的章节必须说明原因，不补造结果。

## Step 6 · 标准交接

### evidence-govern

正常下一站固定为 evidence-govern。handoff 只交付 evidence_items[]、analysis_results JSON Pointer、limitations/lineage 引用和用途限制，不复制 baseline 或其他分析事实。Evidence Govern 不得读取行级数据、重算指标或重新匹配基线。

下游请求必须携带完整 `artifact_instance_ref`、Handoff 引用和可解析的 `payload_refs[]`；不得用“最新文件”、裸对象 ID 或自行拼接路径代替。

### business-impact

用户单独调用 Business Impact 2.0 时，只可显式读取 `evidence_items[]` 作为单源问题证据，并按需读取相关 `segments`、人口分母、指标与 baseline 引用作为 `population_metric` 或影响口径。不得读取行级数据，不得把单源证据升级为已治理事实，也不得把客观指标相关性直接写成方案效果。

### data-visualization

只在用户明确要求时交接 HTML、图表或桑基图。data-visualization 直接读取 analysis_results，并校验：

~~~text
Artifact Instance Ref 的 run、版本、producer、项目、用途和内容摘要全部匹配
~~~

可视化只做表达，不重算、不修改 Objective 结论。

### evidence-archive

不自动归档每次运行。只有用户明确指定或 Govern 放行的重要运行才交给 evidence-archive；下游仅消费请求中显式绑定的已发布实例。

正式产物完成后运行：

~~~text
node shared-workflow/generate-progress-preview.js
~~~

## 自检

1. 是否只读取正式输入和明确授权上下文。
2. 是否默认使用指标-2026，且未采用目标参考值。
3. 是否用业务语言确认真正关键的口径缺口。
4. 是否声明粒度、时间窗、分子、分母、去重和任务边界。
5. 是否区分未请求、不可评估、无发现和运行失败。
6. 是否只执行有业务依据的有限分群，并完成 UNKNOWN、互斥和对账。
7. 是否严格排除当前基线窗口。
8. 是否同时说明样本可靠性与影响规模。
9. 是否没有读取主观原文或声明根因、策略、ROI。
10. 是否以 JSON 为唯一事实源、按请求派生交付报告，且失败未更新该分析目的的 Current Pointer。
11. 是否按门禁交给 evidence-govern，并只在明确请求时交给 data-visualization。
