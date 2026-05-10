# Memory Layer 合同

> 暂不启用。Memory 层在当前项目形态下投入产出比低，contracts 自身的迭代即为质量经验的沉淀方式。本文件保留作为未来扩展占位。

- 什么样的经验可以进入长期 memory
- 什么样的内容只能作为候选，不应长期沉淀
- 如何区分通用质量与领域质量
- 如何处理主观偏好
- 如何让本次任务沉淀出的经验被后续任务消费
- 如何保证 Memory 不污染当前任务真相，也不与 wiki 耦合

## 定位

Memory Layer 是执行中枢的质量经验层，不是新的知识子系统，也不是新的执行中枢。

它负责：

- 从通过样例、失败样例、repair loop、capability 使用结果中提炼可复用经验
- 将经验组织为 pattern / failure_mode / preference / capability_insight
- 对经验进行 generic / domain / task_type 分类
- 记录本次任务提炼出的 memory 候选
- 将被接受的 memory 写入长期 memory 子系统
- 输出用户可读的 `workspace/memory_summary.md`

它不负责：

- 替代 `facts.md`
- 替代业务蓝图或体验蓝图正文
- 替代 `knowledge/wiki/`
- 自动决定业务结论
- 自动补写主观偏好
- 存储完整会话历史

## 与现有架构的关系

Memory Layer 必须嵌入以下现有结构中，而不是替代它们：

- `specs/`：唯一正式规则真源
- `packages/`：正式执行中枢
- `projects/<project-id>/runtime/`：机器运行层
- `projects/<project-id>/workspace/`：人读结果层
- `memory/`：长期 memory 子系统
- `knowledge/wiki/`：独立 wiki 子系统

### 强边界

`knowledge/wiki/` 承担：
- 长期知识沉淀
- 跨任务复用
- 概念统一
- 上下文压缩

`knowledge/wiki/` 不承担：
- 替代 facts
- 替代 business blueprint
- 替代 experience blueprint

因此，Memory Layer **不得直接写入 `knowledge/wiki/` 作为首轮落点**。  
长期 memory 必须位于独立顶层：

```text
memory/
```

## 上位依赖

Memory Layer 必须受以下文档约束：

- `specs/01_execution_hub_spec.md`
- `specs/03_task_card_contract.md`
- `specs/07_wiki_contract.md`
- `specs/11_repair_loop_contract.md`
- `specs/12_capability_registry_contract.md`

如提炼内容涉及阶段质量要求，还必须受：

- `specs/08_fact_extraction_contract.md`
- `specs/09_business_blueprint_contract.md`
- `specs/10_experience_blueprint_contract.md`

## 统一原则

Memory Layer 必须遵守：

- 只沉淀可复用经验，不沉淀单次任务事实
- 只沉淀有证据来源的经验，不沉淀纯感觉
- 当前任务真相优先，memory 只作启发与校准
- 与 wiki 解耦
- 用户偏好只能人工补充，不得由 AI 自行臆造
- 长期 memory 与项目级候选 memory 必须分层
- 用户必须能在 `workspace/memory_summary.md` 查看本次沉淀结果

## 正式输出

Memory Layer 至少输出以下产物：

### 系统级长期产物
- `memory/index.json`
- `memory/patterns/...`
- `memory/failure_modes/...`
- `memory/preferences/quality_preferences.md`
- `memory/preferences/preference_rules.yaml`
- `memory/capability_insights/...`

### 项目级运行产物
- `projects/<project-id>/runtime/memory/extracted_memory_candidates.json`
- `projects/<project-id>/runtime/memory/accepted_memory_items.json`
- `projects/<project-id>/runtime/memory/memory_trace.json`

### 用户可读产物
- `projects/<project-id>/workspace/memory_summary.md`

## Memory 分类模型

P3 首轮至少支持以下对象类型：

- `pattern`
- `failure_mode`
- `preference`
- `capability_insight`

## 质量维度模型

每条 memory 至少要有以下维度字段：

- `scope`
- `domain_tags`
- `task_type_tags`

### `scope`
仅允许：

- `generic`
- `domain`
- `task_type`

### `domain_tags`
领域标签列表。  
首轮至少预留：

- `permission`
- `organization`
- `enterprise_security`
- `personal_account`

### `task_type_tags`
任务类型标签列表。  
首轮允许为空，但结构必须预留。

## 领域归类规则

AI 不得仅凭感觉决定 memory 归属领域。  
归类必须依赖证据。

### 归类优先级

#### 第一优先：`task_card.domain`
如果当前任务在 `task_card` 中显式给出 `Domain`，则该任务提炼出的领域 memory 应优先归到该领域。

#### 第二优先：显式 knowledge / wiki 引用
如任务主要引用某一领域的 wiki / knowledge，则应优先归入对应领域。

#### 第三优先：术语与结构证据
如前两者不足，可结合：
- 高频术语
- 当前 issue / capability 上下文
- 结构性领域特征

#### 第四优先：不确定则不硬分
如果归类证据不足：
- 可归为 `generic`
- 或暂存为 `candidate / unclassified`

### 必需归类字段

每条 memory 至少必须包含：

- `classification_basis`
- `confidence`

其中：

#### `classification_basis`
记录归类依据，例如：
- `task_card.domain=权限管理`
- `wiki_ref=knowledge/wiki/summaries/业务/权限管理/00_领域概述.md`

#### `confidence`
仅允许：
- `high`
- `medium`
- `low`

## 什么内容可以进入长期 Memory

进入长期 memory 的内容，至少应满足以下条件中的大多数：

- 跨任务可复用
- 能提升后续任务质量
- 能提炼成模式、失败模式、偏好或 capability insight
- 能给出来源证据
- 不依赖某个单次任务事实

## 什么内容不能直接进入长期 Memory

以下内容不得直接进入长期 memory：

- 单次任务事实
- 某个项目独有背景
- 某个样例全文
- 当前任务的最终业务结论
- 当前任务的最终体验蓝图全文
- 无证据支撑的主观判断
- AI 自行生成的“用户偏好”

## 长期 Memory 子系统合同

长期 memory 位于顶层：

```text
memory/
```

### 最小结构

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

### 目录约束

- `memory/` 为独立顶层子系统
- 不得写入 `knowledge/wiki/`
- 不得写入 `projects/<project-id>/workspace/` 作为长期真源
- 项目级摘要可写入 `workspace/`，但长期真源必须写入 `memory/`

## 单条 Memory 最小字段

每条长期 memory 至少包含：

- `memory_id`
- `kind`
- `scope`
- `title`
- `rule`
- `why_it_helps`
- `anti_pattern`
- `applies_to_stage`
- `domain_tags`
- `task_type_tags`
- `classification_basis`
- `confidence`
- `source_tasks`
- `source_artifacts`
- `source_issue_ids`
- `status`

### `kind`
仅允许：
- `pattern`
- `failure_mode`
- `preference`
- `capability_insight`

### `status`
仅允许：
- `candidate`
- `accepted`
- `rejected`
- `deprecated`

首轮进入长期 memory 的条目，必须为 `accepted`。

## Preference 文件合同

### `memory/preferences/quality_preferences.md`
用途：
- 由项目维护者补充主观高质量偏好
- 允许自然语言表达

要求：
- AI 不得自动填充偏好正文
- 首轮只需建立骨架与说明

### `memory/preferences/preference_rules.yaml`
用途：
- 把偏好转成结构化字段
- 供后续任务消费

要求：
- 首轮允许为空骨架
- 字段设计要支持：
  - stage 偏好
  - 质量重点
  - 不接受写法
  - 风险容忍度

## 项目级运行时 Memory 合同

每个项目应能在：

```text
projects/<project-id>/runtime/memory/
```

下生成以下产物：

- `extracted_memory_candidates.json`
- `accepted_memory_items.json`
- `memory_trace.json`

## 用户可读摘要合同

每个项目必须支持生成：

```text
projects/<project-id>/workspace/memory_summary.md
```

### 最小结构

该文件至少包含：

- `本次新增的通用模式`
- `本次新增的领域模式`
- `本次识别的失败模式`
- `本次新增的 capability insight`
- `进入长期 memory 的条目`
- `仅作为候选、未进入长期 memory 的条目`
- `当前偏好骨架位置`

## Warning 条件

以下情况可视为 warning，但允许继续推进 P3：

- 首轮只完成 generic + domain 两维，task_type 仍为空骨架
- preference 文件为空骨架，尚未填入你的主观偏好
- 首轮只建立 memory 文件系统结构，尚未做复杂自动提取
- 个别 memory 的 classification_basis 需要人工补充

## 失败条件

Memory Layer 视为失败，如出现以下任一情况：

- 长期 memory 与 wiki 直接耦合
- 缺少独立 `memory/` 顶层子系统
- 没有 `workspace/memory_summary.md`
- 把整篇 blueprint 直接作为长期 memory 主体
- 允许 AI 自动捏造主观偏好
- 无法区分 generic 与 domain
- 领域归类没有任何证据基础
- Memory 污染当前任务真相判断

## 合格标准

一个合格的 Memory Layer 至少满足：

- 已建立正式合同
- 已建立独立 `memory/` 顶层子系统
- 已建立 preference 骨架
- 已预建领域目录骨架
- 已建立项目级 `runtime/memory/`
- 已建立 `workspace/memory_summary.md`
- 已支持 generic / domain 两维
- 不与 wiki 耦合
- 不改变现有主架构

## 阶段完成标准

P3 可视为落地完成，当以下条件同时满足：

- `specs/13_memory_layer_contract.md` 已建立
- `memory/` 子系统骨架已建立
- `memory/preferences/` 骨架已建立
- 领域目录骨架已建立
- 项目级 runtime memory 产物可生成
- `workspace/memory_summary.md` 可生成
- 至少完成一次样例任务的 memory 候选提取与摘要输出
- 不破坏现有主链路与 P2/P4 成果

## 与其他模块的同步要求

本合同引入后，至少应同步检查以下模块：

- `specs/01_execution_hub_spec.md`
- `specs/07_wiki_contract.md`
- `specs/11_repair_loop_contract.md`
- `specs/12_capability_registry_contract.md`
- `packages/README.md`
- `projects/README.md`
- `docs/runbook/external_ai_quickstart.md`
- `docs/runbook/task_execution_flow.md`
- `docs/runbook/repair_loop_flow.md`

## 一句话原则

**Memory 只沉淀可复用的质量经验，不沉淀整篇任务正文；长期 memory 顶层独立，项目级摘要面向用户可读。**
