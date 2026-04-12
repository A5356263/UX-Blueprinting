# P4 正式改造方案：Capability Registry（能力注册层）增强设计
**Project:** UX-Blueprinting  
**Document Type:** Formal Enhancement Plan  
**Status:** Proposed  
**Target:** 在不改变现有项目主架构的前提下，为执行中枢补齐正式的 Capability Registry（能力注册层）  
**Scope:** P4 only（Capability Registry）  
**Out of Scope:** AI Bridge、长期记忆层实现、外部模型 API 适配、重型动态调度器

---

## 1. 文档目标

本方案用于正式定义 **P4: Capability Registry（能力注册层）** 在当前仓库中的改造方式。  
目标不是把现有执行中枢重写成新的控制系统，也不是引入重型 plugin 平台，而是在 **现有 `specs / packages / projects / runtime / exports` 骨架** 上，补一层清晰的“能力声明与治理层”。

该层的作用是把当前已经存在的正式能力——例如：

- `bootstrap`
- `assemble`
- `gate-facts`
- `gate-business`
- `gate-experience`
- `validate`
- `coverage`
- `repair-plan`
- `repair-status`
- `repair-close`
- `archive`

以及未来可能扩展的：

- command
- hook
- policy plugin
- plugin loader

从“散落在命令、spec、runbook 中的隐式能力”，收敛为“可声明、可查询、可治理的正式能力对象”。

---

## 2. 当前项目基线判断

当前仓库已经具备：

- `specs/` 作为唯一正式规则真源
- `packages/` 作为正式执行中枢与固定命令入口
- `projects/<project-id>/` 作为项目真相层
- `source / workspace / runtime / exports` 四层稳定分工
- facts / business / experience 三阶段主链路
- gate / validate / coverage / repair / archive 完整执行链

因此，当前项目不是没有“能力层”，而是：

> **能力已经存在，但主要以命令、规则和 runbook 的分散形式存在。**

这会带来以下问题：

1. 只有熟悉仓库的人，才能快速拼出“系统到底有哪些正式能力”
2. AI / IDE 工具能看到命令，但不一定知道：
   - 什么时候该用哪个能力
   - 这个能力属于哪个阶段
   - 它会读什么、写什么
   - 是否需要 review
   - 是否支持重跑
3. 后续如果增加：
   - repair 相关能力
   - command / hook / policy plugin
   - 未来的 skill 承载器  
   没有能力注册层，就会越来越依赖“作者脑内知识”
4. 后续做 P3 Memory Layer 时，记忆对象会挂在零散命令上，而不是挂在正式能力对象上

因此，P4 的目标不是“再发明一套能力”，而是：

> **把现有能力显式登记成一张正式能力地图。**

---

## 3. P4 设计目标

Capability Registry 需要实现以下 6 个正式目标：

### 3.1 目标一：把隐式能力升级为显式能力对象
让系统正式知道自己有哪些能力，而不是只能从命令和 spec 中间接推断。

### 3.2 目标二：给每个能力补齐正式声明
至少声明：
- capability_id
- stage
- entrypoint
- inputs
- outputs
- dependencies
- retryability
- review requirement
- mutation scope

### 3.3 目标三：不替代现有执行中枢
Capability Registry 只做“声明层”和“治理层”，不替代 `packages` 里的真实执行逻辑。

### 3.4 目标四：为未来扩展位做准备
让未来的：
- command
- hook
- policy plugin
- plugin loader
能挂到同一能力模型下。

### 3.5 目标五：为 AI / IDE / runbook 提供统一消费面
让 IDE 里的 AI 不必同时阅读多个 spec 和 runbook 才知道“该调用什么”。

### 3.6 目标六：为 P3 Memory Layer 提供稳定挂点
让后续记忆对象不再挂在零散命令名上，而是挂在正式 capability 上。

---

## 4. 非目标（明确不做）

本次 P4 明确不做以下内容：

### 4.1 不重做执行中枢
不废弃 `packages`，不把 registry 做成新的主控制器。

### 4.2 不改变主架构
不改变现有主骨架：
- `specs/`
- `packages/`
- `projects/`
- `knowledge/`
- `templates/`
- `docs/`

### 4.3 不引入重型动态调度器
P4 不等于建立新的 workflow engine。  
当前主链仍由 execution hub spec 定义。

### 4.4 不把所有逻辑集中到一个文件
Capability Registry 集中的是“能力声明”，不是把所有实现逻辑搬到一起。

### 4.5 不强制所有未来能力都立刻插件化
P4 的重点是“先注册清楚”，不是“立刻做成 plugin 生态”。

---

## 5. P4 在整体架构中的定位

P4 应被理解为：

> **Execution Hub 的显式能力声明层（explicit capability declaration layer）**

它位于：
- `specs` 规则层之下
- `packages` 执行层之旁
- `runbook` 操作层之上

更具体说：

- `specs/` 负责定义规则与合同
- `packages/` 负责真实执行
- `Capability Registry` 负责登记：
  - 系统有哪些正式能力
  - 每个能力归属哪个阶段
  - 每个能力读取什么、写出什么
  - 每个能力有什么依赖与约束
- `runbook/AI/IDE` 则通过 Registry 更容易理解和消费能力

### 当前状态
```text
specs -> packages -> projects/runtime/workspace
```

### 引入 P4 后
```text
specs -> capability registry -> packages -> projects/runtime/workspace
```

注意：  
Registry 是 **声明层**，不是主控制器。  
真正干活的仍然是 `packages/...`。

---

## 6. P4 核心设计原则

### 6.1 声明优先
Registry 记录“能力是什么”，不记录“能力怎么具体实现”。

### 6.2 向后兼容
现有命令不被替代，现有 runbook 仍可工作。

### 6.3 轻治理，不重调度
Registry 只提供能力地图与最小治理，不引入重型调度引擎。

### 6.4 与现有目录语义一致
系统级能力注册信息应留在系统级目录，不写进项目级 `workspace/`。

### 6.5 支持未来扩展，但不提前过度设计
先把已有正式能力注册清楚，再考虑 hook / policy plugin / plugin loader。

### 6.6 能被人和 AI 同时消费
Registry 既要有机器可读结构，也要有简洁的人类说明。

---

## 7. 推荐结构设计

## 7.1 新增系统级目录（推荐）

在 `packages/` 下新增：

```text
packages/
  capability_registry/
    registry.yaml
    capabilities/
      task_bootstrap.yaml
      context_assemble.yaml
      facts_gate.yaml
      business_gate.yaml
      experience_gate.yaml
      validate_outputs.yaml
      coverage_check.yaml
      repair_plan.yaml
      repair_status.yaml
      repair_close.yaml
      archive_artifacts.yaml
```

### 为什么放在 `packages/`
因为当前仓库已经明确：
- `packages/` 是执行中枢层
- 固定执行步骤由 `packages/` 统一承载

Registry 本质上是对执行中枢能力的正式声明，因此放在 `packages/` 内最稳，不需要新增新的顶层主目录。

---

## 7.2 可选新增运行时快照（可选，不强制首轮实现）

在项目运行时，可选生成：

```text
projects/<project-id>/runtime/capabilities/
  capability_snapshot.json
```

它的作用不是定义能力，而是记录“本次任务实际可用的能力视图”。

首轮 P4 可以不做这一步，避免过重。

---

## 8. P4 的核心输出物

P4 至少应形成三类正式产物：

### 8.1 规则真源
- `specs/12_capability_registry_contract.md`

### 8.2 能力注册真源
- `packages/capability_registry/registry.yaml`
- `packages/capability_registry/capabilities/*.yaml`

### 8.3 面向执行的实现与文档
- `packages/capability_registry/*.py`（如需要）
- `docs/runbook/capability_registry_flow.md`
- `P4_implementation_backlog.md`

---

## 9. Capability Registry 的对象模型

P4 里，正式 capability 至少要回答以下问题：

- 这个能力叫什么
- 属于哪个阶段
- 入口命令是什么
- 需要什么输入
- 会产出什么
- 是否改写正式产物
- 能否重跑
- 是否需要人工确认
- 它依赖哪些上游能力
- 它是否面向未来的 command / hook / policy plugin 扩展开放

---

## 10. 与现有命令面的关系

当前 `packages/__main__.py` 已暴露正式命令。  
P4 不需要改变这些命令的主语义，而应：

### 保留
- `bootstrap`
- `assemble`
- `gate-facts`
- `gate-business`
- `gate-experience`
- `validate`
- `coverage`
- `repair-plan`
- `repair-status`
- `repair-close`
- `archive`

### 新增（可选）
为了让 Registry 更易被 AI/操作者消费，可以考虑新增：

```bash
python -m packages capabilities-list
python -m packages capability-show <capability-id>
```

但这属于体验增强项，不是 P4 首轮落地的硬前提。

---

## 11. 与未来 plugin / hook / policy plugin 的关系

Execution Hub 规格已经预留：

- command
- hook
- policy plugin
- plugin loader

Capability Registry 要做的是：

> 给这些未来扩展位预留统一的能力声明模型。

因此 P4 应支持 capability type 至少包括：

- `command`
- `stage_gate`
- `final_check`
- `repair`
- `archive`
- `hook`（未来）
- `policy_plugin`（未来）
- `plugin_loader`（未来）

但首轮实现时，只要求先注册 **当前已正式存在的能力**，不要为了未来扩展把系统做重。

---

## 12. 对现有项目结构的影响评估

### 不会改变的
- 主架构不变
- 三阶段主链不变
- 项目真相层分工不变
- `packages` 仍是唯一固定执行入口
- `specs` 仍是唯一规则真源

### 会增强的
- 能力识别更清晰
- AI 消费能力更稳定
- runbook 更容易写成能力视角
- 后续 Memory Layer 可挂在 capability 上
- 后续 plugin/hook 不容易乱

### 结论
P4 是 **结构增强**，不是 **架构改造**。

---

## 13. 典型能力示例（贴当前项目）

### 示例：`context_assemble`
- capability_id: `context_assemble`
- stage: `runtime`
- type: `command`
- entrypoint: `python -m packages assemble <project-id>`
- inputs:
  - `source/task_card.md`
  - task card 显式引用路径
- outputs:
  - `runtime/task_card_resolved.json`
  - `runtime/context_manifest.json`
  - `runtime/context_bundle/`
- dependencies:
  - `task_bootstrap`
- retryable: `true`
- review_required: `false`
- mutates_formal_artifacts: `false`
- mutates_runtime_state: `true`

### 示例：`repair_plan`
- capability_id: `repair_plan`
- stage: `repair`
- type: `command`
- entrypoint: `python -m packages repair-plan <project-id>`
- inputs:
  - `runtime/gates/*`
  - `workspace/check_*`
  - `runtime/trace_index.json`
- outputs:
  - `runtime/remediation/issue_index.json`
  - `runtime/remediation/remediation_plan.json`
  - `runtime/remediation/retry_scope.json`
  - `runtime/remediation/repair_summary.md`
- dependencies:
  - `validate_outputs`
  - `coverage_check`
- retryable: `true`
- review_required: `false`
- mutates_formal_artifacts: `false`
- mutates_runtime_state: `true`

---

## 14. 与 P3 的衔接

P4 先于 P3 的最大理由是：

> P4 先把“系统有哪些正式能力”定义清楚，  
> P3 才能去记“哪些能力常失败、常重跑、常触发 warning、常用于哪类任务”。

没有 Registry，Memory 只能挂在零散命令名上；  
有 Registry，Memory 就能挂在“正式能力对象”上。

---

## 15. 风险与应对

### 风险 1：把 Registry 做成新的执行入口
**后果：** 架构复杂化，和现有 execution hub 竞争。  
**应对：** Registry 只做声明，不做主执行。

### 风险 2：把所有逻辑搬到一个大表里
**后果：** 维护困难，逻辑与声明混杂。  
**应对：** Registry 只存元信息，逻辑仍留在原模块。

### 风险 3：首轮就做未来全部扩展
**后果：** 过度设计。  
**应对：** 首轮只注册当前正式能力。

### 风险 4：系统级 registry 写进项目级 workspace
**后果：** 打乱现有分层语义。  
**应对：** 系统级 registry 保持在 `packages/` 下。

---

## 16. P4 验收标准

P4 改造可视为完成，当以下条件同时满足：

### 16.1 规则完成
- `specs/12_capability_registry_contract.md` 已建立
- 与 `specs/01_execution_hub_spec.md` 的关系已说明清楚

### 16.2 注册完成
当前正式能力全部被登记，包括：
- bootstrap
- assemble
- gate-facts
- gate-business
- gate-experience
- validate
- coverage
- repair-plan
- repair-status
- repair-close
- archive

### 16.3 一致性完成
对于每个能力，都能明确：
- entrypoint
- inputs
- outputs
- stage
- dependency
- retryability
- review requirement

### 16.4 兼容完成
- 不破坏现有命令链
- 不要求改项目真相层结构
- 不改变现有 runbook 主流程

### 16.5 消费完成
IDE 里的 AI 可以仅依赖：
- capability registry
- execution hub spec
就较准确理解现有正式能力面

---

## 17. 实施顺序（推荐）

### Phase 1：先立规则
- 写 `specs/12_capability_registry_contract.md`

### Phase 2：再登记已有能力
- 建立 `packages/capability_registry/registry.yaml`
- 为现有正式能力创建 `capabilities/*.yaml`

### Phase 3：再补执行入口与 runbook
- 视需要加 `capabilities-list / capability-show`
- 补 `docs/runbook/capability_registry_flow.md`

### Phase 4：最后做一致性校验
- 检查 registry 与 `packages/__main__.py`
- 检查 registry 与 `specs/01_execution_hub_spec.md`
- 检查 registry 与 runbook 是否一致

---

## 18. 最终结论

对于当前 UX-Blueprinting 项目，P4 不是“改造架构”，而是：

> **把已有执行能力从隐式约定，升级为显式登记。**

它的价值不在于让系统更复杂，而在于：

- 更清楚
- 更易扩展
- 更利于 AI 消费
- 更利于后续 P3 Memory Layer 挂接
- 更贴合 harness 方法论中的 capability governance（能力治理）

P4 完成后，项目将从：

> **contract-driven + command-driven + runbook-assisted 的工作台**

增强为：

> **contract-driven + capability-declared + harness-style execution workbench**

且这一增强不改变现有主骨架，只补齐执行中枢的正式能力地图。
