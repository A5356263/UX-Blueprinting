# Route Decision Contract

## Goal

定义 `packages/route_decision` 在第四阶段后的职责边界。

## Positioning

`route_decision` 不再负责独立语义判断。

它现在只负责：

- 读取 `projects/<project-id>/runtime/uxb_route_decision.json`
- 做基础结构校验
- 生成一个临时执行镜像 `runtime/route_decision.json`

它不再负责：

- 基于 source 文件重新推导 route
- 生成新的 reason / evidence / guardrail
- 输出 `route_decision.md`
- 维护独立规则文件驱动的语义分类

## Input Boundary

唯一正式输入：

- `projects/<project-id>/runtime/uxb_route_decision.json`

不得再把以下文件作为 route 语义判断源：

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

如校验失败，应输出 `needs_rejudgment` 语义，而不是补写新判断。

## Output

必须输出：

- `projects/<project-id>/runtime/route_decision.json`

该文件只允许是临时执行镜像，至少包含：

- `version`
- `project_id`
- `status`
- `source`
- `can_execute_mainline`
- `required_outputs`
- `execution_mode`
- `validation_errors`
- `note`

其中 `note` 应明确说明：

- 这是临时执行镜像
- 不承载新的语义判断

## Prohibited Behaviors

- 不得生成新的 `route_decision.md`
- 不得读取旧 `rules.json` 做语义判断
- 不得输出新的 `reason`
- 不得输出新的 `evidence`
- 不得输出 `matched_signals`、`matched_terms`、`guardrail_hints`
- 不得成为用户可读正文输入

## Long-Term Direction

长期目标是进一步淡化 `route_decision.json` 的存在，只保留 `uxb_route_decision.json` 作为单一判断源。
