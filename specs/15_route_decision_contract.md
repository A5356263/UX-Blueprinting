# Route Decision Contract

定义 `route_decision` 判断能力的规则边界、配置约束与输出契约。

## 职责边界

- `packages/route_decision/core.py` 只负责读取输入、加载规则、执行匹配、输出 `route_decision.json` 与 `route_decision.md`。
- 路线判断的需求类型、维度、关键词、路线升级策略、输出建议和置信度策略不得散落在 Python 代码中。
- 当前机器可读规则源为 `packages/route_decision/rules.json`。
- 如果后续需要调整 `fast / standard / full` 判断口径，优先修改规则文件，而不是改执行代码。

## 输入边界

初始路线判断可读取：

- `projects/<project-id>/source/task_card.md`
- `projects/<project-id>/source/requirement.md`
- `projects/<project-id>/source/background.md`
- `projects/<project-id>/runtime/task_card_resolved.json`
- `projects/<project-id>/runtime/context_manifest.json`

初始 route 判断不得依赖尚未生成的完整 `facts.md`、`business_blueprint.md` 或 `experience_blueprint.md`。

## 输出

必须输出：

- `projects/<project-id>/runtime/route_decision.json`
- `projects/<project-id>/runtime/route_decision.md`

`route_decision.json` 至少包含：

- `version`
- `rules_version`
- `project_id`
- `route`
- `confidence`
- `demand_type`
- `reason`
- `evidence`
- `dimension_judgment`
- `dimension_evidence`
- `design_pressure`
- `business_depth`
- `experience_focus`
- `non_focus_guidance`
- `escalation_signals`
- `should_not_control_mainline`

默认 `route_decision` 只提供路线建议，不控制主链路编排；因此 `should_not_control_mainline` 必须为 `true`。

## 规则文件要求

`packages/route_decision/rules.json` 必须至少声明：

- `demand_types`
- `signal_rules`
- `dimension_fields`
- `dimension_rules`
- `route_policy`
- `confidence_policy`
- `pressure_labels`
- `business_depth_by_route`
- `experience_focus_by_pressure`
- `non_focus_guidance_by_route`
- `escalation_signals_by_route`
- `reason_templates`

规则文件可以包含关键词，但关键词只能作为路线判断线索，不能写成“命中一个词就必然等于某条路线”的硬编码分类器。

## 禁止事项

- 不得让 route 判断替代 facts、business 或 experience 的正式判断。
- 不得让 route 判断直接改写 `run-main` 步骤。
- 不得自动降级路线。
- 不得把某个业务域的专有知识写成唯一判断逻辑。
- 不得为了小需求默认绕过业务依据。
