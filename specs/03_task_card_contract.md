# Task Card Contract

## Goal

定义 `projects/<project-id>/source/task_card.md` 的正式结构与执行边界。

## Positioning

`task_card.md` 是执行说明书，不是判断文件。

它负责：

- 描述任务目标、输入、输出、约束、模板、检查项和结果位置
- 给执行器提供可解析的模板与检查引用

它不负责：

- 复杂度判断
- 知识选择
- 执行深度或主链路准入判断

以上判断统一由 `projects/<project-id>/runtime/uxb_route_decision.json` 承担。

## Required Sections

必须存在：

- `## Protocol`
- `## Task Goal`
- `## Required Inputs`
- `## Required Outputs`
- `## Constraints`
- `## Templates`
- `## Checks`
- `## Result Locations`
- `## Completion Criteria`

可选但推荐：

- `## Task Scenario`
- `## Read Order`
- `## Platform Optimizations`
- `## Facts Output Requirements`
- `## Business Output Requirements`
- `## Experience Output Requirements`
- `## Notes`

## Protocol Fields

`## Protocol` 必须包含：

- `Protocol Name`
- `Protocol Version`
- `Task ID`

可选包含：

- `Task Name`
- `Domain`

`Domain` 仅为描述性字段，不再驱动代码自动选知识。

## Parsing Boundary

解析器只允许从 task card 中提取：

- 任务描述类字段
- `template_refs`
- `check_refs`
- 输出边界说明

解析器不得再从 task card 中提取或生成：

- `knowledge_refs`
- `wiki_refs`
- `guideline_refs`
- `primary_knowledge_entries`
- `fallback_source_refs`
- `fallback_conditions`
- `disallowed_broad_references`
- `has_directory_ref`
- `requires_narrowing`

## Runtime Behavior

task card 的解析结果只在运行时内存中使用，不再要求落盘生成 `runtime/task_card_resolved.json`。

执行期正式记录统一写入：

- `projects/<project-id>/runtime/context_manifest.json`

## Minimum Parsed Fields

- `task_id`
- `protocol_name`
- `protocol_version`
- `task_name`
- `domain`
- `task_goal`
- `task_scenario`
- `execution_constraints`
- `read_order`
- `notes`
- `required_inputs`
- `required_outputs`
- `template_refs`
- `check_refs`
- `result_locations`
- `completion_criteria`
- `facts_output_requirements`
- `business_output_requirements`
- `experience_output_requirements`
- `warnings`
- `errors`

## Failure Conditions

- `task_card.md` 缺失
- 缺少必需 section
- `Protocol Name` / `Protocol Version` / `Task ID` 缺失
- `Required Outputs` 为空
- 任一 output 路径不在 `projects/<project-id>/workspace/` 下
- `Templates` 或 `Checks` section 存在但无法解析为路径
- `Task Goal` 或 `Constraints` 无法解析为可读条目
