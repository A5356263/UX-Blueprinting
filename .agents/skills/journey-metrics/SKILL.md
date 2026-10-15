---
name: journey-metrics
description: >
  旅程埋点与度量 Skill。基于体验蓝图或需求材料，输出视觉旅程图、埋点需求、异常追踪需求和预览集成约定。
  触发关键词：旅程埋点、埋点需求、旅程度量、旅程追踪、埋点清单、异常追踪、度量需求、追踪规格。
  仅在用户明确要求埋点、度量或追踪规格时使用；不得因用户只要求旅程图或工作区已有旅程产物而触发。
  排除：角色任务生命周期与旅程阶段分析（用 journey-analysis）。
---

# Journey Metrics

Use this skill as a sidecar UXB capability. It can run after an experience blueprint exists, or independently from requirement materials and optional background materials when time is tight. Keep generation, validation, and preview integration separate.

Do not automatically read existing project materials to decide the generation scope. When this skill is invoked, first ask the user which tasks or scenarios need visual journey and tracking requirement documents. Read files only after the user confirms the scope.

## Operating Model

Treat the capability as five layers:

1. **Generation layer**: create `journey_visual.md`, `journey_visual.html`, `journey_tracking_spec.md`, and `error_tracking_spec.md`.
2. **Contract layer**: enforce input priority, source labels, output structure, and failure conditions.
3. **Template layer**: use bundled Markdown templates from `assets/templates/`.
4. **Validation layer**: run `scripts/validate_journey_metrics.py` before calling the output complete.
5. **Preview adapter layer**: parse and render the generated files in the host project; do not assume the host uses this repository's preview code unchanged.

Do not present the preview renderer as the generator. The renderer only consumes files in the host `journey_metrics/` output directory.

## Inputs

Prefer inputs in this order:

1. Experience blueprint materials: reuse the journey and interaction sections as the highest-confidence skeleton.
2. Background materials: derive a role/path skeleton from scenario background.
3. Requirement materials: derive a minimal journey and mark inferred context explicitly.

当用户确认范围并选择 Experience Blueprint 作为正式输入时，执行以下硬门禁：

- 必须实际完整读取蓝图 Markdown；JSON 如存在，只用于快速定位，不是正式语义源。
- 即使蓝图刚在同一会话生成、当前上下文仍保留内容，也不得替代本次文件读取。
- 重点章节只决定二次核对优先级，不是正文白名单。
- JSON 与 Markdown 冲突时，以 Markdown 为正式语义源，并记录交接错误。
- 只有 JSON、Markdown 缺失或 Markdown 未读完时，不得生成旅程节点、埋点需求或异常追踪需求。
- 本门禁不改变先由用户确认任务或场景范围的现有入口规则。

如宿主项目提供本地埋点方法文档，必须读取并以其完整规范为最高优先级；否则从 `knowledge-wiki` 的 `knowledge/wiki/index.md` 开始，业务知识先按领域 README 选择正式文件，index 明确直达的单一设计知识直接进入，再按顶部导航只读命中的埋点方法、业务对象或状态章节。两者都不存在时，在定案参数与 API 细节前先索取或形成明确假设。

- 停止条件：命中局部知识后不得停止；问题涉及的主体、动作、条件、例外、结果及已触发依赖均有正式依据后再输出。
- 封闭枚举：仅以完整正式清单作答；未命中完整清单时，不得把局部事实表述为全集。
- 输出边界：以上仅作内部检查，不展示读取过程或检查项；证据不足影响正确性时，只说明必要边界。

## Outputs

Write all generated artifacts under the host-agreed journey-metrics output directory, for example:

```text
<output-root>/journey_metrics/
  journey_visual.md
  journey_visual.html
  journey_tracking_spec.md
  error_tracking_spec.md
```

Create `journey_visual.html` by default so the user can inspect the visual journey as rendered HTML. Keep it self-contained with inline CSS and JavaScript. Skip this file only when the user explicitly asks for Markdown-only output.

## Workflow

1. Ask the user which tasks or scenarios to generate. Do not infer the scope from files that happen to exist in the project.
2. After scope confirmation, inspect the host structure. Identify available input files, existing outputs, knowledge path, templates, and preview code.
3. Determine the input priority level and record it in `journey_visual.md`.
4. Generate the visual journey Markdown first. Every node must have a source label: `confirmed`, `inferred`, or `conflict`. Keep conflict scope narrow: field-level or parameter-level conflicts must not turn the whole journey node into `conflict` unless the node itself is contradicted.
5. Immediately render `journey_visual.html` from `journey_visual.md`. Prefer the bundled deterministic renderer:

```bash
python <skill-root>/scripts/render_journey_visual_html.py <journey_metrics_dir> --project-name <project-name>
```

Do not assume this exact command path already exists in every host. Reuse the bundled renderer or an equivalent host-exposed entrypoint. Do not wait for the user to ask for HTML rendering. This is a required generation step.

6. Generate journey tracking from the node list. Every tracking event must trace back to a journey node.
7. Generate error/exception/interruption tracking by journey first. Do not pre-exclude modal/dialog cases at identification time; record all user-visible interruption cases, then recommend `Info4` while noting that final form must follow the actual online/test-environment component.
8. Validate outputs with `scripts/validate_journey_metrics.py <journey_metrics_dir>`.
9. If the host has a preview adapter, rebuild preview and verify the "埋点需求" tab consumes `journey_visual.html`.
10. The final response must include either a local preview URL or a direct link/path to `journey_visual.html`. Do not finish with only Markdown document paths unless the user explicitly requested Markdown-only output.

## Completion Gate

Do not call the task complete until all of these are true:

- `journey_visual.html` exists in the output directory.
- The validator passes.
- If a preview adapter exists, the rebuilt preview model contains a non-empty `visual_html_path`.
- If a preview adapter exists, it renders the journey visualization only once: `journey_visual.html` is primary, parsed nodes are fallback only.
- If a preview adapter exists, `visual_html_path` is a browser-loadable URL relative to the preview output directory.
- The final answer tells the user where to open the rendered HTML visualization.

## Required Checks

Before finishing, verify:

- Required files exist.
- `journey_visual.html` exists unless the user explicitly requested Markdown-only output.
- `journey_visual.md` contains `## 附录：节点-埋点对照`.
- `journey_tracking_spec.md` contains taskNodeName event blocks and no `待定` / `TBD`.
- Every tracking event has `对应旅程节点` and `来源`.
- Journey tracking and error tracking preview tables are split by journey, one journey per secondary tab.
- Journey tracking code examples cover start context, start node tracking, intermediate node tracking, successful end node tracking, and `endUserTask` / `endUserSubTask` cleanup.
- Journey node payloads use exact field casing `tasknodeName`; `startUserTask` / `endUserTask` only manage context and do not emit node events by themselves.
- Journey tracking preview uses these columns: 任务场景/类型名称, TaskName, TaskID keyword, TaskNodeName, 节点描述, 节点类型, 触发时机, 所属页面/模块, 对应用户旅程节点, 依据状态.
- Error tracking preview uses messageInfo fields: Info, Info2, Info3, Info4, Info5, previous/next journey node, and evidence status. It must include an Info4 filter and code example.
- `TrackType.messageInfo` examples include required fields `cust_id`, non-empty user-visible `info`, and `info4`; `info2`, `info3`, `info5`, and `traceid` are optional enhancement fields.
- The preview adapter, if present, does not silently depend on old field names that the generated Markdown changed.

## Migration Guidance

When porting this capability to a newer UXB project, read `references/migration-guide.md` first. Port the layers separately:

- Bring the skill and templates as-is.
- Reconcile `references/journey-metrics-contract.md` with the new UXB rule system.
- Adapt preview parsing/rendering to the new preview model.
- Treat `assets/fixtures/` as regression fixtures, not production inputs.
- Add the CLI entrypoint only after the host command registry and packaging model are known.

## Handoff · 固定下一步

固定输出：

```text
旅程埋点与度量需求已完成。当前没有固定下一步推荐。
你可以停在这里。
```

**硬规则：正式产物写入并校验通过后，必须执行 `node shared-workflow/generate-progress-preview.js`；失败仅告警，不得阻断 Handoff。**

## Bundled Resources

- `references/journey-metrics-contract.md`: compact rule contract.
- `references/adapter-contract.md`: host integration points for CLI, knowledge, and preview.
- `references/migration-guide.md`: extraction and porting checklist.
- `assets/templates/`: Markdown templates and the standalone `journey_visual.html.template`.
- `assets/fixtures/demo-journey/`: known-good sample outputs.
- `scripts/render_journey_visual_html.py`: render `journey_visual.html` from the Markdown appendix.
- `scripts/validate_journey_metrics.py`: lightweight structural validator.
