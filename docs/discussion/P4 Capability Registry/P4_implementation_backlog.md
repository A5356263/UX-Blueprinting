# P4 Implementation Backlog
**Project:** UX-Blueprinting  
**Goal:** 在现有执行中枢基础上，落地 Capability Registry（能力注册层）  
**原则:** 增强，不重构；注册现有能力，不替代现有能力；保持 `specs / packages / projects / runtime / exports` 主骨架不变

---

## 0. 执行前共识（必须遵守）

- 不改变 facts / business / experience 三阶段主链
- 不改变 `source / workspace / runtime / exports` 分层
- 不把 Registry 做成新的主控制器
- 不废弃现有 `packages` 命令面
- 不把所有逻辑集中到 Registry
- 先登记已有正式能力，再考虑未来扩展

---

## 1. 基于当前仓库的关键事实（给施工 AI 的上下文）

### 当前主骨架已稳定
- `specs/`：唯一正式规则真源
- `packages/`：执行中枢
- `projects/`：项目真相
- `docs/`：解释与 runbook

### 当前执行入口已明确
`packages/__main__.py` 已正式暴露：
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

### Execution Hub 已预留未来扩展位
已明确提到：
- command
- hook
- policy plugin
- plugin loader

### 当前 `packages/README.md` 已把 `packages` 定义为执行中枢
所以 P4 最适合落在 `packages/` 内，不需要新增新的顶层主目录。

---

## 2. 本轮只做这 6 个任务

## Task 1 — 新增正式合同：`specs/12_capability_registry_contract.md`
### 目标
把 Capability Registry 正式纳入规则真源。

### 输入
- `specs/01_execution_hub_spec.md`
- `packages/__main__.py`
- 当前 P4 总方案文档

### 输出
- `specs/12_capability_registry_contract.md`

### 要求
合同必须明确：
- Capability Registry 的定位
- 与现有执行中枢的关系
- registry.yaml 的最小结构
- 单 capability 文件的最小字段
- 当前正式能力最小登记范围
- 与 `packages/__main__.py` / Execution Hub / runbook 的一致性要求
- 明确“增强，不重构”

### 完成标准
- 文件存在
- 风格与现有 `specs/*.md` 一致
- 没把 Registry 写成新的执行主控系统

---

## Task 2 — 新增系统级 Registry 目录
### 目标
建立正式能力登记目录。

### 新增目录
```text
packages/
  capability_registry/
    registry.yaml
    capabilities/
```

### 输出
- `packages/capability_registry/registry.yaml`
- `packages/capability_registry/capabilities/`

### 要求
- 保持在 `packages/` 内
- 不新增新的顶层主目录
- registry 是声明层，不是实现层

### 完成标准
- 目录存在
- registry 文件可被读取
- 不影响现有 `packages` 代码结构

---

## Task 3 — 为当前正式能力逐个建档
### 目标
把当前命令面正式能力全部注册。

### 必须覆盖的 capability
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

### 每个能力文件至少包含
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

### 完成标准
- 当前正式命令全部有独立 capability 文件
- `registry.yaml` 中 `capability_ids` 与这些文件一一对应
- 不登记未正式存在的能力为 `active`

---

## Task 4 — 增加 Registry 读取入口（轻量）
### 目标
让人和 AI 能读取 Capability Registry。

### 最小实现二选一
#### 方案 A（最轻）
先不加 CLI，只确保 Registry 文件结构清晰，能被直接读取。

#### 方案 B（推荐）
在 `packages/__main__.py` 新增：
- `capabilities-list`
- `capability-show <capability-id>`

### 要求
- 查询入口只读，不执行真实能力
- 不改变现有命令行为
- 输出稳定、简洁、面向人和 AI

### 完成标准
- 至少能方便查看当前正式能力面
- 不引入新的主控制器感

---

## Task 5 — 补 runbook 与 README 对齐
### 目标
让 Registry 不只是存在，还能被操作者理解。

### 输入
- `README.md`
- `packages/README.md`
- `docs/runbook/external_ai_quickstart.md`
- `docs/runbook/task_execution_flow.md`
- `docs/runbook/repair_loop_flow.md`

### 输出
- 新增 `docs/runbook/capability_registry_flow.md`
- 必要时小幅更新现有 README / runbook

### runbook 至少说明
- Capability Registry 是什么
- 它和现有命令面有什么区别
- 如何查看当前正式能力
- 如何理解某个 capability 的 inputs / outputs / dependencies
- 它为什么不等于 plugin 平台
- 为什么它不会改变现有架构

### 完成标准
- 人能读懂 P4 的价值
- 不和现有 runbook 主流程冲突

---

## Task 6 — 做一次一致性校验
### 目标
确保 Registry 不是“自说自话”。

### 必查三组一致性
1. `registry.yaml` vs `packages/__main__.py`
2. capability files vs `specs/01_execution_hub_spec.md`
3. capability files vs runbook

### 要求
至少回答：
- 每个 active command capability 是否都有正式入口
- 每个 capability 的 stage 归属是否和 Execution Hub 一致
- runbook 中提到的正式能力是否都被登记
- 是否有 registry 文件写了，但实现/文档并不存在

### 完成标准
- 有一致性检查记录
- 无明显遗漏能力
- 无明显冲突字段

---

## 3. 开发顺序（不要并行乱改）

### Phase 1：规则层
先做：
1. Task 1

### Phase 2：声明层
再做：
2. Task 2
3. Task 3

### Phase 3：消费层
再做：
4. Task 4
5. Task 5

### Phase 4：验证层
最后做：
6. Task 6

---

## 4. 明确不做的事

本轮不要做：

- 不做 Memory Layer
- 不做 AI Bridge
- 不做 plugin loader 真正实现
- 不做 hook / policy plugin 真正实现
- 不把 Registry 做成动态调度器
- 不改变项目真相层目录结构
- 不让 Registry 直接执行业务逻辑

---

## 5. 给 IDE AI 的执行方式

把下面 4 类材料一起喂给 IDE AI：

1. `P4_capability_registry_formal_upgrade_plan.md`
2. `specs/12_capability_registry_contract.md`
3. 本清单 `P4_implementation_backlog.md`
4. 当前仓库相关文件：
   - `README.md`
   - `packages/README.md`
   - `projects/README.md`
   - `specs/01_execution_hub_spec.md`
   - `packages/__main__.py`
   - `docs/runbook/external_ai_quickstart.md`
   - `docs/runbook/task_execution_flow.md`
   - `docs/runbook/repair_loop_flow.md`

然后要求它：

> 按本 backlog 顺序逐项完成；每完成一项，只改相关最少文件；每项完成后输出“改了哪些文件、为什么、如何验证”。

---

## 6. 一句话总原则

**先把现有能力登记清楚，再决定以后怎么扩展；Registry 负责声明，不负责替代执行。**
