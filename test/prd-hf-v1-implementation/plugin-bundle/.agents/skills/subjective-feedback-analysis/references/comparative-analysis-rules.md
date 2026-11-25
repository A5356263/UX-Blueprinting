read_frequency: on_demand
execution_critical: true

# 主观反馈对比分析规则

## 定位

对比分析负责对齐并描述两个反馈窗口的样本内变化，不判断干预效果。正式效果、护栏、分群伤害和归因由 `outcome-validation-recheck` 完成。

## 输入与可比性

至少识别 baseline window、comparison window 和两个窗口的反馈材料。存在改版或干预时记录说明，但不据此推断因果。

比较前检查：渠道范围、去重口径、主题规则版本、用户结构、时间窗长度、业务周期、同期活动、故障、政策和业务规则变化。

已有正式 baseline 时引用，不重新定义。用户只提供两个时期材料时可形成 `baseline_type=run_local_comparison`，必须 `reusable=false` 并记录 `comparability_status`。

## 允许输出

主题、情绪、紧急度和渠道结构的状态只允许：

```text
increased
decreased
stable
newly_observed
not_observed_in_current_sample
shifted
not_comparable
```

同时给出两个窗口的样本内数量、占比、分母、渠道和限制。“本期未观察到”不等于问题已解决；“再次观察到”不等于正式回归判定。

## 禁止

不得使用 `effective`、`ineffective`、`resolved`、`regressed`、`caused_by` 等效果或归因状态。不得评估指标护栏、发布完整性或根因生命周期。

