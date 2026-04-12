# P3 正式改造方案：Memory Layer（记忆层）增强设计
**Project:** UX-Blueprinting  
**Document Type:** Formal Enhancement Plan  
**Status:** Proposed  
**Target:** 在不改变现有项目主架构的前提下，为当前执行中枢补齐可复用的 Memory Layer（记忆层）  
**Scope:** P3 only（Memory Layer）  
**Out of Scope:** AI Bridge、外部模型 API、聊天式长期记忆、重型向量数据库平台

---

## 1. 文档目标

本方案用于正式定义 **P3: Memory Layer（记忆层）** 在当前仓库中的改造方式。  
目标不是把系统改造成会话型聊天 agent，也不是把历史任务整篇文档直接塞进知识库，而是在 **现有 `specs / packages / projects / runtime / exports` 骨架** 上，补一层“可复用质量经验沉淀层”。

P3 的核心目的只有一个：

> **让后续任务更稳定地产出高质量业务蓝图与体验蓝图。**

为达成这个目标，P3 必须把“已通过样例、失败模式、项目偏好、能力使用经验”从一次性任务产物中提炼出来，形成跨任务可复用的 memory，而不是依赖：
- 聊天窗口重复解释
- 人工经验口口相传
- AI 每次重新发挥

---

## 2. 当前项目基线判断

当前仓库已经具备以下基础：

- `specs/` 是唯一正式规则真源
- `packages/` 是正式执行中枢
- `projects/<project-id>/` 是项目真相层
- `source / workspace / runtime / exports` 四层项目级分工明确
- 已有 Repair Loop，可结构化暴露失败与修复路径
- 已有 Capability Registry，可显式声明正式能力
- `task_card` 已支持 `Domain` 字段
- `knowledge/wiki/` 是独立 wiki 子系统

这说明当前项目已经具备：
- 规则层
- 检查层
- 修复层
- 能力声明层

但还没有正式的：

> **跨任务质量沉淀层**

也就是现在系统仍缺：

- 哪些高质量模式值得复用
- 哪些失败模式值得提前预警
- 哪些质量偏好属于项目长期偏好
- 哪些 capability 在什么任务类型下经常触发 warning / blocker

---

## 3. P3 设计目标

Memory Layer 需要实现以下 7 个正式目标：

### 3.1 目标一：沉淀“可复用经验”，不是沉淀“整篇文档”
P3 不应把完整的 `facts.md`、`business_blueprint.md`、`experience_blueprint.md` 原样复制为 memory。
P3 应提炼的是：
- pattern（模式）
- failure mode（失败模式）
- preference（偏好）
- capability insight（能力经验）
- review heuristic（审查启发）

### 3.2 目标二：Memory 不耦合 wiki 子系统
`knowledge/wiki/` 在当前仓库里承担长期知识沉淀、跨任务复用、概念统一与上下文压缩，但不替代主链路产物。  
因此 P3 不应直接写入 `knowledge/wiki/`，避免把“任务质量经验系统”与“wiki 知识子系统”耦合。

### 3.3 目标三：长期 memory 与项目级候选 memory 分层
P3 应至少分成两层：
- **长期 memory 子系统**：跨任务长期沉淀
- **项目级候选 memory**：本次任务运行中提炼出的候选经验

### 3.4 目标四：支持两条质量维度
P3 必须同时支持：
- `generic`：通用质量模式，不带具体业务领域属性
- `domain`：领域质量模式，例如 permission / organization / enterprise_security / personal_account
同时允许第三条辅助维度：
- `task_type`：任务类型维度，例如 self_apply / admin_config / audit_view

### 3.5 目标五：支持主观偏好正式化
系统已有硬规则只能定义“最低合格标准”。  
P3 还必须预留一层正式偏好文件，让项目维护者后续补充“更高质量的偏好标准”。

### 3.6 目标六：让 Memory 对下游任务真正可消费
P3 不是做存档，而是做“下次任务能读到、能起作用的经验层”。

### 3.7 目标七：用户可看见本次任务沉淀了什么
除了机器真源，还必须给出：
- `projects/<project-id>/workspace/memory_summary.md`

让用户明确看到：
- 本次新增了哪些模式
- 识别了哪些失败模式
- 哪些经验被纳入长期 memory
- 哪些只是候选，不进入长期沉淀

---

## 4. 非目标（明确不做）

本次 P3 明确不做以下内容：

### 4.1 不做聊天记忆
P3 不是把用户聊天历史变成长期 persona memory。

### 4.2 不做向量数据库优先方案
首轮不引入重型外部 memory infra。  
先用文件系统 + 结构化文档落地。

### 4.3 不直接耦合 `knowledge/wiki/`
P3 不是 wiki 子系统的一部分，不往 `knowledge/wiki/` 直接落盘。

### 4.4 不直接复制通过样例全文
首轮 Memory Layer 不把整篇 blueprint 原样当作 memory 主体。

### 4.5 不替代规则层
P3 负责沉淀“质量经验”，不替代 `specs/` 的正式合同。

---

## 5. P3 在整体架构中的定位

P3 应被理解为：

> **Execution Hub / Repair Loop / Capability Registry 之上的质量经验沉淀层**

它位于：
- `specs` 规则层之下
- `packages` 执行层之旁
- `memory/` 长期沉淀层之中
- `projects/<project-id>/runtime/memory/` 候选提取层之内
- `projects/<project-id>/workspace/memory_summary.md` 用户可读层之上

### 当前状态
```text
specs -> packages -> projects/runtime/workspace
```

### 引入 P3 后
```text
specs -> packages -> projects/runtime/memory -> memory/ -> workspace/memory_summary.md
```

注意：
- `memory/` 是独立顶层子系统
- `projects/<project-id>/runtime/memory/` 是本轮候选
- `workspace/memory_summary.md` 是人类摘要
- `knowledge/wiki/` 不直接承载 P3

---

## 6. P3 核心设计原则

### 6.1 可复用优先
只有跨任务、跨样例可复用的经验，才值得进入长期 memory。

### 6.2 证据优先
任何 memory 都必须能回答：
- 它来自什么任务
- 来自什么样例 / issue / repair / capability
- 为什么值得沉淀

### 6.3 不污染当前任务真相
当前任务的事实、业务判断、体验推导，仍以当前任务输入与显式引用知识为准。  
Memory 只能作为：
- 结构启发
- 风险提醒
- 模式参考
- 失败预警
- 偏好校准

### 6.4 与 wiki 解耦
P3 不得把 memory 混入 `knowledge/wiki/`。

### 6.5 两层沉淀
- 项目运行时候选
- 长期沉淀真源

### 6.6 两维质量
必须支持：
- 通用质量
- 领域质量  
可选再叠加任务类型维度。

### 6.7 人机双消费
既要让机器后续任务消费，也要让人能在 `memory_summary.md` 看懂。

---

## 7. 推荐目录设计

## 7.1 顶层长期 Memory 子系统（推荐）

在仓库根目录新增：

```text
memory/
  README.md
  index.json
  patterns/
    generic/
    permission/
    organization/
    enterprise_security/
    personal_account/
  failure_modes/
    generic/
    permission/
    organization/
    enterprise_security/
    personal_account/
  preferences/
    quality_preferences.md
    preference_rules.yaml
  capability_insights/
```

### 说明

#### `patterns/`
存高质量模式卡（pattern cards）

#### `failure_modes/`
存失败模式卡（failure mode cards）

#### `preferences/`
存项目长期质量偏好骨架
- `quality_preferences.md`：自然语言偏好
- `preference_rules.yaml`：结构化偏好规则

#### `capability_insights/`
存围绕 capability 的经验沉淀，例如：
- 哪个 capability 在什么任务类型下常失败
- 哪个 capability 最容易触发 warning
- 哪种修复单元常出现

---

## 7.2 项目级运行时 Memory 候选层

在每个项目中新增：

```text
projects/<project-id>/runtime/memory/
  extracted_memory_candidates.json
  accepted_memory_items.json
  memory_trace.json
```

### 文件职责

#### `extracted_memory_candidates.json`
本次任务自动/半自动提炼出的候选 memory 列表。

#### `accepted_memory_items.json`
本次任务中，被接受进入长期 memory 的项目级记录。

#### `memory_trace.json`
记录本次任务中：
- 使用了哪些 memory
- 新提炼了哪些 memory
- 哪些 memory 被拒绝 / 延期

---

## 7.3 用户可读摘要层

在每个项目中新增：

```text
projects/<project-id>/workspace/memory_summary.md
```

该文件面向用户，回答：
- 本次任务沉淀出了什么
- 哪些是通用模式
- 哪些是领域模式
- 哪些是失败模式
- 哪些进入长期 memory
- 哪些只是候选

---

## 8. Memory 对象模型

P3 首轮建议至少支持 4 类 memory 对象：

### 8.1 Pattern Card（高质量模式卡）
记录：
- 什么结构 / 表达方式 / 处理方式能显著提高输出质量
- 适用于哪些阶段
- 适用于哪些领域 / 任务类型
- 不适用于什么场景

### 8.2 Failure Mode Card（失败模式卡）
记录：
- 哪类问题常出现
- 典型症状
- 常见触发条件
- 常见修复建议
- 哪些 capability / stage 容易触发

### 8.3 Preference Card（偏好卡）
记录：
- 项目维护者的高质量偏好
- 比“最低合格线”更高的质量取向
- 不应自动从样例推断，优先由人工补充

### 8.4 Capability Insight（能力经验）
记录：
- 某 capability 在何种任务类型下更关键
- 常见风险
- 常见 warning / blocker
- 推荐搭配的 review 点

---

## 9. 什么样的内容可以进入 Memory

Memory 必须同时满足以下标准中的大多数：

### 9.1 跨任务可复用
不是只对某个单次任务成立。

### 9.2 能提高后续任务质量
例如能减少：
- blueprint 摘要化
- trace missing
- 状态矩阵缺失
- 体验层空泛口号
- business / experience 越权

### 9.3 能写成“规则化启发”
能提炼成：
- pattern
- anti-pattern
- checklist
- failure mode
- capability guidance

### 9.4 能给出来源证据
能追溯到：
- 哪个任务
- 哪个样例
- 哪次 repair loop
- 哪个 capability
- 哪种 check / gate / acceptance 结果

---

## 10. 什么样的内容不应进入长期 Memory

以下内容不应直接进入长期 memory：

- 单次任务特有事实
- 特定项目背景的临时结论
- 整篇 blueprint 全文
- 只靠主观感觉判断“写得不错”的段落
- 无法复用的措辞细节

---

## 11. 质量维度模型

P3 必须支持至少两条质量维度：

### 11.1 通用质量（generic）
不带具体业务领域属性，例如：
- business blueprint 不应只是 facts 摘要
- experience blueprint 必须覆盖异常态
- trace mapping 应显式可追溯
- copy contract 不能只有标题没有语义责任

### 11.2 领域质量（domain）
带业务领域属性，例如：
- permission
- organization
- enterprise_security
- personal_account

### 11.3 任务类型质量（task_type，可选）
例如：
- self_apply
- admin_config
- audit_view
- approval_flow

---

## 12. 领域归类规则

AI 不应凭“感觉”决定 memory 属于哪个领域。  
归类必须基于证据。

### 12.1 优先级规则

#### 第一优先：`task_card.domain`
如果当前任务显式给出 `Domain`，则该任务提炼出的 domain memory 优先归到该领域。

#### 第二优先：显式 wiki / knowledge 引用
如果任务主要显式引用某一领域 wiki / knowledge，则优先归到相应领域。

#### 第三优先：术语与结构证据
如前两者都弱，可结合：
- 高频术语
- 当前 capability / issue 上下文
- 明显的领域结构特征

#### 第四优先：不确定则不硬分
如果归类证据不足：
- 能抽成通用规则，就记为 `generic`
- 不能确认，就进入 `candidate` 或 `unclassified`

### 12.2 归类字段

每条 memory 至少应包含：

- `scope`
- `domain_tags`
- `task_type_tags`
- `classification_basis`
- `confidence`

---

## 13. 主观偏好如何落地

P3 不要求现在就填满主观偏好，但必须先搭骨架。

### 推荐文件
```text
memory/preferences/
  quality_preferences.md
  preference_rules.yaml
```

### 作用

#### `quality_preferences.md`
供项目维护者后续用自然语言补充：
- 你认为什么叫高质量
- 哪些写法你更看重
- 哪些表达方式你不接受

#### `preference_rules.yaml`
用于把偏好转成结构化字段，例如：
- 更偏好 judgement trace 显式展开
- 更偏好 state & feedback matrix 完整
- 不接受只有口号式体验蓝图

### 原则
偏好文件是人工补充，不应由 AI 自行臆造。

---

## 14. 与当前项目结构的关系

### 不会改变的
- 主架构不变
- `specs/` 仍是规则真源
- `packages/` 仍是执行中枢
- `projects/<project-id>/` 仍是单任务真相层
- `knowledge/wiki/` 仍是独立子系统

### 会新增的
- 顶层 `memory/` 子系统
- 项目级 `runtime/memory/`
- 用户可见 `workspace/memory_summary.md`

### 结论
P3 是 **增强层**，不是 **架构重做**。

---

## 15. 与 P2 / P4 的衔接

### P2 为 P3 提供
- 失败问题
- 修复路径
- blocker / warning / accepted / deferred 结构信息

### P4 为 P3 提供
- 正式 capability 对象
- capability 的阶段、入口、依赖与副作用

因此 P3 可以沉淀：
- 哪些失败模式常出现
- 哪些 capability 常触发问题
- 哪些模式能减少 repair loop 触发率

---

## 16. 典型 Memory 示例

### 示例 A：通用 Pattern
- `scope`: `generic`
- `applies_to_stage`: `experience`
- `rule`: “体验蓝图必须显式覆盖失败态、阻断态、处理中状态”
- `why_it_helps`: “可显著降低 experience gate 与 coverage warning”
- `anti_pattern`: “只写正常流程，不写状态反馈矩阵”

### 示例 B：领域 Pattern（permission）
- `scope`: `domain`
- `domain_tags`: [`permission`]
- `applies_to_stage`: `business`
- `rule`: “审批型 permission 任务必须在业务蓝图中显式展开判断追踪映射”
- `classification_basis`:
  - `task_card.domain=permission`
  - `wiki_ref=permission-domain-index`

### 示例 C：Capability Insight
- `capability_id`: `repair_plan`
- `task_type_tags`: [`self_apply`]
- `insight`: “在自助申请类任务中，repair_plan 更容易暴露 trace missing 与 coverage gap”
- `recommended_followup`: “优先检查 business judgement trace 与 experience state matrix”

---

## 17. 风险与应对

### 风险 1：把 P3 做成 wiki
**后果：** 与 `knowledge/wiki/` 耦合，破坏子系统独立性  
**应对：** 长期 memory 放根目录 `memory/`

### 风险 2：把整篇样例直接存为 memory
**后果：** 冗余、难复用、污染长期层  
**应对：** 只存提炼后的 pattern / failure mode / preference / capability insight

### 风险 3：AI 硬猜领域归类
**后果：** 领域 memory 失真  
**应对：** 归类必须依赖 task_card / knowledge 引用 / 证据字段

### 风险 4：偏好层被 AI 自动生成
**后果：** 伪偏好、漂移  
**应对：** 偏好只搭骨架，内容由你后续填

---

## 18. P3 验收标准

P3 改造可视为完成，当以下条件同时满足：

### 18.1 规则完成
- `specs/13_memory_layer_contract.md` 已建立

### 18.2 结构完成
- 顶层 `memory/` 子系统已建立
- `memory/preferences/` 骨架已建立
- `memory/domains/permission/`
- `memory/domains/organization/`
- `memory/domains/enterprise_security/`
- `memory/domains/personal_account/`
  已建立

### 18.3 项目级运行层完成
- `projects/<project-id>/runtime/memory/` 可生成候选 memory 产物

### 18.4 用户可读层完成
- `projects/<project-id>/workspace/memory_summary.md` 可生成

### 18.5 质量维度完成
- 至少支持 generic / domain 两维
- 可选支持 task_type 维

### 18.6 兼容完成
- 不改变现有三阶段主链
- 不改变 wiki 子系统定位
- 不破坏现有 runbook / execute 命令

---

## 19. 实施顺序（推荐）

### Phase 1：先立规则
- 写 `specs/13_memory_layer_contract.md`

### Phase 2：再搭子系统骨架
- 建 `memory/`
- 建 preferences / patterns / failure_modes / capability_insights 骨架
- 建领域目录骨架

### Phase 3：再补项目级运行层
- `runtime/memory/`
- `workspace/memory_summary.md`

### Phase 4：最后补提取与汇总命令
- 让 packages 产生候选 memory
- 让用户可查看 memory_summary

---

## 20. 最终结论

对于当前 UX-Blueprinting 项目，P3 不是聊天式“会记住你说过什么”，而是：

> **把高质量模式、失败模式、偏好与能力经验沉淀为跨任务可复用的质量经验层。**

它的价值不在于更自动，而在于：

- 后续任务更稳
- 输出更接近你要的高质量标准
- 好样例的价值能被复用
- 失败经验不会只停留在一次性修复里
- 不会污染 wiki 子系统

P3 完成后，项目将从：

> **contract-driven + repair-aware + capability-declared 的工作台**

增强为：

> **contract-driven + quality-memory-enabled 的 harness-style execution workbench**
