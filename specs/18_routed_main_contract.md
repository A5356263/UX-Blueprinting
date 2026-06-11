# Routed Main Contract

## Goal

`run-routed-main` 是按 UXB 已确认判断驱动的正式蓝图主链路后续生成入口。

## Entry Boundary

- `run-routed-main` 的执行判断只来自 `runtime/uxb_route_decision.json`
- 只允许 `--route auto`
- 不再接受手动 `fast / standard / full` 覆盖
- 它不是“是否进入正式蓝图任务”的判断入口
- 它只承接“用户已经确认进入正式蓝图任务”之后的后续生成段

## Required Preconditions

执行前必须检查：

- `source/task_card.md` 存在
- `source/requirement.md` 存在
- `source/background.md` 存在
- 项目目录最小结构检查通过
- `source/requirement.md` / `source/background.md` 不得仍停留在 bootstrap 占位骨架
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
- `runtime/route_decision.md`
- `runtime/task_card_resolved.json`
- `runtime/knowledge_usage_report.json`

## Report Requirements

`routed_main_plan.json` 至少记录：

- `mainline_entry`
- `decision_source`
- `requested_route`
- `execution_mode`
- `planned_steps`
- `required_outputs`

不得记录：

- 完整 `uxb_route_decision` 对象
- `reason`
- `evidence`
- `matched_signals`
- `matched_terms`
- `guardrail_hints`

`routed_main_report.json` 至少记录：

- `mainline_entry`
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
