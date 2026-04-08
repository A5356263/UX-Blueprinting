# Gate / Check 正式规范（兼容 UX-Blueprinting 现有执行链路）

## 1. 目标

本规范定义 UX-Blueprinting 项目中 `gate` 与 `check` 的正式职责、检查维度、状态语义、产物格式与实现约束。

本规范面向：

- `packages/validate/core.py`
- 各阶段 gate 执行逻辑
- `check_report.md` / `check_status.json` 生成逻辑
- 后续与 `task_card_resolved.json`、`context_manifest.json`、阶段合同、模板的联动实现

本规范的目标不是新增一条并行主链路，而是在当前仓库既有执行中枢上，升级 gate / check 的检查深度，使其能够消费已经升级后的 `08/09/10` 合同与三份模板，而不是继续停留在“栏目完整即可通过”的旧校验模式。

---

## 2. 适用范围

本规范适用于以下现有主链路：

- `facts` 阶段 gate
- `business` 阶段 gate
- `experience` 阶段 gate
- 最终 `validate`
- 最终 `coverage`

本规范默认兼容当前仓库中的以下基线：

- 执行中枢由步骤化流程推进，且统一使用 `pending / running / passed / warning / failed` 状态语义。
- `task_card.md` 解析后生成 `runtime/task_card_resolved.json`。
- 上下文装配后生成 `runtime/context_manifest.json`，且当前实现允许目录级知识引用，但会产生 warning。
- 最终正式检查仍输出 `workspace/check_report.md` 与 `workspace/check_status.json`。

---

## 3. 现有仓库基线（本规范对齐对象）

当前执行中枢规格已定义：执行中枢负责目录、协议解析、装配、校验、状态、归档；AI 推理负责事实提炼、业务判断、体验推导与 `[GAP] / [CONFLICT]` 的语义处理，且 Step 6 Validation 的目标是“检查输出结构、阶段边界与事实承接情况” fileciteturn34file0。

当前 `task_card.md` / `task_card_resolved.json` 仍将 `facts.md`、`business_blueprint.md`、`experience_blueprint.md`、`gap_list.md`、`check_report.md`、`check_status.json` 作为标准输出，并把 `specs/06/08/09/10` 作为检查依据 fileciteturn44file2 fileciteturn34file1。

当前 `context_manifest.json` 已明确暴露：知识引用中存在目录级引用，系统会记录 warning，提示应尽量收窄到文件或索引页 fileciteturn34file2。

当前 `packages/validate/core.py` 的实现仍以硬编码栏目、简单禁词、占位符检查、事实 ID 引用和原则 ID 引用为主；这说明现有 gate / check 仍偏“结构检查”，尚未升级为“深度检查”与“跨阶段一致性检查” fileciteturn32file0。

---

## 4. 术语定义

### 4.1 Gate

`gate` 是阶段性准入检查。

其目标是判断：

- 当前阶段产物是否合格
- 是否允许进入下一阶段
- 若允许进入，带着怎样的 warning 进入

`gate` 不负责替代下一阶段推理；它负责“准入执法”。

### 4.2 Check

`check` 是最终正式检查。

其目标是判断：

- 全部标准产物是否齐全
- 各阶段是否相互承接
- 机器状态与 Markdown 报告是否一致
- 是否满足归档前的正式出库条件

### 4.3 Coverage

`coverage` 是跨阶段承接覆盖检查。

其目标是判断：

- facts 是否被 business / experience 承接
- business judgment 是否被 experience 消费
- experience 页面与任务流是否有业务来源

### 4.4 Blocker / Warning / Info

- `blocker`：必须阻断当前阶段或最终通过
- `warning`：允许继续，但必须显式暴露
- `info`：记录执行事实或统计信息，不影响通过与否

---

## 5. 总体设计原则

### 5.1 先读合同与模板，再检查产物

gate / check 的栏目、格式、边界与深度要求，必须来自：

- `specs/08_fact_extraction_contract.md`
- `specs/09_business_blueprint_contract.md`
- `specs/10_experience_blueprint_contract.md`
- 当前生效模板

禁止继续只依赖 `core.py` 内硬编码标题作为唯一标准。

### 5.2 结构检查只是最低层，不得等同于合格

以下检查都属于最低层：

- 文件存在
- 标题存在
- 占位符已替换
- 禁词未出现

仅满足以上条件，不得直接判定为 `passed`。

### 5.3 Gate 检查“阶段是否成立”，Check 检查“整条链路是否成立”

- facts gate：检查 facts 是否可作为 business 输入
- business gate：检查 business 是否可作为 experience 输入
- experience gate：检查 experience 是否可进入正式检查
- final check：检查整条链路是否达到归档条件

### 5.4 不以固定事实条数为跨域硬标准

本项目未来将接入多业务域知识库，因此 gate / check 不得把“事实条数 >= N”作为唯一或核心判定条件。

更稳妥的检查对象应是：

- 维度覆盖
- 结构粒度
- 追溯关系
- 决策质量
- 页面级可消费程度

### 5.5 知识库在 facts 阶段只能做校准，不得伪装成输入事实

facts gate 必须区分：

- 来自输入材料的事实
- 来自引用知识的术语/边界校准
- 仍未确认的 gap

如果 facts 产物把知识库中未在输入中出现的结论直接写成“已确认事实”，应判定为 blocker。

---

## 6. 统一状态与产物要求

### 6.1 统一状态

所有 gate / check 必须复用执行中枢已有状态语义：

- `pending`
- `running`
- `passed`
- `warning`
- `failed`

### 6.2 Gate 产物位置

每个阶段 gate 必须输出：

- `projects/<project-id>/runtime/gates/<stage>_gate_report.md`
- `projects/<project-id>/runtime/gates/<stage>_gate_status.json`

### 6.3 Final Check 产物位置

最终检查必须输出：

- `projects/<project-id>/workspace/check_report.md`
- `projects/<project-id>/workspace/check_status.json`

### 6.4 机器状态最小字段

所有 `*_status.json` 至少应包含：

- `project_id` 或 `task_id`
- `stage`（对于 gate）
- `status`
- `can_proceed`（对于 gate）
- `generated_by`
- `updated_at`
- `blocker_count`
- `warning_count`
- `info_count`
- `issues.blockers`
- `issues.warnings`
- `issues.infos`
- `checked_files`
- `metrics`（新增，详见第 12 节）

### 6.5 Markdown 报告最小结构

所有 gate report 至少应包含：

- `## Summary`
- `## Checked Files`
- `## Blockers`
- `## Warnings`
- `## Infos`

最终 `check_report.md` 至少应包含：

- `## Summary`
- `## Output Status`
- `## Blockers`
- `## Warnings`
- `## Infos`
- `## Coverage Check`
- `## Machine Status`

---

## 7. Gate / Check 的通用检查维度

以下维度适用于所有阶段：

### 7.1 文件存在性

检查目标：

- 当前阶段所需上游输入是否存在
- 当前阶段正式产物是否存在
- 所需 gate 状态文件是否存在

判定：

- 缺任一必需文件：`blocker`

### 7.2 栏目完整性

检查目标：

- 当前产物是否满足当前生效合同与模板要求的栏目

判定：

- 缺关键栏目：`blocker`
- 缺非关键辅助栏目：`warning`

### 7.3 占位符清理

检查目标：

- 是否仍含 `<填写...>`、`{{TASK_ID}}`、`<project-id>` 等占位内容

判定：

- 关键栏目保留占位：`blocker`
- 非关键注释位保留占位：`warning`

### 7.4 阶段边界检查

检查目标：

- facts 不得越权进入 business judgment / experience architecture / implementation
- business 不得越权进入 visual design / implementation
- experience 不得越权进入 database / API / SQL / component implementation

判定：

- 明显越权且影响主输出语义：`blocker`
- 轻微越权表述：`warning`

### 7.5 追溯关系检查

检查目标：

- 当前阶段关键结论是否能追溯到上游阶段或显式引用知识

判定：

- 主结论无法追溯：`blocker`
- 少量次级结论追溯不清：`warning`

### 7.6 深度检查

检查目标：

- 产物是否只停留在摘要级表述
- 是否具备当前阶段要求的结构单元、矩阵、映射、表格、流程、区块示意等

判定：

- 仅有概述，缺关键结构单元：`blocker`
- 结构单元存在但粒度偏粗：`warning`

### 7.7 Gap 暴露检查

检查目标：

- 依赖未确认信息的地方，是否显式保留 `[GAP]` / 开放问题 / 缺口项

判定：

- 关键不确定性未暴露却被写成确定结论：`blocker`
- 非关键缺口未整理：`warning`

### 7.8 一致性检查

检查目标：

- Markdown 报告与 JSON 状态是否一致
- `status` 与 `blocker/warning` 数量是否一致
- `can_proceed` 与 `status` 是否一致

判定：

- 机器状态与报告冲突：`blocker`

---

## 8. Facts Gate 规范

### 8.1 准入前提

facts gate 前必须已有：

- `source/task_card.md`
- `source/requirement.md`
- `source/background.md`
- `runtime/task_card_resolved.json`
- `runtime/context_manifest.json`
- `workspace/facts.md`

### 8.2 Facts Gate 必查项

#### A. 输入与协议完整性

必须检查：

- `task_card.md`、`task_card_resolved.json`、`context_manifest.json` 是否存在
- `task_card_resolved.json` 是否可解析出当前任务的 inputs / outputs / checks / templates

#### B. 事实来源合法性

必须检查：

- facts 中主事实是否来源于输入材料
- 若使用知识库，是否只用于术语校准、边界校准、冲突识别、gap 分类
- 是否把知识库补写内容伪装成输入已确认事实

判定：

- 伪造输入事实：`blocker`
- 来源引用不够明确：`warning`

#### C. 原子事实粒度

facts 必须包含足以支持后续 business 推理的结构化事实单元。

推荐检查维度：

- actor（角色）
- object（对象）
- state（状态）
- action（动作）
- rule（规则）
- exception（异常）
- dependency（依赖）
- scope（范围）
- gap（缺口）

判定：

- 只有高层摘要，没有足够结构化事实单元：`blocker`
- 维度覆盖不完整，但主链路仍可推导：`warning`

#### D. 事实追溯

每个关键 facts block 应能追溯到：

- 输入原文片段
- 或显式引用知识页

若 facts 采用 ID 化表达，则 gate 应检查：

- 是否存在事实 ID
- 是否存在事实来源说明或 trace section

判定：

- 无法追溯关键事实：`blocker`
- facts 存在但来源说明偏弱：`warning`

#### E. 阶段边界

facts 不得输出：

- business final position（业务最终立场）
- solution evaluation（方案评审）
- experience architecture（体验架构）
- visual layout（视觉布局）
- implementation design（实现方案）

#### F. Gap 处理

必须检查：

- 输入不足位置是否显式保留开放问题或 `[GAP]`
- 是否把未知项硬写成事实

### 8.3 Facts Gate 通过条件

只有在以下条件同时满足时，facts gate 才能 `passed`：

- facts 文件存在且结构合格
- 事实来源合法
- 已达到原子事实粒度下限
- 不确定项已显式暴露
- 未越权到 business / experience / implementation

### 8.4 Facts Gate Warning 条件

以下情况允许 `warning` 通过：

- facts 已可支持 business 推理，但部分维度粒度偏粗
- 来源路径已列出，但部分事实未精确 trace 到原文片段
- knowledge 仍为目录级引用，尚未细化到索引页或文件

### 8.5 Facts Gate Blocker 条件

- 缺少任一必需输入或 facts.md
- facts 主要内容来自推断而非输入
- 关键事实无法支撑后续 business 判断
- 明显越权
- 关键 gap 未暴露

---

## 9. Business Gate 规范

### 9.1 准入前提

business gate 前必须已有：

- 通过或带 warning 通过的 facts gate 结果
- `workspace/facts.md`
- `workspace/business_blueprint.md`

### 9.2 Business Gate 必查项

#### A. 上游 gate 状态

必须检查：

- `facts_gate_status.json` 是否存在
- facts gate 是否为 `failed`

判定：

- facts gate 失败仍继续：`blocker`

#### B. 业务蓝图不是 facts 改写版

必须检查：

- business 是否在 facts 基础上形成业务判断
- 是否存在独立的 review layer（审视层）内容，而不是仅摘要重写 facts

#### C. 核心判断维度

business 必须检查并表达以下判断维度（名称可随合同调整，但语义不得缺失）：

- goal fit（是否服务任务核心目标）
- domain logic fit（是否符合领域底层逻辑）
- management strategy fit（是否符合管理策略）
- value / cost ratio（价值与认知/培训/维护成本比）
- capability placement（应独立 / 合并 / 不做 / 作为配置项）
- anti-pattern check（是否功能堆砌、绕过治理、徒增复杂度）

判定：

- 缺少主判断框架：`blocker`
- 存在判断，但只有部分维度：`warning`

#### D. 结论追溯

每个关键业务判断必须追溯到：

- facts
- 或任务显式引用知识 / wiki

若存在“最终立场 / 推荐方案 / 不建议方案”，则必须有对应依据。

#### E. 冲突与缺口处理

如果业务判断依赖未确认信息，必须显式保留：

- `[GAP]`
- 开放问题
- 或“待确认后再裁决”的条件语句

#### F. 阶段边界

business 不得直接输出：

- 页面 IA 细节
- 页面区块布局
- 组件级交互稿
- 高保真视觉方案
- 技术实现细节

### 9.3 Business Gate 通过条件

只有在以下条件同时满足时，business gate 才能 `passed`：

- facts gate 已通过或 warning 通过
- business 已形成清晰业务判断
- 判断能追溯到 facts / 引用知识
- 已表达必要的方案合理性、边界与取舍
- 未越权到 experience / implementation

### 9.4 Business Gate Warning 条件

- 主判断已成立，但部分维度未展开
- facts 承接充分，但 options compare 或 anti-pattern 偏粗
- 仍有少量非主链路 gap 未决

### 9.5 Business Gate Blocker 条件

- 缺 business_blueprint.md
- facts gate 未通过
- business 只是在改写 facts
- 关键业务判断无依据
- 结论依赖未知条件却未暴露

---

## 10. Experience Gate 规范

### 10.1 准入前提

experience gate 前必须已有：

- 通过或带 warning 通过的 business gate 结果
- `workspace/facts.md`
- `workspace/business_blueprint.md`
- `workspace/experience_blueprint.md`

### 10.2 Experience Gate 必查项

#### A. 上游 gate 状态

必须检查：

- `business_gate_status.json` 是否存在
- business gate 是否为 `failed`

#### B. 体验蓝图已进入 UI-ready blueprint 粒度

experience 不得只停留在抽象体验原则。必须达到可进入 UI 规划的蓝图粒度。

至少应覆盖以下结构单元中的主要部分（具体栏目名可随合同更新，但语义不可缺失）：

- IA（信息架构）
- task flow（任务流）
- page / window inventory（页面 / 窗口清单）
- page-region layout（页面区块布局）
- state & feedback matrix（状态与反馈矩阵）
- content / copy contract（内容 / 文案合同）

判定：

- 仍然只有抽象体验要求：`blocker`
- 已进入页面级，但仍偏粗：`warning`

#### C. 非纯文案要求

experience 应允许并鼓励使用：

- 表格
- 文本流程图
- ASCII / 文本结构图
- 页面区块示意

gate 必须检查：

- 是否只有大段纯文案，导致页面消费性不足

判定：

- 缺少任何结构化展示方式，无法支撑后续 UI 讨论：`warning`
- 严重缺少页面级结构信息：`blocker`

#### D. 体验承接关系

experience 的页面、任务流、文案策略必须追溯到：

- business judgment
- facts
- 设计原则 / 设计指南

若页面级安排无法说明“为什么这样组织”，应视为承接不足。

#### E. 文案与解释合理性

必须检查：

- 关键状态是否有对应反馈文案
- 关键阻断点是否有解释文案
- 页面主任务是否有清晰主标题 / 次说明 / 空状态 / 错误反馈
- 是否存在容易引起歧义、误解治理规则、误判结果状态的文案

#### F. 阶段边界

experience 可以做到：

- UI-ready blueprint（可进入 UI）
- 页面区块与内容合同
- 信息优先级和交互说明

experience 不得直接输出：

- 高保真视觉参数
- 颜色、像素、品牌样式规范
- React / Vue / Flutter 组件实现
- API 字段 / SQL / 数据库表结构

### 10.3 Experience Gate 通过条件

只有在以下条件同时满足时，experience gate 才能 `passed`：

- business gate 已通过或 warning 通过
- experience 已达到页面级 / 任务流级 / 文案级可消费粒度
- 已显式引用或承接 business judgment 与设计原则
- 页面组织、反馈与文案解释具有可讨论性
- 未越权到视觉高保真或实现层

### 10.4 Experience Gate Warning 条件

- 页面级结构已成立，但部分窗口或状态仍偏粗
- 文案策略已列出，但个别关键状态未完整覆盖
- 结构化表达存在，但图表/表格不足

### 10.5 Experience Gate Blocker 条件

- 缺 experience_blueprint.md
- business gate 未通过
- experience 仍是抽象体验原则稿
- 页面 / 状态 / 文案无法承接业务判断
- 明显越权到实现层

---

## 11. Final Validate / Coverage 规范

### 11.1 Final Validate（最终正式检查）

最终 validate 必须检查：

#### A. 标准输出齐全

必须以 `task_card_resolved.json.required_outputs` 为准检查正式产物是否齐全，而不是只依赖硬编码输出列表。

#### B. 报告与机器状态一致

必须检查：

- `check_report.md` 与 `check_status.json` 是否同时存在
- `status`、`blocker_count`、`warning_count`、`info_count` 是否一致
- `issues` 与 Markdown 列表是否一致

#### C. 三阶段边界一致

必须检查：

- facts / business / experience 是否分别满足各自阶段边界
- 最终报告不得掩盖任何 blocker

### 11.2 Coverage（跨阶段承接覆盖）

最终 coverage 不应只检查“facts ID 是否被引用”，还必须增加：

#### A. Facts → Business 承接覆盖

检查目标：

- 关键 facts 是否在 business 中被消费
- facts 是否被转换成规则、边界、判断或风险，而不是只被字符串提及

#### B. Business → Experience 承接覆盖

检查目标：

- business judgment 是否映射到 experience 的页面、任务流、状态、文案或保护策略
- 不能只出现“原则 ID 被引用”，还应看到页面级消费

#### C. Experience → Page-level Consume 覆盖

检查目标：

- 页面清单、区块、反馈、文案是否形成闭环
- 是否存在“提了体验目标，但没有落到页面”

#### D. Orphan 检查

检查目标：

- orphan fact：facts 中关键事实未被后续消费
- orphan judgment：business 中关键判断未被 experience 消费
- orphan page：experience 中新增页面 / 窗口无业务来源

### 11.3 Final Check 通过条件

最终 check 只能在以下条件同时满足时 `passed`：

- required outputs 齐全
- report / status 一致
- 无 blocker
- coverage 不存在关键 orphan
- 各阶段主要结构单元可被后续消费

---

## 12. 建议新增的 Metrics（机器可读指标）

为避免 gate / check 继续停留在字符串规则层，建议在每个阶段状态 JSON 中新增 `metrics` 字段。

### 12.1 Facts Metrics

建议包含：

- `fact_count`
- `dimension_coverage.actor`
- `dimension_coverage.object`
- `dimension_coverage.state`
- `dimension_coverage.action`
- `dimension_coverage.rule`
- `dimension_coverage.exception`
- `dimension_coverage.dependency`
- `dimension_coverage.scope`
- `traceable_fact_count`
- `gap_count`
- `knowledge_derived_fact_count`

### 12.2 Business Metrics

建议包含：

- `judgment_count`
- `facts_consumed_count`
- `judgment_traceable_count`
- `option_compare_count`
- `anti_pattern_count`
- `unresolved_gap_count`

### 12.3 Experience Metrics

建议包含：

- `flow_count`
- `page_count`
- `window_count`
- `region_map_count`
- `state_feedback_pair_count`
- `copy_contract_item_count`
- `business_judgment_consumed_count`
- `principle_ref_count`

### 12.4 Final Coverage Metrics

建议包含：

- `facts_covered_by_business`
- `facts_covered_by_experience`
- `business_judgments_consumed_by_experience`
- `orphan_fact_count`
- `orphan_judgment_count`
- `orphan_page_count`

---

## 13. 严重级别判定规则

### 13.1 Blocker

以下情况原则上必须定为 `blocker`：

- 缺少必需输入或正式输出
- 当前阶段关键栏目缺失
- 主结论无法追溯
- 关键 gap 被伪装成已确认结论
- 上游 gate 失败仍进入下游阶段
- 报告与机器状态冲突
- 主链路结构深度不足，导致下一阶段无法稳定消费

### 13.2 Warning

以下情况可定为 `warning`：

- 结构已成立但粒度偏粗
- 部分 trace 不够精确
- 目录级知识引用未收窄
- 文本图 / 表格 / 矩阵表达不足
- 存在次级 orphan，但不阻断主链路

### 13.3 Info

适合作为 `info` 的内容：

- 已提炼事实数量
- 已承接事实数量
- 已引用原则数量
- 已生成页面数量
- 已检查输出文件列表

---

## 14. 对 `packages/validate/core.py` 的实施要求

### 14.1 禁止继续只靠硬编码标题表执法

当前 `core.py` 中的：

- `REQUIRED_HEADINGS`
- `FORBIDDEN_TERMS`
- `TRACKED_OUTPUTS`

只能作为过渡期兜底，不应继续作为唯一真源 fileciteturn32file0。

正式实现应改为：

- 优先从阶段合同 / 配置读取当前阶段要求
- 若读取失败，再回退到最小兜底规则

### 14.2 Coverage 逻辑必须升级

当前 coverage 主要看 facts ID 是否在 business / experience 中出现，仍属于字符串覆盖，不足以反映业务承接深度 fileciteturn32file0。

正式实现应至少补：

- facts → judgment 映射
- judgment → page / flow / copy 映射
- orphan 检查

### 14.3 Gate Status 必须输出 Metrics

每个 gate 的 JSON 状态必须补充 `metrics`，否则系统无法区分：

- 真正深度合格
- 只是标题齐全

### 14.4 Final Validate 必须以 `task_card_resolved.json` 为准

正式实现应从 `task_card_resolved.json.required_outputs` 读取标准输出，而不是只校验固定的六个文件名。

---

## 15. 与 Task Card / Context Manifest 的联动要求

### 15.1 Task Card 联动

如果后续 `task_card.md` 增加以下字段，gate / check 应支持消费：

- 每阶段输出粒度要求
- 每阶段知识使用边界
- 体验阶段是否强制表格 / 文本图 / 区块示意
- 是否要求 option compare / anti-pattern check

### 15.2 Context Manifest 联动

gate / check 应读取 `context_manifest.json` 的引用信息，并至少支持：

- 目录级知识引用 warning
- 缺少关键索引页 warning
- 引用路径丢失 blocker

---

## 16. 迁移顺序建议

建议按以下顺序落地：

1. 先改 `packages/validate/core.py` 的结构模型
2. 再改 facts / business / experience 三个 gate 的具体检查逻辑
3. 再改 final validate / coverage
4. 最后补 task card / context manifest 的可选扩展字段

原因：

- 你已经先升级了 `08/09/10` 合同与模板
- 现在最短板是 gate / check 仍按旧标准执法
- 若不先升级 gate / check，新的合同与模板仍会被旧校验逻辑压回浅输出

---

## 17. 最终结论

本项目下一阶段的重点，不再是继续扩写阶段 spec，而是把 gate / check 从“结构与字符串引用检查器”升级成“阶段准入与链路一致性检查器”。

正式执法标准应变为：

- facts gate：检查事实是否真实、结构化、可支撑 business
- business gate：检查业务判断是否成立、是否有依据、是否不是摘要重写
- experience gate：检查体验蓝图是否真正进入页面 / 流程 / 文案层
- final check：检查整条链路是否齐全、一致、可归档

只有这样，前面你已经升级过的 `08 / 09 / 10` 合同与三份模板，才会真正被系统消费，而不会继续被旧检查逻辑稀释。
