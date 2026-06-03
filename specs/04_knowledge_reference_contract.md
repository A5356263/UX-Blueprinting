# Knowledge Reference Contract

## Goal

定义任务在主链路执行前后，如何按 `Summary First / Raw Later` 原则装配知识与设计参考。

## Single Source Of Judgment

知识选择唯一判断源：

- `projects/<project-id>/runtime/uxb_route_decision.json`

工程代码不得再根据以下信息自动补知识：

- `Domain`
- 关键词
- summary/source refs 邻接关系
- 默认 budget
- fallback 推荐

## Allowed Assembly Inputs

上下文装配只允许读取以下显式输入：

1. task card 中的 `template_refs`
2. task card 中的 `check_refs`
3. `uxb_route_decision.json.knowledge_selection.files`

## Reference Rules

- 所有引用必须是仓库相对路径。
- wildcard 引用不得直接复制到 `context_bundle/`。
- 如果 UXB 没有显式选择某个知识文件，代码不得自行补装。
- `knowledge_selection.files` 只声明本次任务计划读取的知识文件，不得自动扩张为整域全量读取。
- `knowledge_selection.reasoning` 只解释整体知识选择思路，不承担逐条工程字段对齐职责。

## Context Assembly Requirements

`context_assemble` 必须：

- 读取 `source/task_card.md`
- 读取 `runtime/uxb_route_decision.json`
- 校验显式 refs 是否存在
- 只复制模板、检查项和 UXB 显式登记 refs 到 `runtime/context_bundle/`
- 把装配结果统一记录到 `runtime/context_manifest.json`
- 同步产出 `runtime/knowledge_trace.json`

## Required Manifest Fields

`context_manifest.json` 至少包含：

- `task_card_source`
- `selection_source`
- `knowledge_trace`
- `assembled_refs`
- `missing_refs`
- `references`
- `reference_summary`
- `task_contract`
- `warnings`
- `strict_mode`

其中：

- `selection_source` 必须指向 `projects/<project-id>/runtime/uxb_route_decision.json`
- `knowledge_trace` 必须显式记录 `files / reasoning`
- `references[*].selected_by` 用于区分哪些材料由 `uxb_ai` 显式指定
- `context_manifest.json` 是唯一正式装配记录

## Prohibited Outputs

以下 runtime 文件不再是正式产物：

- `runtime/task_card_resolved.json`
- `runtime/knowledge_usage_report.json`

## Failure Conditions

- `uxb_route_decision.json` 中声明的 ref 不存在
- wildcard ref 被当成直接复制目标
- 引用无法复制进 `context_bundle/`
- `context_manifest.json` 未生成
