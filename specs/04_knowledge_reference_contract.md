# Knowledge Reference Contract

## Goal

定义任务如何引用 `knowledge/` 中的材料，以及执行期如何只按 UXB 已确认判断装配上下文。

## Source Of Judgment

- `projects/<project-id>/runtime/uxb_route_decision.json` 是知识选择的唯一判断源。
- 代码不得根据 `Domain`、关键词、summary、`source_refs`、默认 budget 或 fallback 规则自动补知识。
- `task_card.md`、`knowledge/wiki/index.md`、`knowledge/raw/*` 仍可作为显式引用材料存在，但它们本身不再触发自动知识选择。

## Knowledge Layer Responsibilities

- `knowledge/wiki/`：知识导航与摘要层，可被显式引用。
- `knowledge/raw/`：原始知识层，可被显式引用。
- `task_card.md`：声明任务边界、模板、检查项和可选知识入口。
- `uxb_route_decision.json`：声明本次任务实际需要装配的 `business_refs`、`guideline_refs`、`complexity_refs`。
- generation / validate：只消费已经装配进 `runtime/context_bundle/` 的材料。

## Allowed Assembly Inputs

上下文装配只允许从以下来源读取引用：

1. `task_card_resolved.json` 中的 `template_refs`
2. `task_card_resolved.json` 中的 `check_refs`
3. `uxb_route_decision.json.knowledge_selection.business_refs`
4. `uxb_route_decision.json.knowledge_selection.guideline_refs`
5. `uxb_route_decision.json.knowledge_selection.complexity_refs`

## Reference Rules

- 所有引用必须是仓库相对路径。
- 优先使用文件路径或稳定索引页路径。
- 目录引用仍允许作为显式输入存在，但只能做工程级收窄，不能触发额外语义判断。
- 通配符引用不能直接复制进 `context_bundle/`。
- 如果 `uxb_route_decision.json` 未显式选择某个知识文件，代码不得自行补装。

## Directory Narrowing Rules

当显式引用指向目录时，执行层只做工程级收窄，按以下顺序尝试：

1. 同目录下显式声明的 `Primary Knowledge Entry`
2. `README.md`
3. `index.md`
4. `*-index.md`
5. `*-domain-index.md`

如果找到稳定入口，只复制该入口文件。

如果没有稳定入口：

- 非 strict 模式：记录 warning，并允许目录 fallback copy
- strict 模式：直接失败

这里的 fallback 仅指“目录复制的工程降级”，不代表知识语义上的自动补全。

## Prohibited Behaviors

- 不得根据 summary 自动展开其 `source_refs`
- 不得把 summary 视为 raw 的自动入口
- 不得根据 guideline 关键词自动命中设计指南
- 不得根据 domain 自动注入业务知识
- 不得因为 refs 为空而自动推荐或补装知识
- 不得因为 refs 数量较多而自动截断或替换

## Context Assembly Requirements

`context_assemble` 必须：

- 读取 `task_card_resolved.json`
- 读取 `runtime/uxb_route_decision.json`
- 校验被选 refs 是否存在
- 仅复制显式模板、检查项和 UXB 已选择 refs 到 `runtime/context_bundle/`
- 记录实际装配结果，而不是重新生成选择理由

## Required Manifest Fields

`context_manifest.json` 至少包含：

- `selection_source`
- `references`
- `warnings`
- `strict_mode`
- `directory_refs_detected`
- `directory_refs_resolved_to_index`
- `directory_refs_fallback_copied`
- `narrowed_references`
- `facts_extraction_boundary`
- `business_judgment_boundary`
- `experience_translation_boundary`

其中：

- `selection_source` 必须指向 `projects/<project-id>/runtime/uxb_route_decision.json`
- `references[*].selected_by` 用于区分哪些材料由 `uxb_ai` 明确指定
- manifest 只记录装配结果，不再承载代码生成的知识消费计划

## Required Usage Report Fields

`knowledge_usage_report.json` 至少包含：

- `selection_source`
- `selected_refs`
- `assembled_refs`
- `missing_refs`
- `references`
- `assembly_details`

可选补充：

- `notes`
- `reference_summary`

报告语义应是“UXB 指定了什么、代码装了什么、缺了什么”，而不是“代码决定用了什么”。

## Failure Conditions

- `uxb_route_decision.json` 中声明的 ref 不存在
- 通配符引用被当成直接复制目标
- 引用无法复制进 `context_bundle/`
- `context_manifest.json` 未生成
- strict 模式下遇到无法收窄的目录引用

## Notes

- `summary` 与 `raw` 现在是平级可选材料，不再存在自动补链。
- `guideline`、`business`、`complexity` 三类 refs 只按 `knowledge_selection` 装配。
- task card 中保留 `Knowledge` / `Wiki` / `Design Guidelines` 章节的目的，是提供任务描述和显式入口，不是让代码替 UXB 做判断。
