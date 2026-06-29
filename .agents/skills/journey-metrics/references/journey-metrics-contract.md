# Journey Metrics Contract

This is the portable contract for the journey-metrics sidecar capability. It intentionally avoids assuming a specific UXB command runner.

## Purpose

Generate journey and tracking artifacts from UXB project inputs:

- Visual user journey: roles, paths, node details, gaps, conflicts.
- Journey tracking requirements: task lifecycle, taskNodeName events, parameters, node mapping.
- Error/exception/interruption tracking requirements: identify all user-visible interruption cases by journey first, then recommend Info4 according to the messageInfo enum. Do not pre-exclude modal/dialog cases during identification; modal/dialog cases remain in scope and must be represented with the actual online/test component form.

## Input Priority

1. `workspace/experience_blueprint.md`
   - Use as the journey skeleton.
   - Existing and requirement-added nodes can be `confirmed`.
2. `source/background.md`
   - Use when no experience blueprint exists.
   - Mark inferred context explicitly.
3. `source/requirement.md`
   - Use as the minimum input.
   - Mark most context completion as `inferred` and record gaps.

## Source Labels

Use exactly these labels:

| Label | Meaning |
|---|---|
| `confirmed` | Explicitly supported by the requirement, background, or experience blueprint. |
| `inferred` | Reasonable context completion that needs human review. |
| `conflict` | Requirement conflicts with trusted business knowledge; generate but flag. |

Keep conflict scope narrow. If only a field limit, parameter value, copy rule, or error threshold conflicts, mark the specific error scenario or parameter as `conflict`; keep the journey node and taskNodeName `confirmed` unless the existence, order, role, page, or action of the node itself is contradicted.

## Tracking API Contract

When a host project has `tracking_spec.md`, use it as the highest-priority local tracking specification. Otherwise use the host's tracking method document, such as `knowledge-root/raw/业务/埋点统一方法.md`.

User journey rules:

- `window.UX.startUserTask(taskName, taskId?)`, `window.UX.endUserTask()`, `window.UX.startUserSubTask(subTaskName)`, and `window.UX.endUserSubTask()` register or clear context only; they do not create node tracking events by themselves.
- Node tracking uses `<Button x-track-taskname="节点名称">` or manual `Util.trackData({ tasknodeName: '节点名称' }, TrackType.custom)`.
- Use exact casing `tasknodeName`.
- For non-button end nodes, emit the terminal node event before calling `endUserTask()` or `endUserSubTask()`.
- `taskId` may be omitted; the implementation can generate it from `taskName`. Generated specs should still recommend a searchable TaskID keyword.
- `taskName`, `subTaskName`, and `tasknodeName` should be stable, searchable, and business-readable. Uppercase English naming is recommended, not mandatory; it does not apply to `cust_id`, `info3`, or other messageInfo fields.

`TrackType.messageInfo` rules:

- Required fields: `cust_id`, `info`, `info4`.
- `cust_id` is the custom tracking name for the function module or business scenario. Base user, company, page, and task metadata is auto-added and must not be duplicated manually.
- `info` is the user-visible error message and must be non-empty after trimming. If no user-visible message can be extracted, skip the `messageInfo` event.
- Optional enhancement fields: `info2` for extra debugging context such as document number or field name, `info3` for error code or stable classification, `info5` for trigger source/action, and `traceid` for API tracing.
- `info5` should be `request` for API/backend errors. Frontend-triggered values should be stable action names and avoid generic values such as `click`.
- Known `info4` values: `FormError`, `Popover`, `message`, `result`, `AlertError`, `Toast`, `messageError`, `messageWarning`, `AlertWarning`, `resultWarning`, `resultError`, `modalConfirm`, `modalWarning`, `modalWarn`, `modalError`, `modalInfo`.

## Output Directory

```text
projects/<project-id>/workspace/journey_metrics/
```

Required files:

- `journey_visual.md`
- `journey_visual.html`
- `journey_tracking_spec.md`
- `error_tracking_spec.md`

Skip `journey_visual.html` only when the user explicitly requests Markdown-only output.

## Completion Gate

A generation run is incomplete until:

- `journey_visual.html` has been rendered from the generated journey nodes.
- `validate_journey_metrics.py <journey_metrics_dir>` passes.
- The host preview model, when present, has a non-empty `visual_html_path`.
- The user receives a local preview URL or direct file path for the rendered HTML.

## Markdown Parsing Contract

Preview adapters may rely on these structures:

- `journey_visual.md` must include `## 附录：节点-埋点对照`.
- The appendix table must include: `节点标识`, `节点名称`, `角色`, `来源`, `节点类型`, `关联 taskNodeName`.
- `journey_tracking_spec.md` event blocks must include `taskNodeName`, `节点描述`, `节点类型`, `所属任务`, `触发时机`, `所属页面/模块`, `对应旅程节点`, `来源`.
- `error_tracking_spec.md` error blocks must include `错误场景标识`, `触发条件`, `展示形式`, `展示位置`, `可见文案`, `事件ID`, `错误码`, `用户下一步`, `来源`.

## Preview Table Contract

Render journey tracking and error tracking by journey, one secondary tab per TaskName.

Journey tracking table name:

- 中文：用户旅程节点埋点表
- English: User Journey Task Node Tracking Table

Journey tracking columns:

- 任务场景/类型名称
- 旅程名称 TaskName
- 旅程编号 TaskID（给出建议关键词）
- 指定旅程关键节点名称 TaskNodeName
- 节点描述
- 节点类型：开始节点 / 中间节点 / 前端操作结束节点 / 任务成功结束节点
- 触发时机
- 所属页面/模块
- 对应用户旅程节点
- 依据状态（confirmed=已证实，inferred=推断，conflict=规则冲突）

Error tracking table name:

- 中文：报错/异常/中断埋点表
- English: Error, Exception and Interruption Tracking Table

Error tracking columns:

- 任务场景/类型名称
- 旅程名称 TaskName
- 旅程编号 TaskID（给出建议关键词）
- 报错信息 Info
- Info2（开发分析用额外信息，如单据号/批次号）
- Info3（错误码 errorCode 或分类标识）
- 推荐报错形式 Info4（FormError / Popover / message / result / AlertError / Toast / message* / result* / Alert* / modal*；以线上实际为准）
- 触发动作 Info5（request 或稳定触发动作；避免泛化 click）
- 触发条件/校验逻辑
- 报错上一个旅程节点名称
- 报错下一个旅程节点名称
- 依据状态

The error table must include an Info4 filter area and both tables must include tracking code examples.

## Failure Conditions

Treat the output as failed when:

- A required file is missing.
- A required section or table is missing.
- Any parameter or event uses `待定`, `TBD`, or equivalent placeholder text.
- A tracking event cannot be traced to a journey node.
- A journey tracking code example omits start node tracking, terminal node tracking, or clears journey context before emitting the terminal node event.
- A `TrackType.messageInfo` event omits `cust_id`, `info`, or `info4`, or uses empty `info`.
- Generated content invents roles, pages, or business rules that are not present in input or clearly marked as inferred.
