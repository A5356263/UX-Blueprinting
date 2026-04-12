# Capability Registry Flow

## 是什么

Capability Registry 是当前执行中枢的正式能力声明层。

它负责回答：

- 系统当前有哪些正式能力
- 每个能力属于哪个阶段
- 每个能力的正式入口是什么
- 每个能力依赖哪些输入、声明哪些输出
- 哪些能力会改写正式产物，哪些只会改写 runtime
- 哪些能力默认需要人工确认

Registry 不负责替代 `packages/` 的真实执行逻辑。  
真正执行任务的仍然是 `python -m packages ...` 命令面。

## 放在哪里

系统级声明位于：

```text
packages/capability_registry/
  registry.yaml
  capabilities/*.yaml
```

其中：

- `registry.yaml`：系统级能力总表
- `capabilities/*.yaml`：单能力治理字段

## 它和现有命令面的区别

区别如下：

- `packages/__main__.py`：负责正式执行入口
- `Capability Registry`：负责正式能力声明与查询消费面
- `specs/`：负责规则合同
- `runbook/`：负责操作说明

因此，Registry 是增强层，不是新的主控制器。

## 如何查看当前正式能力

可直接读取：

- `packages/capability_registry/registry.yaml`
- `packages/capability_registry/capabilities/*.yaml`

也可通过只读命令查看：

```bash
python -m packages capabilities-list
python -m packages capability-show <capability-id>
```

这两个命令只读取 Registry，不执行 facts / business / experience / repair / archive 能力本身。

## 如何理解一个 capability

读取单能力文件时，至少看以下字段：

- `capability_id`：稳定唯一标识
- `type`：command / stage_gate / final_check / repair / archive
- `stage`：所属阶段
- `entrypoint`：正式调用入口
- `required_inputs`：正式依赖输入
- `declared_outputs`：正式输出或副作用
- `dependencies`：上游 capability
- `retryable`：是否可重跑
- `review_required`：是否默认需要人工确认
- `mutates_formal_artifacts`：是否改写正式产物
- `mutates_runtime_state`：是否改写 runtime 状态

## 当前首轮登记范围

当前 Registry 已登记：

- 主链路能力：`task_bootstrap`、`context_assemble`
- 阶段闸门：`facts_gate`、`business_gate`、`experience_gate`
- 最终检查：`validate_outputs`、`coverage_check`
- 修复闭环：`repair_plan`、`repair_status`、`repair_accept`、`repair_defer`、`repair_close`
- 归档能力：`archive_artifacts`
- 查询能力：`capabilities_list`、`capability_show`
- memory 能力：`memory_extract`、`memory_accept`、`memory_summary`

## 为什么它不等于 plugin 平台

本轮 Registry 只做：

- 已有正式能力登记
- 最小治理字段补齐
- 统一查询消费面

本轮不做：

- plugin loader 真正实现
- hook / policy plugin 真正执行框架
- 动态调度器
- 新的主控制器

Registry 为未来扩展位保留统一模型，但不提前把系统做重。

## 为什么它不会改变现有架构

引入 Registry 后，保持不变的内容包括：

- `specs/` 仍是唯一规则真源
- `packages/` 仍是唯一固定执行入口
- `projects/<project-id>/` 仍是项目真相层
- facts / business / experience 三阶段主链不变
- Repair Loop 与 archive 的正式链路不变

变化只在于：

- 原本分散在命令、spec、runbook 中的隐式能力，被显式登记成 capability 对象

## 一句话原则

先把已有能力登记清楚，再让人和 AI 更稳定地消费；Registry 负责声明，不负责替代执行。
