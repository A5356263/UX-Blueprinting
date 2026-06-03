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

## Semantic Boundary

`gate / validate / coverage` 是轻量工程护栏，只允许发现问题，不允许替主 AI 做具体语义裁决。

允许检查：

- 必填章节是否存在
- 产物是否落在规定路径
- Markdown 与 JSON 状态是否一致
- blocker / warning / info 数量是否一致
- facts、business、experience 之间是否存在显性承接断点
- 是否存在明显模板骨架、占位残留或结构缺失
- 是否存在明显缺失的待确认问题
- 是否存在只复述事实、缺少判断落点的显著质量风险
- 是否存在主流程完整但异常与阻断明显缺失的显著体验风险

不允许检查器执行：

- 判断需求是否成立
- 判断值不值得做
- 判断能力形态是否正确
- 生成推荐业务方案
- 生成体验策略
- 替 AI 补充业务边界
- 根据关键词把需求归类成固定方案
- 根据领域、关键词、summary 自动补知识
- 将 coverage 演变为领域分类器或方案分类器

如果检查阶段发现判断不足，应输出 blocker / warning 并要求回到主 AI 重新判断；不得在 gate / validate / coverage 中自动补写判断。

## Runtime Contract Checks

校验器必须检查：

- `runtime/context_manifest.json` 存在且可读
- `context_manifest.json.task_contract` 存在
- `context_manifest.json.selection_source` 指向 `runtime/uxb_route_decision.json`
- `context_manifest.json.knowledge_trace` 存在
- `context_manifest.json.knowledge_trace.files` 存在
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

## Output Guidance

当发现业务判断不足、知识适用性不明、异常流程薄弱时，检查器只能记录问题与影响，不得自动修复语义内容。

允许输出的问题类型示例：

- `business 缺少需求不成立场景判断`
- `business 缺少系统代价评估`
- `experience 异常与阻断流程不足`
- `experience 未承接 business 中的风险边界`
- `coverage 发现承接断点，需要主 AI 重新判断`

禁止输出的问题类型示例：

- `本需求应做成全局配置`
- `本需求应采用弹窗方案`
- `该能力应归类为权限管理`
- `建议自动补充某业务知识`
