# Route Decision Contract

## Goal

定义 `packages/route_decision` 在正式蓝图主链路前半段中的职责边界。

## Positioning

`route_decision` 不再负责独立语义判断。

它现在只负责：

- 读取 `projects/<project-id>/runtime/uxb_route_decision.json`
- 做基础结构校验
- 输出确认结果或 `needs_rejudgment` 提示

它所处的位置是：

- 已完成 `bootstrap`
- 已写入正式输入
- 尚未进入 `run-routed-main` 后续生成段

它不再负责：

- 基于 source 文件重新推导 route
- 生成新的 reason / evidence / guardrail
- 生成 `runtime/route_decision.json`
- 生成 `route_decision.md`

## Input Boundary

唯一正式输入：

- `projects/<project-id>/runtime/uxb_route_decision.json`

不得把以下文件作为 route 语义判断源：

- `source/task_card.md`
- `source/requirement.md`
- `source/background.md`
- `runtime/context_manifest.json`

## Required Validation

至少校验：

- `schema_version`
- `created_by == "uxb_ai"`
- `confirmed_by_user == true`
- `can_execute_mainline == true`
- `execution.required_outputs` 存在
- `knowledge_selection.files` 为非空字符串列表
- `knowledge_selection.reasoning` 为非空字符串

校验失败时，应输出 `needs_rejudgment` 语义，而不是补写新判断。

## Output

该能力不再要求产出独立 runtime 文件。

它的正式效果只有：

- 标准输出中的确认信息或错误信息
- 命令退出码

## Prohibited Behaviors

- 不得生成新的 `route_decision.json`
- 不得读取旧规则文件做语义判断
- 不得输出新的 `reason`
- 不得输出新的 `evidence`
- 不得输出 `matched_signals`、`matched_terms`、`guardrail_hints`
