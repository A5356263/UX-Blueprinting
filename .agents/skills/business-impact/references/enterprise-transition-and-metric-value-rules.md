# 企业转化与指标价值规则

## 1. 适用条件

仅在估值涉及企业/用户状态转化或“指标变化 → 业务价值”时读取。这里保存通用模型，不保存月活、深度月活、存续等具体业务定义或实际转化率。

## 2. 企业状态输入契约

上游结构化结论必须能追溯到：

- 同一规范化企业 ID；
- 明确统计月或观察窗口；
- 每个企业在该窗口内的状态快照；
- 企业分群和状态规则版本；
- 方案计划覆盖、实际曝光和采用状态；
- 唯一任务实例、任务类型和完成状态。

跨表 ID 无交集、窗口不一致或方案曝光缺失时，只能输出数据缺口，不得输出转化数量。Business Impact 正式包不保存企业 ID 列表，只保存聚合范围和来源引用。

## 3. 资格规则不等于转化概率

企业类型与转化规则只能判断哪些企业满足资格。实际转化概率必须来自历史可比数据、试点/实验、Outcome Validation，或明确的情景假设。

仅有覆盖企业和分群完成率差异时可以描述差异，不能归因于方案。选择偏差、原始活跃度和分群差异由 Outcome Validation 处理。

## 4. Metric Value Link

`metric_value_links[]` 是计算事实源，每项至少包含：

- metric、`baseline_input_ref` 与时间窗口引用；
- effect status：`forecast_scenario | validated_result`；
- effect range 与来源；
- addressable volume、adoption、conversion、attribution 与 unit value 三情景参数；
- value unit/currency、period count、dedup group；
- 允许用途和限制。

通用情景模型：

```text
expected_benefit
= addressable_volume
× metric_change
× conversion_rate
× adoption_rate
× attribution_discount
× unit_value
```

某些指标已直接表达转化数量时，使用显式公式类型避免重复乘 conversion。公式类型必须由 Schema 枚举，不接受自然语言公式。

## 5. Forecast 与 Validated Revaluation

- `forecast`：effect 来自正式历史依据或情景假设；不得声明实际效果。
- `validated_revaluation`：effect 必须引用 Outcome Validation 放行结果；Business Impact 不重新判断 baseline、对照或因果有效性。

预测总结必须使用“在这些条件下可能/预计”；验证后重估仍只声明价值估算，不把业务价值反写成效果证据。

## 6. Impact Value Chain

程序从 Problem Case、Solution Case 和 Metric Value Link 派生：

```text
问题 → 受影响对象 → 当前指标 → 具体方案 → 指标变化 → 状态转化 → 业务价值
```

派生链用于报告与可视化，不作为计算输入。链路缺失时停在可证实节点，不补造后续数字。

`value_vs_effort` 不创建带金额参数的 `metric_value_links[]`，改用 `qualitative_value_links[]` 保存价值方向、相关指标、说明和来源。它不是量化收益的替代字段。

## 7. 去重

同一企业、同一价值事件、同一窗口只能计入一次。多个指标指向同一最终收益时共享 `dedup_group`，汇总只采用一条主价值路径或经证明互斥的部分。
