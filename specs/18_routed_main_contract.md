# Routed Main Contract

## Goal

`run-routed-main` 是按 UXB 已确认判断驱动的主链路执行入口。

## Entry Boundary

- `run-routed-main` 的执行判断只来自 `runtime/uxb_route_decision.json`
- 只允许 `--route auto`
- 不再接受手动 `fast / standard / full` 覆盖

## Required Preconditions

执行前必须检查：

- `runtime/uxb_route_decision.json` 存在
- `schema_version` 受支持
- `created_by == "uxb_ai"`
- `confirmed_by_user == true`
- `can_execute_mainline == true`
- `execution.required_outputs` 存在

若判断不足，必须停止并返回 `needs_rejudgment`。

## Runtime Products

至少产出：

- `runtime/routed_main_plan.json`
- `runtime/routed_main_report.json`
- 对应模式要求的 `workspace/*.md`

不再要求产出：

- `runtime/route_decision.json`

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

## Prohibited Behaviors

- 不得在执行中自动升级判断
- 不得在执行中自动降级判断
- 不得补写新的知识选择
- 不得替 UXB 改写 required outputs
- 不得把内部执行模式词汇写入用户可读正文
