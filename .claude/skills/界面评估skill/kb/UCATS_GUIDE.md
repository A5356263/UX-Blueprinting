# UCATS 界面证据评分指南

本指南说明如何把截图、DOM、Accessibility Tree、runtime 状态和行为数据转成可复现的 UCATS 界面评估报告。检查项和扣分口径以 `ASSESSMENT_CRITERIA.md` 为准。

## 适用边界

可以直接评估：

- 页面、表单、列表、表格、看板、设置页、文章页、弹窗、错误状态、空状态和多步骤流程。
- 可从截图、DOM、A11Y、runtime 或 computed style 证明的结构、文案、状态、反馈和流程问题。

不能仅凭界面证据评估：

- 真实点击率、曝光度、完成率、完成时长、活跃率、PV/UV、满意度或用户口碑。
- 后端规则、真实权限、真实性能、真实数据质量和业务成功率。

不能仅凭行为数据评估：

- 具体界面原因，例如按钮是否可发现、文案是否清楚、布局是否合理。
- 具体设计改法。行为数据能定位异常，改法必须结合界面证据或进一步调研。

## 评分模型

走查评分使用截图表模型：

```text
信息呈现权重 = 0.35
操作体验权重 = 0.65
```

11 个检查元素先判断是否涉及：

- `applicable`：涉及且证据足够，表格值为 `1`。
- `evidence_insufficient`：任务需要但证据不足，表格值仍为 `1`，并降低置信度。
- `not_applicable`：确实不涉及，表格值为 `0`，权重为 `0`，不扣分。

元素权重只在涉及元素之间均分：

```text
元素内部权重 = 1 / 当前一级维度中涉及元素数量
```

扣分只按问题单元个数和档位计算，严重度不参与算术扣分：

```text
points_per_problem = 1 / 2^(scale_level - 1)
deduction_points = problem_count * points_per_problem
元素原始分 = 100 - sum(deduction_points) + element_adjustment
元素分 = clamp(元素原始分, 0, 100)
一级维度分 = clamp(sum(元素分 * 元素内部权重) + primary_adjustment, 0, 100)
走查总分 = clamp(信息呈现分 * 0.35 + 操作体验分 * 0.65, 0, 100)
```

如果只涉及一个一级维度，则该维度权重为 `1.0`，另一个为 `0`。两个一级维度都没有可判断证据时，报告无效，应请求补充截图、DOM、runtime 或任务上下文。

## 问题单元、档位与下限

`problem_count` 表示标准化后的问题单元数量，不等于 issue 条数。一个大问题如果只影响一个检查目标，仍可只记 1 个问题单元，但应通过 `High` 或 `Critical` 影响 gate；如果同一根因破坏多个检查目标，可以在不同元素下分别计问题单元，并说明不同影响路径。

分数不会变成负数：

```text
raw_element_score = 100 - sum(points) + adjustment
element_score = clamp(raw_element_score, 0, 100)
```

当 `raw_element_score < 0` 时，输出分数为 `0`。这表示该元素在当前任务中基本失效，不代表报告无效；报告是否有效取决于证据是否足够、路径是否可定位、问题单元是否去重、档位是否匹配评估范围。

默认整份报告使用同一档位；如不同元素覆盖范围明显不同，可以逐元素记录档位并解释。

| 档位 | 单题扣分 | 适用范围 |
| ---: | ---: | --- |
| 1 | 1 | 单组件、单状态、局部截图 |
| 2 | 0.5 | 小面板、弹窗、表单片段 |
| 3 | 0.25 | 一个完整页面的主任务区域 |
| 4 | 0.125 | 完整页面，多个区域或状态 |
| 5 | 0.0625 | 多页面或多状态任务流程 |
| 6 | 0.03125 | 复杂产品、批量页面、跨流程评估 |

`deductions[]` 推荐记录：

```json
{
  "issue_id": "iss_1",
  "criterion_id": "E1-01",
  "unit_scope": "region:filter_bar",
  "state_scope": "default",
  "expected": "筛选状态应在当前页面可见。",
  "actual": "核心筛选状态不够明确。",
  "evidence_test": "筛选条件没有可见摘要、选中状态或当前范围说明。",
  "problem_count": 3,
  "scale_level": 1,
  "points_per_problem": 1,
  "points": 3,
  "reason": "核心筛选状态不够明确。"
}
```

`points` 必须是正数。人工表写“扣 -3 分”时，JSON 写 `"points": 3`。

## 自动化校验

`scripts/ucats_report.py` 会校验：

- 非 `not_applicable` 元素的权重之和为 `1`，且在涉及元素间均分。
- `involved_elements` 等于非 `not_applicable` 元素 id 集合。
- 元素 `score` 由 `deductions[].points` 和 `adjustment` 重算得出。
- 如扣分项填写 `problem_count`、`scale_level` 或 `points_per_problem`，则必须填写 `criterion_id`、`unit_scope`、`state_scope`、`expected`、`actual`、`evidence_test`，且 `points = problem_count * 1 / 2^(scale_level - 1)`。
- 如果元素原始分小于 0，脚本会把元素分按 0 重算，并输出需要复核问题单元计数和档位的 warning。
- 一级维度 `score` 由元素分和元素权重重算得出。
- `ucats.walkthrough.overall_score` 由两个一级维度分和权重重算得出。
- `ucats.dimensions.clarity.score` 必须等于 `ucats.walkthrough.overall_score`。
- 未提供五个维度的独立证据时，`ucats.overall_score` 必须省略或为 `null`。
- 非清晰度维度若出现，必须引用 `input.behavior_metrics[n]` 等独立产品/行为证据，不能引用界面检查项。
- evidence 路径必须指向真实字段，不能把任务上下文、业务描述或生成元数据当界面证据。
- 每个 issue 至少被一个 recommendation 覆盖。

## 问题记录

每个 issue 必须包含：

- `id`
- `severity`
- `dimension`
- `title`
- `observation`
- `impact`
- `evidence`
- `source_refs`

严重度只用于排序和门禁：

- `Critical`：阻塞核心任务，或可能造成资金、数据、权限、安全、合规、不可逆损失。
- `High`：很可能导致任务失败、严重困惑、反复错误或明显流失；即使只有 1 个，也会触发 `review`。
- `Medium`：拖慢任务、增加理解成本、造成局部误操作或降低信任。
- `Low`：一致性、文案、视觉或局部效率问题，对任务完成影响有限。

同一根因不要在同一检查元素内重复计数。跨元素计数时，必须说明它分别破坏了不同检查目标。

## 调整项

调整项默认放在一级维度上，用于截图表中的“调整项分值”：

```text
一级维度分 = clamp(sum(元素分 * 元素内部权重) + adjustment, 0, 100)
```

规则：

- 没有明确证据时填 `0`。
- 非 0 时必须填写 `adjustment_reason` 和 `adjustment_evidence`。
- 单个一级维度建议控制在 `-10` 到 `+10`。
- 调整项不能抵消 `Critical` 问题或阻塞性缺陷。

## UCATS 维度边界

界面走查分只对应 UCATS `clarity`：

```text
ucats.dimensions.clarity.score = ucats.walkthrough.overall_score
```

11 个检查元素都不能映射到 `usability`、`task_completion`、`acceptance` 或 `stability`。这些维度只有在有独立产品/行为证据时才可评分，例如：

- `usability`：满意度、问题处理时长、无效点击、重复点击、操作耗时。
- `task_completion`：任务完成率、完成时长、漏斗流失、访问深度。
- `acceptance`：PV/UV、活跃率、核心功能使用率、留存或调研。
- `stability`：性能指标、错误率、崩溃率、接口失败、稳定性工单。

只有五个 UCATS 维度都有独立证据时，才输出完整综合分：

```text
overall =
  usability * 0.20 +
  clarity * 0.20 +
  task_completion * 0.25 +
  acceptance * 0.15 +
  stability * 0.20
```

只有界面证据时，输出 `clarity_score`，不要输出完整 `ucats.overall_score`。

## 置信度

置信度表示评分证据是否充分：

- `high`：DOM/A11Y/runtime/截图证据完整，关键状态可见，任务上下文明确，证据直接支撑评分。
- `medium`：部分证据缺失、截图裁切、缺少交互后状态、需要少量推断，或只有单一状态截图。
- `low`：关键状态不可见、文本不可读、任务上下文模糊，或结论主要依赖假设。

建议按以下因子估算：

```text
confidence_index =
  source_strength * 0.35 +
  state_coverage * 0.30 +
  traceability * 0.25 +
  context_clarity * 0.10
```

`confidence_index >= 0.80` 为 `high`，`0.55-0.79` 为 `medium`，低于 `0.55` 为 `low`。

## 门禁

- `fail`：清晰度分或完整 UCATS 总分 `<65`，或存在任一 `Critical`，或已评估的 `task_completion.confidence == low`。
- `review`：清晰度分或完整 UCATS 总分 `<80`，或存在任一 `High`，或任一已评估 UCATS 维度置信度为 `medium`。
- `pass`：不触发以上条件。

## 执行步骤

1. 明确输入模式：`browser`、`screenshot` 或 `mixed`。
2. 判定对象：完整业务界面、流程状态、加载/鉴权壳层或行为数据异常。
3. 生成 Page/Flow/Interaction DSL，只记录证据能证明的内容。
4. 按 11 个元素判断涉及性；证据不足但任务需要时用 `evidence_insufficient`。
5. 记录问题单元个数、档位、扣分、证据路径和建议。
6. 计算元素分、一级维度分、走查总分。
7. 将走查分写入 `ucats.dimensions.clarity.score`；只有五维都有独立证据时才重算完整综合分。
8. 输出报告：UCATS 清晰度得分 -> 一句话结论 -> 主要问题 -> 怎么改 -> 评分推导与不确定项。
