# 效果与归因规则

## 1. 两道独立门

`intervention_effectiveness` 回答“结果是否变好”；`attribution.strength` 回答“变化能在多大程度上归因于本次干预”。两者必须分开。

- 指标改善但同时有版本、运营、培训、故障、季节或口径变化时，可以是改善，但只能关联性归因；
- 无改善且暴露不足或实施不到位时，结论是 `not_evaluable`，不是 `ineffective`；
- 关键护栏或关键分群恶化时，总体结果只能是 `mixed` 或 `harmful`；
- `causal_supported` 只允许在混杂风险低且证据设计足以支持时使用；
- 高混杂风险只能是 `associational_only` 或 `unknown`。

## 2. 数据消费边界

Objective Data Analysis 提供统计结果、分群结果、基线比较、样本可靠性和影响规模。Outcome 消费这些正式结论，不重新计算统计量。

Subjective Feedback Analysis 和 Experience Heuristic Analysis 的新证据也必须先经 Evidence Govern 放行。Business Impact 的价值结果只能作为补充解释，不能替代主客观效果证据。

## 3. 结果等级

- `effective`：主要结果改善、关键护栏无实质伤害，且准备度满足；
- `partially_effective`：部分目标改善，存在范围或持续性限制；
- `mixed`：正负结果并存，尤其是关键分群/护栏受损；
- `harmful`：净影响明确偏负；
- `ineffective`：实施和暴露充分、观察条件有效但目标未改善；
- `not_evaluable`：输入、准备度或测量不足。

