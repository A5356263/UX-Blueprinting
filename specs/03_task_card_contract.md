# Task Card Contract

## Goal

定义 `projects/<project-id>/source/task_card.md` 的正式结构、路径规则与解析结果。

## Positioning

`task_card.md` 是任务执行入口合同，用于描述任务范围、显式引用、交付目标与阶段边界。

它不是：

- UXB 判断文件
- 知识自动选择规则文件
- 复杂度自动分类文件

`runtime/uxb_route_decision.json` 才是执行判断与知识选择的唯一正式来源。

## Required Sections

必须存在并可机读：

- `## Protocol`
- `## Task Goal`
- `## Required Inputs`
- `## Required Outputs`
- `## Constraints`
- `## Templates`
- `## Checks`
- `## Result Locations`
- `## Completion Criteria`

推荐但可选：

- `## Task Scenario`
- `## Read Order`
- `## Knowledge`
- `## Wiki`
- `## Design Guidelines`
- `## Knowledge Consumption Policy`
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

`Domain` 现在只作为描述性字段保留，不再驱动代码自动选知识。

## Knowledge Reference Rules

- `Knowledge` / `Wiki` / `Design Guidelines` 可以作为显式入口存在
- 这些入口不会自动触发知识装配
- 真正装配哪些 refs，以 `uxb_route_decision.json.knowledge_selection` 为准
- `Templates` 与 `Checks` 仍由 task card 直接声明并装配

## Knowledge Consumption Policy

如果保留 `## Knowledge Consumption Policy`，其作用仅限于：

- 解释显式目录引用的工程收窄方式
- 说明哪些 broad reference 不应被直接整目录复制

它不再承担：

- fallback raw 自动补全策略
- summary 命中后自动展开策略
- 业务知识自动选择策略

## Parse Output

执行必须生成：

- `projects/<project-id>/runtime/task_card_resolved.json`

最小字段：

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
- `knowledge_refs`
- `wiki_refs`
- `guideline_refs`
- `template_refs`
- `check_refs`
- `primary_knowledge_entries`
- `fallback_source_refs`
- `fallback_conditions`
- `disallowed_broad_references`
- `reference_granularity`
- `has_directory_ref`
- `requires_narrowing`
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
- 引用 section 存在但无法解析为路径
- `Task Goal` 或 `Constraints` 无法解析为可读条目
- `task_card_resolved.json` 未生成
