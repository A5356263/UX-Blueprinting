# UX-Blueprinting 通用规范升级草案
## Facts（事实层）与 Business Blueprint（业务蓝图层）V2 正式规范

## 1. 文档定位

本规范用于把当前 `facts -> business_blueprint -> experience_blueprint` 主链路，从“摘要传递”升级为“可编译的结构化推理链路”。

本规范是通用规范，不绑定权限域；权限域仅作为已验证样例。后续接入新的业务知识库时，应沿用本规范，只替换领域知识与领域词表，不替换阶段职责。

本规范同时约束：

- `specs/`：阶段合同与执行法典
- `templates/`：输出模板
- `packages/`：执行、gate、validate、coverage 的固定逻辑
- `projects/`：项目真相层产物结构
- `knowledge/`：知识引用方式与校准方式
- `docs/`：runbook 与外部执行说明

## 2. 背景问题

当前仓库已完成主架构：任务协议、上下文装配、执行中枢、检查与归档链路基本成立。但现阶段输出仍存在以下共性问题：

1. `facts.md` 倾向于主题摘要，而非业务编译单元提取。
2. `business_blueprint.md` 倾向于事实重述，而非业务合理性审视。
3. gate 与 validate 当前主要检查“结构完整”和“事实承接”，尚未检查“编译深度”。
4. task card 与 context assembly 已支持 Knowledge / Wiki / Templates / Checks 显式引用，但知识仍以目录级引用为主，缺少更窄的消费边界。
5. 模板头部与检查器约束过粗，导致“写得浅但格式正确”的结果可以通过。

## 3. 核心升级目标

本轮升级的目标不是增加篇幅，而是提升阶段分辨率。

### 3.1 Facts（事实层）V2 的目标

Facts（事实层）必须从“摘要层”升级为“Structured Extraction Layer（结构化提取层）”。

它回答：

- 输入里已经确认了什么
- 这些确认信息分别属于哪个业务维度
- 哪些内容仍然缺失，不能被推断
- 哪些内容需要被后续阶段继续消费

Facts（事实层）不负责：

- 做业务合理性判断
- 做方案取舍
- 做体验转译
- 用知识库补写输入里不存在的事实

### 3.2 Business Blueprint（业务蓝图层）V2 的目标

Business Blueprint（业务蓝图层）必须从“业务总结层”升级为“Business Review Layer（业务审视层）”。

它回答：

- 一个新增业务 / 功能在业务上是否成立
- 它是否符合底层业务逻辑与治理逻辑
- 它是否只是功能堆砌
- 它应该独立、合并、降级为配置项，还是不应新增
- 它带来的价值是否大于治理、认知、培训与维护成本

Business Blueprint（业务蓝图层）不负责：

- 重新发明事实
- 直接给出页面方案
- 输出视觉设计或实现设计

## 4. 总体原则

### 4.1 输入优先原则

Facts（事实层）以原始输入为主，知识库为辅。

- 原始需求文档、背景文档、附件，是 facts 的主数据源。
- Wiki（维基）与 Knowledge（知识库）在 facts 阶段只承担“术语校准、边界校准、冲突校准、缺口识别”职责。
- Facts 阶段不得把知识库中的通用规则，伪装成当前任务已确认事实。

### 4.2 校准而非补写原则

知识库在 facts 阶段的角色是校准器，不是补写器。

### 4.3 编译单元优先原则

阶段输出必须以“最小可消费单元”组织，而不能只按主题摘要组织。

### 4.4 Gap（缺口）保留原则

当输入不足时，必须显式产出 gap，而不是在 facts 或 business 阶段用经验补齐。

### 4.5 通用主线 + 领域覆盖原则

主线合同保持通用，领域差异通过以下方式注入：

- 领域 Wiki（维基索引）
- 领域知识包
- 领域词表 / 状态词典 / 角色词典
- 领域特定 gate 规则扩展

## 5. Facts（事实层）V2 正式规范

## 5.1 阶段定义

Facts（事实层）V2 是“面向后续业务与体验消费的原子业务信息提取阶段”。

输出必须能直接支撑：

- business judgment（业务判断）
- rule analysis（规则分析）
- state analysis（状态分析）
- actor / object / action mapping（角色 / 对象 / 动作映射）
- exception tracing（异常追踪）

## 5.2 Facts（事实层）V2 的输入

强制输入：

- `projects/<project-id>/source/task_card.md`
- `projects/<project-id>/source/requirement.md`
- `projects/<project-id>/source/background.md`
- `projects/<project-id>/runtime/task_card_resolved.json`
- `projects/<project-id>/runtime/context_manifest.json`

可选输入：

- `projects/<project-id>/source/attachments/`
- task card 中显式引用的 wiki / knowledge / templates / checks

## 5.3 Facts（事实层）V2 的知识使用边界

### 允许使用知识库做的事

1. 统一术语
2. 判断输入中的表达属于哪个业务维度
3. 识别输入是否与现有域定义冲突
4. 识别输入是否缺少关键业务位
5. 识别哪些内容应标记为 gap

### 禁止使用知识库做的事

1. 把知识库里的通用逻辑直接写成当前任务事实
2. 替业务阶段提前下结论
3. 用行业常识自动补全未确认信息
4. 把 wiki 或知识的默认策略伪装成需求显式要求

## 5.4 Facts（事实层）V2 的最小提取单元

Facts 不再只输出主题事实，而必须输出 Atomic Fact（原子事实）。

每条 Atomic Fact（原子事实）只表达一个明确结论，并能归入以下维度之一：

- Actor Fact（角色事实）
- Object Fact（对象事实）
- State Fact（状态事实）
- Action Fact（动作事实）
- Rule Fact（规则事实）
- Constraint Fact（约束事实）
- Exception Fact（异常事实）
- Dependency Fact（依赖事实）
- Scope Fact（范围事实）
- Evidence Fact（证据事实，例如调研与竞品）

## 5.5 Facts（事实层）V2 强制输出结构

`facts.md` 必须包含以下栏目：

- `## 任务目标`
- `## 输入摘要`
- `## 角色地图`
- `## 对象模型`
- `## 状态模型`
- `## 动作与流程事实`
- `## 规则矩阵`
- `## 已知约束`
- `## 异常与失败场景`
- `## 依赖与外部系统`
- `## 范围与边界`
- `## 证据与来源`
- `## 开放问题`
- `## 追踪映射`

其中：

### 角色地图
列出参与者、权限边界、可见动作、不可见动作。

### 对象模型
列出业务对象及对象关系，例如“申请单、权限项、角色、组织、审批流、通知”等。

### 状态模型
列出与当前需求直接相关的业务状态，而不是抽象写“有状态流转”。

### 动作与流程事实
按动作拆解，而不是按页面拆解。

### 规则矩阵
至少包含：

- 规则 ID
- 触发条件
- 适用对象
- 判定逻辑
- 结果
- 来源
- 是否已确认

### 异常与失败场景
单独列出失败触发条件、拦截原因、报错语义、待确认异常。

### 追踪映射
要求 facts 内的每条核心事实能追溯到：

- requirement 原文片段
- background 原文片段
- 附件或引用知识的校准位置

## 5.6 Facts（事实层）V2 的产出粒度要求

在一般复杂度任务中，facts 的有效编译规模不应只有 10 余条高层摘要。

推荐基线：

- 简单任务：20–40 条原子事实
- 中等任务：40–80 条原子事实
- 复杂任务：80 条以上原子事实，并配套规则矩阵与状态矩阵

## 5.7 Facts（事实层）V2 的质量判定

一个合格的 `facts.md` 必须满足：

1. 事实可追溯
2. 事实粒度可消费
3. 关键角色、对象、状态、动作、规则、异常已显式拆开
4. 缺口已显式保留
5. 没有提前进入业务判断
6. 没有把知识校准内容伪装成任务事实

## 6. Business Blueprint（业务蓝图层）V2 正式规范

## 6.1 阶段定义

Business Blueprint（业务蓝图层）V2 是“面向需求合理性评审的业务审视阶段”。

它不是简单总结，而是对新增需求进行：

- 合理性审查
- 归位判断
- 取舍分析
- 管理策略对齐
- 价值 / 成本评估

## 6.2 Business Blueprint（业务蓝图层）V2 的输入

强制输入：

- `projects/<project-id>/workspace/facts.md`
- task card 中显式引用的 wiki
- task card 中显式引用的 business knowledge
- task card 中显式引用的 check spec

Business Blueprint 必须建立在 facts 之上；不得绕过 facts 直接从 requirement 重写一版总结。

## 6.3 Business Blueprint（业务蓝图层）V2 的核心判断任务

Business Blueprint 至少要回答以下问题：

1. 这个需求的业务目标是否成立
2. 这个需求是否符合领域底层逻辑
3. 这个需求是否符合基本治理策略
4. 这个需求是否只是功能堆砌
5. 这个需求应独立、合并、降级，还是不做
6. 它带来的业务价值是否大于治理成本与认知成本
7. 它是否会破坏既有职责边界、授权边界、审批边界或审计边界

## 6.4 Business Blueprint（业务蓝图层）V2 的强制评估维度

`business_blueprint.md` 必须显式包含以下评估维度：

- Goal Fit（目标匹配）
- Domain Logic Fit（领域逻辑匹配）
- Management Strategy Fit（管理策略匹配）
- Capability Placement（能力归位）
- Value / Cost Ratio（价值成本比）
- Risk and Anti-pattern Check（风险与反模式检查）
- Final Position（最终立场）

### 目标匹配
判断该新增是否服务核心目标，而不是只回应表层诉求。

### 领域逻辑匹配
判断是否违背领域底层运行逻辑。

### 管理策略匹配
判断是否违背集中治理、授权闭环、审批闭环、审计留痕、分级职责等策略。

### 能力归位
判断该需求是：

- 新独立能力
- 现有能力扩展
- 配置项
- 规则项
- 不建议新增

### 价值成本比
至少同时评估：

- 业务价值
- 认知成本
- 培训成本
- 治理成本
- 维护成本

### 风险与反模式检查
至少检查：

- Feature Bloat（功能堆砌）
- Policy Bypass（绕过治理）
- Layer Violation（层级错位）
- Mental Burden Without Payoff（增加认知负担但收益不足）
- Duplicate Capability（重复能力）

### 最终立场
必须给出清晰立场，而不是只罗列信息：

- 建议做
- 建议做，但需收缩边界
- 建议合并到现有能力
- 建议作为规则或配置承载
- 当前不建议做
- 暂缓，等待 gap 补齐

## 6.5 Business Blueprint（业务蓝图层）V2 强制输出结构

`business_blueprint.md` 必须包含以下栏目：

- `## 业务目标复述`
- `## 领域基线`
- `## 核心业务判断`
- `## 治理与管理策略检查`
- `## 能力归位判断`
- `## 方案取舍与对比`
- `## 价值与成本评估`
- `## 风险与反模式`
- `## 最终立场`
- `## 需要补齐的业务缺口`
- `## 引用事实与引用知识`

## 6.6 Business Blueprint（业务蓝图层）V2 的引用要求

Business Blueprint 必须显式引用：

- Facts ID
- 知识来源
- 使用这些知识的目的：术语对齐、边界判断、治理判断、历史策略对齐，或反模式识别

## 6.7 Business Blueprint（业务蓝图层）V2 的输出标准

一个合格的 `business_blueprint.md` 必须满足：

1. 能看出“做不做、怎么做、放哪里做”的立场
2. 能解释为什么该立场成立
3. 能显式暴露风险、代价与反模式
4. 能帮助体验设计师与产品讨论需求合理性
5. 不越权进入页面结构、交互细节或视觉实现

## 7. 其他模块的同步升级要求

本轮升级不能只改 `specs/`，还必须同步改以下模块。

## 7.1 Task Card（任务卡）协议同步项

`task_card.md` / `task_card_resolved.json` 需新增或收紧：

- `domain_glossary_refs`
- `state_model_refs`
- `role_model_refs`
- `business_policy_refs`
- `anti_pattern_refs`
- `fact_depth_target`
- `business_review_required`

其中：

- `fact_depth_target` 用于声明事实层目标粒度
- `business_review_required` 用于声明业务层必须进行合理性评估，而不只是业务总结

## 7.2 Context Assembly（上下文装配）同步项

`packages assemble` 必须支持把知识引用分层写入 `context_manifest.json`：

- Wiki（默认消费入口）
- Business Knowledge（业务真源）
- Policy Knowledge（策略知识）
- Glossary（词表）
- Template（模板）
- Check Spec（检查规格）

并在 manifest 中标记：

- 是否目录级引用
- 是否建议缩窄到文件级引用
- 被哪个阶段消费

## 7.3 Templates（模板）同步项

必须重写以下模板：

- `templates/facts.template.md`
- `templates/business_blueprint.template.md`
- `templates/check_report.template.md`
- 必要时新增 `templates/facts_rule_matrix.template.md`
- 必要时新增 `templates/business_review_notes.template.md`

模板必须从“章节占位模板”升级为“结构化编译模板”。

## 7.4 Validate / Coverage / Gate（检查与闸门）同步项

当前 `packages/validate/core.py` 主要检查栏目、越权词与事实 ID 承接，这只能保证结构与浅层承接，无法保证深度。

因此必须新增：

### Facts Gate（事实层闸门）新增检查

- 是否存在角色地图
- 是否存在对象模型
- 是否存在状态模型
- 是否存在规则矩阵
- 是否存在异常清单
- Atomic Fact 数量是否达到 task card 目标
- 核心事实是否具有 trace（追踪映射）
- 是否把知识库内容误写成任务事实

### Business Gate（业务层闸门）新增检查

- 是否显式给出最终立场
- 是否完成能力归位判断
- 是否完成价值 / 成本评估
- 是否完成治理策略检查
- 是否完成反模式检查
- 是否只做了事实重述而没有判断

### Coverage（覆盖检查）新增检查

- 不只检查事实 ID 是否被引用
- 还检查：角色、对象、状态、规则、异常是否被业务层承接
- 检查是否存在“只引用 ID 但未消费语义”的空承接

## 7.5 Projects（项目真相层）同步项

`projects/<project-id>/workspace/` 建议增加或允许以下正式中间产物：

- `facts_rule_matrix.md` 或 `facts_rule_matrix.json`
- `facts_state_matrix.md` 或 `facts_state_matrix.json`
- `business_review_notes.md`
- `business_decision_matrix.md`

`runtime/` 建议增加：

- `trace_index.json`
- `knowledge_usage_report.json`
- `gate_metrics.json`

## 7.6 Packages（固定逻辑实现层）同步项

建议在 `packages/` 中新增或扩展以下能力：

- `packages/trace_extract/`：把原文片段与 facts 建立追踪索引
- `packages/knowledge_audit/`：记录知识在各阶段被如何使用
- `packages/gate_metrics/`：输出事实数量、规则数量、状态数量、引用数量等指标
- `packages/coverage/`：从 ID 覆盖升级为语义覆盖

## 7.7 Docs（说明文档层）同步项

以下文档必须同步更新：

- `docs/runbook/task_execution_flow.md`
- `docs/runbook/external_ai_quickstart.md`
- `docs/sdd/` 中涉及 facts / business / check 的说明文档

要求外部执行说明明确：

- facts 阶段以输入提取为主，知识校准为辅
- business 阶段必须做合理性审视，而不只是归纳
- gate 失败时必须回补，不允许直接跳体验阶段

## 8. 建议新增的正式规格文件

建议在 `specs/` 中新增以下文件：

- `specs/08a_fact_depth_contract.md`
- `specs/09a_business_review_contract.md`
- `specs/06a_semantic_coverage_contract.md`
- `specs/04a_knowledge_usage_boundary_contract.md`

其中：

- `08a` 负责定义 facts 的原子粒度与矩阵要求
- `09a` 负责定义 business 的合理性评审维度
- `06a` 负责定义语义覆盖与深度检查
- `04a` 负责定义知识在各阶段的允许用法与禁止用法

## 9. 落地顺序建议

按照仓库现有改造原则，本轮优化建议按以下顺序落地：

1. 先改 `specs/08` 与 `specs/09`
2. 再改 `templates/facts.template.md` 与 `templates/business_blueprint.template.md`
3. 再改 `packages/validate/core.py` 与各 stage gate
4. 再改 `task_card` 协议与 `context_assemble`
5. 再补 `trace_index` 与 `knowledge_usage_report`
6. 最后更新 runbook 与真实项目样例

## 10. 结束判定

当以下条件同时满足时，视为 Facts / Business V2 升级完成：

1. Facts 已从主题摘要升级为原子事实提取
2. Business 已从业务总结升级为业务审视
3. Gate 能检查深度，而不只检查结构
4. Coverage 能检查语义承接，而不只检查 ID 引用
5. Task Card 能表达阶段深度目标与知识边界
6. Context Manifest 能解释知识是如何被各阶段消费的
7. 模板、检查器、运行流与真实项目样例保持一致

## 11. 一句话定义

Facts（事实层）V2：把输入编译成可消费的原子业务事实。  
Business Blueprint（业务蓝图层）V2：基于这些事实，判断一个需求在业务上是否成立、应以什么形态成立。

## 落地顺序：
先改 specs，再改 templates，再改 packages，最后回填 docs 和真实项目样例
