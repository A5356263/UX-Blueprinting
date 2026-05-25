# Check Contract

## Goal

定义 validate / coverage / stage gate 的正式检查口径。

## Formal Outputs

- `projects/<project-id>/workspace/check_report.md`
- `projects/<project-id>/workspace/check_status.json`

阶段 gate 对应输出：

- `projects/<project-id>/runtime/gates/*_gate_report.md`
- `projects/<project-id>/runtime/gates/*_gate_status.json`

## Status Levels

- `blocker`
- `warning`
- `info`

## Status Rules

- 存在 `blocker` 时，状态必须为 `failed`
- 不存在 `blocker` 但存在 `warning` 时，状态必须为 `warning`
- 同时不存在 `blocker` 和 `warning` 时，状态必须为 `passed`

## Runtime Contract Checks

校验器必须检查：

- `runtime/context_manifest.json` 存在且可读
- `context_manifest.json.task_contract` 存在
- `context_manifest.json.selection_source` 指向 `runtime/uxb_route_decision.json`
- `context_manifest.json.selected_refs` 存在
- `context_manifest.json.assembled_refs` 存在
- `context_manifest.json.missing_refs` 存在

校验器不再要求：

- `runtime/task_card_resolved.json`
- `runtime/knowledge_usage_report.json`
- `knowledge_consumption_plan`
- `source_ref_chains`

## UXB Decision Checks

主链路执行前必须存在：

- `runtime/uxb_route_decision.json`

并且：

- `confirmed_by_user == true`
- `can_execute_mainline == true`
- `execution.required_outputs` 存在

如果执行期发现判断不足，应返回 `needs_rejudgment`，而不是自动升级或补写判断。

## Consistency Rules

- Markdown 报告中的总状态必须与 JSON 一致
- blocker / warning / info 数量必须与 JSON 计数一致
- 被标记为 `failed` 的阶段不得在文档中伪装成“仅观察”
- JSON 中未出现的问题，不得仅靠 Markdown 当作正式 blocker
