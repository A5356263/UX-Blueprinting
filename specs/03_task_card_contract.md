# 任务卡片合同

## Goal

定义 `projects/<project-id>/source/task_card.md` 的正式结构与执行边界。

## Positioning

`task_card.md` 是工程入口，不是判断文件。

它负责：

- 提供稳定可解析的执行入口结构
- 声明输入、输出、约束、模板与检查引用

它不负责：

- 需求语义输入
- 复杂度判断
- 知识选择
- 执行深度或主链路准入判断

以上判断统一由 `projects/<project-id>/runtime/uxb_route_decision.json` 承担。

## Required Sections

必须存在：

- `## Protocol`
- `## Required Inputs`
- `## Required Outputs`
- `## Constraints`
- `## Templates`
- `## Checks`

## Protocol Fields

`## Protocol` 必须包含：

- `Protocol Name`
- `Protocol Version`
- `Task ID`

可选包含：

- `Task Name`
- `Domain`

说明：

- `Protocol Name`、`Protocol Version`、`Task ID` 等字段名当前属于解析稳定字段
- 如需整体中文化，应与解析器实现一并调整，不能只改模板或合同

`Domain` 仅为描述性字段，不再驱动代码自动选知识。

## Parsing Boundary

解析器只允许从 task card 中提取：

- `task_id`
- `protocol_name`
- `protocol_version`
- `task_name`
- `domain`
- `execution_constraints`
- `required_inputs`
- `required_outputs`
- `template_refs`
- `check_refs`

解析器不得再从 task card 中提取或生成：

- `task_goal`
- `task_scenario`
- `read_order`
- `notes`
- `knowledge_refs`
- `wiki_refs`
- `knowledge_selection.files`
- `knowledge_selection.reasoning`
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
- `execution_constraints`
- `required_inputs`
- `required_outputs`
- `template_refs`
- `check_refs`
- `warnings`
- `errors`

## Failure Conditions

- `task_card.md` 缺失
- 缺少必需 section
- `Protocol Name` / `Protocol Version` / `Task ID` 缺失
- `Required Outputs` 为空
- 任一 output 路径不在 `projects/<project-id>/workspace/` 内
- `Templates` 或 `Checks` section 存在但无法解析为路径
- `Constraints` 无法解析为可读条目
