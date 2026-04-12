# Capability Registry 合同

## 目标

定义当前项目中 `Capability Registry`（能力注册层）应如何对执行中枢的正式能力进行显式登记、统一声明与最小治理。

本合同的目标不是建立新的执行主控系统，也不是替代 `packages/` 中的真实执行逻辑，而是在现有执行中枢、主阶段链路与 repair loop 之上，正式建立一层 **显式能力声明层**。

本合同用于解决以下问题：

- 当前系统有哪些正式能力
- 每个能力属于哪个阶段
- 每个能力的正式入口是什么
- 每个能力依赖什么输入，会产生什么输出
- 哪些能力会修改项目正式产物，哪些只会修改运行时状态
- 哪些能力可重跑，哪些能力需要人工确认
- 如何为未来的 command / hook / policy plugin / plugin loader 预留统一能力模型

## 定位

Capability Registry 是执行中枢的能力声明层，不是新的执行中枢。

它负责：

- 把当前正式能力登记为统一 capability 对象
- 为每个 capability 声明最小治理信息
- 为 IDE / AI / runbook / 后续记忆层提供统一消费面
- 为未来扩展位提供统一挂接模型

它不负责：

- 直接执行任务步骤
- 替代 facts / business / experience / repair 的真实逻辑
- 改写项目正式产物
- 替代 `specs/` 作为规则真源
- 替代 `packages/` 作为固定执行入口

## 与现有架构的关系

Capability Registry 必须嵌入以下现有结构中，而不是替代它们：

- `specs/`：唯一正式规则真源
- `packages/`：正式执行中枢
- `projects/<project-id>/`：项目真相层
- `docs/runbook/`：操作说明层

Capability Registry 的正式声明产物原则上位于：

```text
packages/capability_registry/
```

其中：

- `registry.yaml`：系统级能力总表
- `capabilities/*.yaml`：单能力声明文件

## 上位依赖

Capability Registry 必须受以下文档约束：

- `specs/01_execution_hub_spec.md`
- `specs/03_task_card_contract.md`
- `specs/06_check_contract.md`
- `specs/11_repair_loop_contract.md`

如 capability 归属 facts / business / experience 阶段，还必须受：

- `specs/08_fact_extraction_contract.md`
- `specs/09_business_blueprint_contract.md`
- `specs/10_experience_blueprint_contract.md`

## 统一原则

Capability Registry 必须遵守：

- 先声明，再消费
- 不声明不存在的正式能力
- 不把实验性脚本伪装成正式能力
- 声明与实现必须可追溯
- Registry 只存“能力元信息”，不承载实现逻辑
- Registry 与 `packages/__main__.py`、Execution Hub Spec、runbook 不得长期不一致

## 正式输出

Capability Registry 至少输出以下系统级产物：

- `packages/capability_registry/registry.yaml`
- `packages/capability_registry/capabilities/*.yaml`

如需要 CLI 查询能力，可选新增：

- `python -m packages capabilities-list`
- `python -m packages capability-show <capability-id>`

首轮 Capability Registry 不要求项目级 runtime 快照；如后续扩展，可选生成：

- `projects/<project-id>/runtime/capabilities/capability_snapshot.json`

## registry.yaml 合同

### 目标

记录系统级能力总表，表达“当前仓库有哪些正式 capability”。

### 最小字段

`registry.yaml` 至少包含：

- `registry_version`
- `project`
- `description`
- `capability_ids`
- `last_updated_from`
- `notes`

### 字段说明

#### `registry_version`
能力注册表版本号。

#### `project`
固定指向当前仓库项目名。

#### `capability_ids`
系统当前正式 capability 的 ID 列表。  
这些 ID 必须与 `capabilities/*.yaml` 一一对应。

#### `last_updated_from`
用于说明 Registry 主要对齐的实现与规则来源，例如：

- `packages/__main__.py`
- `specs/01_execution_hub_spec.md`

## 单 capability 文件合同

每个正式 capability 必须有一个独立声明文件：

```text
packages/capability_registry/capabilities/<capability-id>.yaml
```

### 最小字段

每个 capability 至少包含：

- `capability_id`
- `display_name`
- `type`
- `stage`
- `entrypoint`
- `description`
- `required_inputs`
- `declared_outputs`
- `dependencies`
- `retryable`
- `review_required`
- `mutates_formal_artifacts`
- `mutates_runtime_state`
- `source_of_truth_refs`
- `status`

### 字段说明

#### `capability_id`
能力唯一标识。  
必须稳定、可读、不可与其他 capability 冲突。

建议使用 snake_case，例如：

- `task_bootstrap`
- `context_assemble`
- `facts_gate`
- `business_gate`
- `experience_gate`
- `validate_outputs`
- `coverage_check`
- `repair_plan`
- `repair_status`
- `repair_close`
- `archive_artifacts`

#### `display_name`
人类可读名称。

#### `type`
能力类型，至少允许以下值：

- `command`
- `stage_gate`
- `final_check`
- `repair`
- `archive`
- `hook`
- `policy_plugin`
- `plugin_loader`

首轮实现中，至少应覆盖当前正式存在的：
- `command`
- `stage_gate`
- `final_check`
- `repair`
- `archive`

#### `stage`
能力归属阶段，至少允许：

- `runtime`
- `facts`
- `business`
- `experience`
- `repair`
- `final`
- `archive`
- `cross_stage`

#### `entrypoint`
正式调用入口。  
对于当前系统，优先写成：

```bash
python -m packages <command> <project-id>
```

如果未来 capability 不通过 CLI 调用，也必须给出其正式入口说明。

#### `description`
简洁说明 capability 的职责。  
必须说明“它做什么”，而不是实现细节。

#### `required_inputs`
至少列出 capability 正式依赖的输入文件、输入状态或前置条件。

#### `declared_outputs`
至少列出 capability 正式产出的文件、状态或副作用。

#### `dependencies`
列出上游 capability_id。  
如果无依赖，必须显式写空列表，而不是省略。

#### `retryable`
布尔值。  
表达 capability 是否允许重跑。

#### `review_required`
布尔值。  
表达 capability 的结果是否默认需要人工审查后才能继续下游操作。

#### `mutates_formal_artifacts`
布尔值。  
表达 capability 是否会直接改写 `workspace/` 或其他正式产物。

#### `mutates_runtime_state`
布尔值。  
表达 capability 是否会改写 `runtime/` 状态。

#### `source_of_truth_refs`
至少列出：
- 对应的 spec
- 对应的实现位置
- 必要时对应的 runbook

#### `status`
仅允许：

- `active`
- `planned`
- `deprecated`

首轮实现中，当前已正式存在的能力必须标记为 `active`。

## 当前正式能力的最小登记范围

Capability Registry 首轮至少必须登记以下能力：

- `task_bootstrap`
- `context_assemble`
- `facts_gate`
- `business_gate`
- `experience_gate`
- `validate_outputs`
- `coverage_check`
- `repair_plan`
- `repair_status`
- `repair_close`
- `archive_artifacts`

如果某能力已经在 `packages/__main__.py` 中正式暴露，就不得缺席 Registry。

## 与 packages/__main__.py 的一致性要求

Capability Registry 必须与当前命令面保持一致。

### 一致性规则

- `packages/__main__.py` 中已正式暴露的命令，应在 Registry 中有对应 capability
- Registry 中标记为 `active` 的 command 类 capability，应能在正式命令面找到入口
- Registry 中不存在的能力，不得在 runbook 中被描述为正式能力

### 失败条件

- 命令存在，但 Registry 未登记
- Registry 标为 active，但命令入口不存在
- Registry 与 Execution Hub Spec 对同一能力的阶段归属矛盾

## 与 Execution Hub Spec 的一致性要求

Execution Hub Spec 描述的是步骤链路，Capability Registry 描述的是能力对象。  
两者必须一致，但职责不同。

### Execution Hub Spec 负责
- 步骤顺序
- 输入输出合同
- 失败条件
- 阶段边界

### Capability Registry 负责
- 能力声明
- 能力归属
- 能力治理字段
- 能力查询消费面

### 最低一致性要求

对任一正式 capability，Registry 至少要能追溯到：
- Execution Hub 中对应步骤
- `packages` 中对应入口
- 相关 spec 合同

## 与 runbook 的关系

runbook 负责说明“如何操作”，  
Capability Registry 负责说明“系统有哪些正式能力”。

两者必须保持一致：

- runbook 中描述为正式可用的能力，Registry 中应存在
- Registry 中标为 active 的能力，runbook 不得长期缺失操作说明
- 如某能力属于系统内能力但不直接面向操作者，runbook 可不单独展开，但 Registry 仍必须登记

## 与未来 plugin / hook / policy plugin 的关系

Execution Hub 已预留：

- command
- hook
- policy plugin
- plugin loader

Capability Registry 必须允许这些未来对象被登记为 capability，但首轮不要求全部实现。

### 首轮原则
- 先登记当前已正式存在的能力
- 不为了未来扩展而强行引入复杂插件系统
- 对未来 capability type 只做模型预留，不做重实现

## 人类与 AI 消费要求

Capability Registry 必须同时支持：

### 人类消费
让项目维护者、协作者、操作者快速理解：
- 系统有哪些正式能力
- 哪些能力在哪个阶段
- 哪些能力会修改正式产物
- 哪些能力需要 review

### AI / IDE 消费
让外部 AI / IDE 工具更容易理解：
- 当前任务链上有哪些正式能力
- 什么时候该调哪个能力
- 这个能力是否可重跑
- 是否需要人工确认

因此，Registry 的内容必须：
- 简洁
- 稳定
- 结构化
- 不依赖长篇自然语言才能理解

## Warning 条件

以下情况可视为 warning，但允许继续推进 P4：

- 个别 capability 的 source_of_truth_refs 还未完全补齐
- 个别 capability 的 runbook 说明仍偏粗
- 首轮只登记 command 类与 repair 类 capability，未来类型尚未启用
- 还没有 `capabilities-list` / `capability-show` 查询命令

## 失败条件

Capability Registry 视为失败，如出现以下任一情况：

- `registry.yaml` 缺失
- 当前正式命令未全部登记
- active capability 无法追溯到正式入口
- Registry 与 `packages/__main__.py` 不一致
- Registry 与 Execution Hub 的阶段归属严重冲突
- 把实现逻辑塞进 Registry，导致声明层和执行层混杂
- Registry 反过来替代 `specs/` 或 `packages/` 的职责

## 合格标准

一个合格的 Capability Registry 至少满足：

- 已建立正式合同
- 已建立系统级 registry
- 已登记当前正式能力
- 每个能力有最小治理字段
- 与 `packages/__main__.py`、Execution Hub、runbook 保持一致
- 不改变现有项目主架构
- 不引入新的主控制器
- 能被人类和 AI 同时消费

## 阶段完成标准

P4 可视为落地完成，当以下条件同时满足：

- `specs/12_capability_registry_contract.md` 已建立
- `packages/capability_registry/registry.yaml` 已建立
- 当前正式能力均有独立 capability 文件
- 如增加查询命令，其输出能正确读取 Registry
- 至少完成一次一致性检查：
  - registry vs `packages/__main__.py`
  - registry vs `specs/01_execution_hub_spec.md`
  - registry vs runbook
- 对当前通过样例与主流程不造成兼容性破坏

## 与其他模块的同步要求

本合同引入后，至少应同步检查以下模块：

- `specs/01_execution_hub_spec.md`
- `packages/__main__.py`
- `packages/README.md`
- `docs/runbook/external_ai_quickstart.md`
- `docs/runbook/task_execution_flow.md`
- `docs/runbook/repair_loop_flow.md`

如果合同已建立，但命令面、runbook 与 Registry 长期不同步，则 Capability Registry 只能停留在文档层，无法成为正式能力治理层。

## 一句话原则

**Registry 负责把能力登记清楚，不负责替代能力执行；先注册已有能力，再考虑未来扩展。**
