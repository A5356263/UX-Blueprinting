---
name: subjective-feedback-analysis
description: 主观反馈分析技能。用于分析客服工单、用户群聊、客服与运营记录、应用商店或社媒评论、问卷开放题、访谈摘录、内嵌反馈和客户成功记录，执行隐私脱敏、体验工单识别、主题聚类、情绪与紧急度分析、渠道偏差控制、样本内关注信号、条件性的前后反馈比较、主观证据转换、客观验证请求和知识候选提取。适用于用户要求分析用户声音、投诉、咨询、工单、评论、问卷、访谈或改版前后主观反馈变化时。不得用于分析埋点、漏斗、真实路径或原始系统日志，不证明真实发生率、最终根因、客观影响规模或方案效果，不自动发布知识。
---

# 主观反馈分析

## Step 0 · 运行入口

### Step 0.1 · 本 Skill 产物状态

执行前只检查以下正式产物是否存在：

- `spark-output/results/subjective/ 与 spark-output/context/current/subjective.json`
- `spark-output/subjective-feedback-analysis/subjective-analysis-report.md`

只检查存在性和版本标识。不得因为已有产物而自动读取正文、推断本轮范围、进入增量分析或覆盖结果。只有用户明确要求历史比较，或通过正式上游引用进入 `comparative_analysis`，才读取既有产物。

只接受 Registry 登记的 `4.0.0` 正式产物；其他版本没有真实适配器时阻断消费，不补造字段或自动迁移。

### Step 0.2 · 正式输入获取

只把以下内容作为本轮正式输入：

- 用户在本轮消息中提供的反馈文本、附件、截图、文件、链接或路径。
- 用户明确授权读取的目录或项目材料。
- 用户明确指定的 UXB、体验蓝图、旅程指标、历史反馈或其他正式上游引用。
- 已通过治理门禁且与当前问题直接相关的正式上下文。

不得自行扫描工作区寻找可能有用的工单、群聊、访谈、历史主题或业务资料。聊天历史只能帮助理解意图；除非用户明确说“就用上面的内容”，否则不得把历史讨论冒充正式输入。

### Step 0.3 · 裸激活沟通

用户只激活本 Skill、尚未提供具体材料时，输出：

```text
你好，我可以帮你分析用户反馈、客服工单、群聊记录、问卷、访谈或评论。

请直接把材料发给我，也可以给我文件路径。如果是改版前后对比，再告诉我改了什么，以及希望比较的两个时间段。

我会自动判断是整体分析还是前后对比；只有关键范围不清楚时才向你确认。
```

用户已经提供材料和目标时不要重复激活语，直接建立分析范围。

### Step 0.4 · 输入模式与门禁

使用两个正交字段表达执行方式：

- `source_mode=independent`：只使用用户本轮提供或明确授权的材料。
- `source_mode=chain_context`：只读取用户指定或图谱允许的正式上游引用。
- `analysis_mode=discovery`：分析当前反馈现状。
- `analysis_mode=comparative_analysis`：对齐并比较两个反馈窗口，不判断方案效果。

材料已明确时直接执行。只有以下信息会实质改变结果时才询问，最多三个问题：

- 分析对象或时间范围存在多种合理解释。
- 需要读取新增目录、额外数据源或敏感范围。
- 前后比较缺少两个窗口、干预说明或关键可比口径。
- 业务术语或字段含义存在无法安全推断的歧义。

## 角色定义

把散乱主观材料转成可追溯、经过脱敏且有使用边界的 `subjective_evidence_package`。说明样本中的用户表达、主题、情绪、紧急度、体验表现和待验证假设；不把表达升级为客观事实、真实发生率、最终根因或效果结论。

## 总原则

1. 先脱敏，再分类、聚类、引用和交接。
2. 始终写“样本内数量/占比”，不得写成总体发生率或真实影响人数。
3. 区分 Findings 与 Evidence：分析发现不自动成为正式证据。
4. 用户报告使用 `shared-workflow/data-analysis/presentation-vocabulary.json` 的中文状态；Item ID、Evidence ID 和机器状态码只保留在 JSON 与追溯明细。
4. 单条高情绪反馈不能证明高普遍性；低频阻断信号可以进入高关注，但必须保留频次和置信度。
5. 保留来源材料中的用户分群；没有业务依据时使用 `unknown`，不得发明高价值用户标签。
6. 用户或客服转述的报错只能标记为 `reported_error`，不得写成已验证 Bug 或系统日志事实。
7. Knowledge Wiki 只提供正式知识查询和候选审阅，不承担本技能的分析工作。
8. 任何下游不得绕过用途权限升级结论。

## 触发边界

适用：用户声音、客服工单、咨询、投诉、群聊、运营 QA、开放题、访谈、App 评论、社媒反馈、客户成功记录、体验工单识别，以及两个反馈窗口的主观比较。

不适用：

- 埋点、漏斗、真实路径、性能、接口或原始错误日志：交给 `objective-data-analysis`。
- 现有页面的启发式诊断：交给 `experience-heuristic-analysis`。
- 最终根因综合：交给 `root-cause-synthesis`。
- 受影响用户、业务影响和投入产出比：交给 `business-impact`。
- 干预有效性、护栏、归因和生命周期回检：交给 `outcome-validation-recheck`。

服务日志只有明确绑定的客户原声或客服转述字段才能进入反馈分析；内部处理记录仅作为 `internal_context`，不得聚类为客户反馈或提升为 Evidence。没有明确文本绑定时，不得把整行拼成反馈。

## 项目名确定

按以下顺序确定并保持一致：用户明确指定；从材料中的业务主题提炼；无法确定时使用核心反馈主题。不得使用敏感客户名或个人名作为项目名。

## 固定状态顺序

```text
INIT
→ INPUT_GATE
→ PREPROCESS_AND_PRIVACY
→ SUBJECTIVE_ANALYSIS
→ EVIDENCE_GATE
→ OUTPUT_VALIDATE
→ WRITE
→ HANDOFF
```

输入不足且无法安全继续时进入 `NEEDS_USER_INPUT`。不设置固定 Phase 1/Phase 2 暂停；只有 Step 0.4 的实质性歧义才暂停。

## 当前结构

```text
确认正式输入与模式
→ 脱敏、拆分、去重、线程合并
→ 工单体验相关性识别
→ 主题、情绪、紧急度、渠道偏差分析
→ 条件页面/流程/分群/前后比较
→ Findings 与 Evidence 分流
→ 条件客观验证请求与知识候选
→ 校验统一 JSON
→ 生成对应可读报告或索引
→ 按用途交接
```

## 先读什么

1. 读取 `shared-workflow/skill-graph.json` 和 `shared-workflow/data-analysis/artifact-registry.json`，确认当前版本、允许的上下文和下游。
2. 读取 `shared-workflow/data-analysis/references/context-handoff-protocol.md`。
3. 读取用户明确提供或授权的材料。
4. 按场景读取一层 references：

| 场景 | 读取 |
| --- | --- |
| 来源拆分、去重、线程、隐私 | `references/input-processing-rules.md` |
| 聚类、情绪、渠道偏差、分群、映射 | `references/analysis-rules.md` |
| Findings、Evidence、场景描述符、交接 | `references/evidence-contract-rules.md` |
| 规则、权限、配置、资格或预期流程线索 | `shared-workflow/data-analysis/references/business-rule-basis-rules.md` |
| 运营答复、知识冲突或复用 | `references/knowledge-candidate-rules.md` |
| 两个时间窗比较 | `references/comparative-analysis-rules.md` |
| 薪福通体验工单识别 | `references/ticket-experience-classification-rules.md` |

不得一次加载全部 references。

## 上下文承接分支

### 模式 A · Independent

只分析用户本轮提供或明确授权的材料。上游缺失不阻断主题分析；页面、旅程、业务规则和分群映射无法确认时写入 `limitations`。

### 模式 B · Chain Context

只读取用户明确指定的正式引用。保留上游事实、假设、限制和确认状态；记录 `upstream_refs`。上游信息与原始反馈冲突时保留冲突，不擅自覆盖。

### 模式 C · Comparative Analysis

只有两个反馈窗口可识别时执行。对齐来源范围、去重规则、主题版本、用户结构、时间窗和同期事件；只输出样本内变化及可比性，不使用 `effective`、`resolved`、`regressed` 等正式效果词。

## Knowledge Wiki 消费协议

仅当业务规则、状态、权限、路径或已有正式答案会改变判断时定向消费：

1. 先明确需要核对的问题。
2. 从 `.agents/skills/knowledge-wiki/knowledge/wiki/index.md` 进入能回答问题的主域实际入口。
3. 按 index 指向读取必要的知识集合 README、领域 README、单一 raw 或命中章节；每层必须缩小范围。
4. 仅当条件依赖会改变规则、状态、责任、异常或审计时补读依赖域，再回到主域闭环。
5. 达到最小充分证据后停止；未命中时记录知识缺口，不遍历 raw 补救。

index 与 README 只负责路由，raw 才是正式事实。记录已读入口、raw/章节、支撑判断和未确认部分。后台读取 Knowledge Wiki 时不切换当前 Skill，也不输出 Knowledge Wiki 激活语。

## Step 1 · 输入理解与分析范围

先执行机械输入准备，不让 Agent 直接读取未整理的整表：

```bash
python3 .agents/skills/subjective-feedback-analysis/scripts/validate_subjective_output.py \
  prepare-input <request-json> --output <temporary-prepared-json>
```

该步骤只做来源清单、只读解析、空表识别、去重、确定性隐私预处理和来源指纹；
不做主题聚类、体验语义判断或结论生成。Agent 只消费临时 prepared JSON 完成语义分析。
临时文件不得成为 latest，正式包写入后删除。

每个来源应声明 `content_role` 和 `field_bindings`。分别记录“文件已读取”和“反馈字段可分析”；`service_log` 未绑定文本字段时标记不可分析，绑定内部记录时只标记 `context_only`。企业编号和企业名称留在 `segment_fields` 用于授权范围内的关联与分群，不按个人隐私字段删除。

识别材料类型、渠道、时间窗、样本单位、线程字段、用户标识、页面/流程字段、语言、历史窗口和用户目标。用户已给出足够材料时，先用一句通俗表达说明理解和默认范围，然后继续；不要让用户选择模式或预先完成字段映射。

建立 `effective_analysis_contract`，至少包含：

- 纳入和排除范围。
- 样本单位、去重单位和线程合并规则。
- 渠道与时间窗。
- `source_mode` 与 `analysis_mode`。
- 可用页面、流程、旅程和分群依据。
- 隐私处理和报告引用方式。
- 条件能力是否启用及理由。

工单类输入先按 `ticket-experience-classification-rules.md` 标记体验相关性。用户要求筛选体验工单时，只把 `experience_related` 和 `possibly_experience_related` 纳入体验主题频次，但保留其他工单的数量与分流原因；用户要求分析全部反馈时，分类只作为标签。

## Step 2 · 预处理、隐私与质量门禁

按 `input-processing-rules.md` 执行来源拆分、反馈单元化、线程合并、稳定去重和脱敏。正式产物只保存脱敏文本、稳定脱敏实体引用和必要 source ref；不得保存未脱敏原文。

质量门禁至少记录：输入量、有效量、排除量、重复量、无法解析量、渠道覆盖、时间窗、字段缺失、线程完整性、分群覆盖、隐私风险、翻译或语义风险和样本边界。

无法安全脱敏的内容不得进入报告或 handoff，只保留风险类型、来源引用和 `manual_review_required=true`。关键材料完全不可读、所有内容均无法安全处理或范围无法确定时停止；其他缺口使用 `completed_with_caveats`。

## Step 3 · 主观反馈分析

按 `analysis-rules.md` 执行：

1. 开放编码并聚合为主题，不用预设分类压制新主题。
2. 计算样本内 `sample_count` 与 `sample_share`，说明分母和去重口径。
3. 分别判断情绪、紧急度和主观严重度。
4. 评估渠道偏差、重复风险和转述风险。
5. 可用流程阻断、权限/配置、信息展示、能力缺失、效率成本、业务规则和协作问题作为多标签辅助编码；辅助标签不得替代开放主题。
6. 只有材料或正式上下文支持时映射产品模块、页面、功能、操作节点、流程、旅程节点和用户分群；显式映射与推断映射分开保留。
7. 按产品模块、页面、功能、操作节点、渠道、企业群体和显式业务字段做受控单维或最多三维交叉切片；低样本降级，样本占比不得解释为客观发生率。
8. 使用 `analysis_attention_items` 表达值得优先关注的主观信号，不使用 P0—P3 产品优先级。
9. 用户、客服或运营提到规则、权限、配置、资格或流程要求时，输出 `analysis_results.business_rule_signals`，只标线索、来源和确认状态，不验证规则真伪。
10. `comparative_analysis` 下按参考规则输出 `analysis_results.comparison`。
11. 输入存在 0–10 NPS 评分时按 response_id 与来源稳定去重，输出总体、业务板块、企业状态及板块×企业状态的 promoter/passive/detractor、NPS 和样本数；只有提供邀请数或邀请标记时计算响应率。NPS 是 survey_response 粒度的主观指标，不与任务或企业粒度直接拼接。

体验工单六类标签是入口辅助标签，不替代开放式主题聚类，也不证明问题成立或根因。

## Step 4 · Findings、Evidence 与可选候选

按 `evidence-contract-rules.md` 分流：

- `findings`：样本内分析发现，可以包含待验证假设。
- `evidence_items`：满足追溯、脱敏、样本边界、置信度和允许用途要求的正式主观证据。
- `analysis_results.objective_validation_requests`：只有重要发现确实需要行为、错误、漏斗、路径或规模验证时生成。
- `knowledge_candidates`：只有材料中存在稳定答复、重复问题、冲突答案、过期风险或 workaround 时生成。

假设不得作为正式 evidence 的 `claim_type`。知识候选统一使用 `candidate_type` 区分 QA、回答模式和引导素材；全部 `manual_review_required=true`。

## Step 5 · 输出生成

结构化事实源固定写入：

```text
spark-output/results/subjective/ 与 spark-output/context/current/subjective.json
```

顶层固定为：

```text
run
scope
source_summary
privacy
data_quality
analysis_results
  nps_summary
findings
evidence_items
knowledge_candidates
limitations
handoff
```

必须符合 `schemas/output.schema.json`。先写临时文件并运行
`scripts/validate_subjective_output.py validate <candidate-json>`；通过后运行
`scripts/validate_subjective_output.py write <candidate-json>` 原子替换 latest，随后删除
临时 prepared/candidate 文件。失败时保留旧正式产物，不建立持久 run 目录，不声称完成。

### Independent 报告

默认生成 `spark-output/subjective-feedback-analysis/subjective-analysis-report.md`，依次包含：结论摘要；范围和材料；样本质量、去重与隐私；渠道偏差；主要主题；情绪、紧急度与低频高风险；关注信号；条件用户/页面/流程/旅程；代表性脱敏反馈；客观验证请求；可选知识候选；限制和下一步。

### Chain Context 索引

默认只生成简短制品索引；用户明确要求时再生成完整报告，避免套件重复输出。

### Comparative Analysis 报告

聚焦两个窗口的可比性、主题变化、情绪与渠道变化、再次出现和限制。不得判断方案有效、问题解决或因果归因。

Markdown 只能复述 JSON，不新增结论，不输出 HTML 或正式图表。

## Step 6 · 标准交接

- `evidence-govern`：默认下一站，只把 `evidence_items` 交给 Phase 1；Findings、比较结果和知识候选不得被规范化成正式证据。
- `business-impact`：用户要求影响与价值评估时，可显式读取 Evidence，并把 Findings 作为独立的低成熟度 problem signal；不得与其他未治理单源发现合并，不得用反馈条数推算总体规模、方案效果或 ROI。
- `data-visualization`：仅用户明确要求时，通过 Artifact Instance Ref 与获准 Payload 读取 analysis results、Findings、Evidence、`privacy` 和 `limitations` 做展示，不重算；可视化 Handoff 必须释放隐私门禁和限制。

交给 Evidence Govern 时，请求必须绑定完整 Artifact Instance Ref、正式 Handoff 和绝对 `payload_refs[]`；对象 ID 只用于包内关联。
- `knowledge-wiki`：只有 `evidence-govern` 放行或用户明确发起候选审阅时读取 `knowledge_candidates`。
- `outcome-validation-recheck`：具备根因和干预契约时读取 `analysis_results.comparison`，再判断正式效果。
- `evidence-archive`：仅满足归档治理门禁时归档正式包。

写出正式产物后运行 `node shared-workflow/generate-progress-preview.js`。会话内输出：

```html
<!-- spark-context:subjective-feedback-analysis ref="spark-output/results/subjective/ 与 spark-output/context/current/subjective.json" -->
主观反馈分析已完成：project=[project_name]，有效反馈=[N]，主题=[M]，正式证据=[K]，状态=[status]
<!-- /spark-context:subjective-feedback-analysis -->
```

## 自检

- 输入是否只来自用户本轮提供、授权或明确引用的正式上下文？
- 是否先脱敏再分析，所有 quote 是否只有脱敏文本？
- 是否说明样本分母、去重口径、渠道偏差和限制？
- 是否保留 Findings 与 Evidence 的门禁？
- 是否避免真实发生率、最终根因、客观影响规模和效果结论？
- 报错是否保持 `reported_error`，没有误标系统日志或已验证 Bug？
- 工单分类是否允许多标签、不静默删除不确定项？
- 知识候选是否需要人工复核且没有自动入库？
- comparison 是否只描述样本内变化？
- 下游是否只按允许用途读取？
- 两份 Schema、核心校验、报告和 preview 是否通过？

## 硬边界

- 不读取或分析原始埋点、漏斗、路径、性能和系统日志。
- 不输出真实发生率、真实影响人数、最终根因、方案效果、产品排期或投入产出比。
- 不自动发布知识、客服话术、引导文案或 Knowledge Wiki patch。
- 不在正式产物中保存未脱敏原文、个人名、个人账号 ID、工单号或其他个人/凭证敏感标识。企业编号和企业名称可作为获授权的关联、分群字段保留，但不得因此扩大授权范围或对外披露。
- 不把归档、展示、知识候选或 Business Impact 读取视为证据放行。
- 不创建独立子技能包、持久 run 目录、Profile Registry 或第二份结构化事实源。
