# Knowledge Reference Contract

## Goal

定义主链路如何按 `Summary First / Raw Later` 原则装配知识与设计参考，并明确 `context_manifest.json` 的职责边界。

## Single Source Of Judgment

知识选择唯一判断源：

- `projects/<project-id>/runtime/uxb_route_decision.json`

工程代码不得再根据以下信息自动补知识：

- `domain`
- 关键词
- summary/source refs 邻接关系
- 默认 budget
- fallback 推荐

## Allowed Assembly Inputs

上下文装配只允许读取以下显式输入：

1. `task card` 中的 `template_refs`
2. `task card` 中的 `check_refs`
3. `uxb_route_decision.json.knowledge_selection.files`
4. `source/requirement.md`
5. `source/background.md`

## Reference Rules

- 所有引用必须是仓库相对路径。
- wildcard 引用不得直接复制到 `context_bundle/`。
- 如果 UXB 没有显式选择某个知识文件，代码不得自行补装。
- `knowledge_selection.files` 只声明本次任务计划读取的知识文件，不得自动扩展为整域全量读取。
- `knowledge_selection.reasoning` 只解释整体知识选择思路，不承担逐条工程字段对齐职责。

## Context Assembly Requirements

`context_assemble` 必须：

- 读取 `source/task_card.md`
- 读取 `runtime/uxb_route_decision.json`
- 读取 `source/requirement.md` 与 `source/background.md`
- 校验显式 refs 是否存在
- 把 `source/requirement.md` / `source/background.md` 作为 shared 正式输入装配到 `runtime/context_bundle/`
- 只复制模板、检查项和 UXB 显式登记 refs 到 `runtime/context_bundle/`
- 把装配结果统一记录到 `runtime/context_manifest.json`
- 不再单独产出 `runtime/knowledge_trace.json`

## Context Manifest Role

`context_manifest.json` 是：

- 后台装配记录
- 系统运行时消费的装配清单

它不是：

- `Agent` 交互状态单
- 阶段派单文件
- 大而全的运行中心文件

## Required Manifest Fields

`context_manifest.json` 至少包含：

- `task_card_source`
- `selection_source`
- `knowledge_trace`
- `assembled_refs`
- `missing_refs`
- `excluded_refs`
- `stage_contexts`
- `references`
- `task_contract`
- `warnings`
- `strict_mode`

其中：

- `selection_source` 必须指向 `projects/<project-id>/runtime/uxb_route_decision.json`
- `knowledge_trace` 必须显式记录 `files / reasoning`
- `excluded_refs` 用于记录装配阶段未进入上下文的引用及原因；当前默认允许为空
- `stage_contexts` 用于记录各阶段实际可读材料清单
- `references[*]` 只保留实际消费字段；未被 `generation / validate / knowledge loader` 消费的冗余说明字段不应继续写入正式 manifest

## Removed / Non-Required Fields

以下字段不再要求写入正式 `context_manifest.json`：

- `reference_summary`
- `stage_boundaries`
- `facts_extraction_boundary`
- `business_judgment_boundary`
- `experience_translation_boundary`

原则：

- 纯统计字段不进入正式 manifest
- 阶段边界说明字段不进入正式 manifest
- 如无真实消费方，不继续向 `context_manifest.json` 追加新字段

## Prohibited Outputs

以下 runtime 文件不再是正式产物：

- `runtime/task_card_resolved.json`
- `runtime/knowledge_usage_report.json`
- `runtime/knowledge_trace.json`

## Failure Conditions

- `uxb_route_decision.json` 中声明的 ref 不存在
- wildcard ref 被当成直接复制目标
- 引用无法复制进 `context_bundle/`
- `context_manifest.json` 未生成
