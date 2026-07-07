# 规则与质量门禁

## 强制规则

1. DOM/Accessibility/runtime/截图证据至少要有一种作为主输入。不要只根据提示词、业务描述、源代码或既有 DSL 进行评分。
2. 在评分、诊断或建议前，必须先自动生成 Page/Flow/Interaction 证据 DSL；用户不需要也不应该被要求手写 DSL。
3. 每个结论都必须引用 DSL 证据。
4. 必须区分观察、推理和建议。
5. 不可见细节必须标记为 `uncertain`。
6. 必须区分页面级、流程级与交互状态级问题。
7. 必须区分可见界面问题与业务规则假设。
8. 除非证据中存在，不要声称隐藏状态、可访问性树细节、精确对比度、视觉遮挡、数据分析影响或后端行为。
9. 除非用户明确要求实现，否则不要生成前端代码。
10. 当用户要求自动化时，必须输出可由 `scripts/ucats_report.py` 校验的规范 JSON。
11. 没有多模态模型或截图证据时，可以评估语义清晰度、可访问性结构、状态反馈与表单表达是否清楚，但视觉布局、美观度、图片内容和像素级遮挡必须降置信度或标记为 `uncertain`。
12. Browser mode 必须执行 `DOM/Accessibility/runtime + prompt_context -> DSL`；Screenshot mode 必须执行 `screenshot + prompt_context -> DSL`；Mixed mode 必须执行证据合并和冲突标记。
13. 提示词中的 `interface_capabilities` 只能作为“界面声称应提供的能力”或任务验收标准；如果证据中找不到对应控件或反馈，应记录为缺失或 `uncertain`，不能直接写成已存在组件。
14. 前端行为数据、产品看板数据、埋点日志和反馈工单是行为数据证据，不是普通上下文。它们可以直接证明体验异常，但不能单独证明具体界面原因；具体原因和改法必须结合界面证据、提示内容、回放或进一步调研。
15. 自动化报告中的 evidence 路径必须指向可观察 DSL；只有具体行为指标可以指向 `input.behavior_metrics[n]`。不要把 `input.task_context`、`dsl.pages[n].task_context`、`generation`、`source`、提示词或业务描述直接当界面证据。
16. 每个 issue 必须至少被一个 `recommendations[].target_issue_ids` 覆盖；没有可执行建议的问题不能进入正式门禁报告。
17. `input.*[].ref`、`dsl.pages[].page_id`、`issues[].id`、`recommendations[].id` 必须唯一；证据来源和建议目标不能含糊或重复。
18. `adjustment` 非 0 时必须有 `adjustment_reason` 和 `adjustment_evidence`；没有证据的调整项不能参与评分。

## 证据要求

每个问题必须包含：

- `evidence`：一个或多个指向 DSL 的 JSON 指针风格路径。
- `source_refs`：一个或多个来源 id，例如 DOM、Accessibility、runtime 或截图。
- `observation`：证据中可见、可读或可机器抽取的内容或缺失项。
- `impact`：它为什么影响 UCATS `clarity`；非清晰度维度必须另有行为/产品证据。
- `recommendation`：应该如何修改。
- 对应的 `recommendations[].target_issue_ids`：至少一个建议必须覆盖该问题。

## 自动化质量门禁

以下情况报告无效：

- 没有 `dsl`。
- 没有自动生成的 Page DSL。
- 没有 `ucats.dimensions`。
- 任一维度分数不在 0-100 范围内。
- 任一问题缺少证据。
- 任一问题没有被建议覆盖。
- 任一建议缺少预期影响。
- 未先生成 DSL 就给出了评分或建议；默认人类报告可以不先展开完整 DSL，但内部必须已有可引用证据路径。

以下情况应标记为人工复核：

- 超过 30% 的关键 DSL 字段为 `uncertain`。
- 截图质量包含 `blurred`、`cropped` 或 `partial`。
- browser mode 中缺少 Accessibility Tree，且问题涉及可访问性或语义清晰度。
- 已提供独立行为数据且 Task Completion 置信度为 `low`。
- 存在改版前后对比，但截图顺序不确定。

## 合规检查清单

- 已记录输入来源元数据。
- 已抽取区域、组件与可见文本。
- 不可读、不可见、屏幕外或证据来源不支持判断的内容已标记为 uncertain。
- UCATS `clarity` 有证据和置信度；非清晰度维度若出现，必须有独立行为/产品证据。
- 问题严重度分配一致。
- 建议包含优先级、工作量、预期影响和目标证据。
- 自动化评估场景下，规范 JSON 可通过 CLI 校验。
