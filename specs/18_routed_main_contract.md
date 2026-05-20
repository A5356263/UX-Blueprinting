# Routed Main Contract

## Goal

`run-routed-main` 是按 UXB 已确认判断驱动的主链路执行入口。

## Entry Boundary

- `run-routed-main` 不改变 `run-main` 的默认存在方式
- `run-routed-main` 的执行判断只来自 `runtime/uxb_route_decision.json`
- 代码可以保留内部执行模式映射，但这些内部枚举不应成为用户可读判断源

## Route Selection

- 只允许 `--route auto`
- 不再接受手动 `fast / standard / full` 覆盖
- 执行模式由 `execution.required_outputs` 推导
- 如果 UXB 判断不完整或不允许执行，必须停止并返回 `needs_rejudgment`

## Required Preconditions

执行前必须检查：

- `runtime/uxb_route_decision.json` 存在
- `schema_version` 受支持
- `created_by == "uxb_ai"`
- `confirmed_by_user == true`
- `can_execute_mainline == true`
- `execution.required_outputs` 存在

## Execution Products

轻量模式至少产生：

- `workspace/facts.md`
- `workspace/business_note.md`
- `workspace/experience_blueprint.md`
- `runtime/routed_main_plan.json`
- `runtime/routed_main_report.json`

中等模式至少产生：

- `workspace/facts.md`
- `workspace/business_blueprint_lite.md`
- `workspace/experience_blueprint.md`
- `runtime/routed_main_plan.json`
- `runtime/routed_main_report.json`

完整模式复用现有完整主链路产物。

## Report Requirements

`routed_main_plan.json` 至少记录：

- `decision_source`
- `requested_route`
- `execution_mode`
- `planned_steps`
- `uxb_route_decision`

`routed_main_report.json` 至少记录：

- `status`
- `stopped_at`
- `steps`
- `actual_outputs`
- `execution_mode`

如判断不足，应记录：

- `status = needs_rejudgment`
- `blocking_issue`

## Prohibited Behaviors

- 不得在执行中自动升级判断
- 不得在执行中自动降级判断
- 不得补写新的知识选择
- 不得替 UXB 改写 required outputs
- 不得把内部执行模式词汇写入用户可读正文
- 不得修改正式 knowledge 系统作为测试输入
