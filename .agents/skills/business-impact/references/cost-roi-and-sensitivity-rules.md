# 成本、ROI 与敏感性规则

## 1. 估值层级

- `impact_only`：没有具体方案或可靠投入，不输出财务结果。
- `value_vs_effort`：有具体方案，输出价值方向与相对投入，不把等级换算成金额。
- `quantified_roi`：人口、baseline、effect、转化、采用、单位价值、归因、完整成本、币种和窗口均有引用。

缺少关键输入时自动降级。

## 2. 成本构成

按适用性检查：设计、研发、测试、数据、实施、迁移、运营、培训、支持、合规和维护。区分 `one_time | recurring`，记录团队、范围驱动因素、相对复杂度、成本区间、来源、不确定性和责任人。

Experience Blueprint 只能说明方案范围；工程、人天、报价、上线日期和预算必须来自用户、正式计划、负责人或有适用范围的正式基准。

## 3. 三情景区间

所有量化驱动使用 `low | base | high`，且 `low ≤ base ≤ high`。金额使用同一币种、价格口径和窗口。禁止单点伪精确值。

计算：

```text
expected_benefit = Σ 去重后的 metric value benefit
total_investment = Σ one-time cost + 观察期内 recurring cost
total_disbenefit = Σ 可量化负向影响
net_benefit = expected_benefit - total_investment - total_disbenefit
roi = net_benefit / total_investment
payback_period = total_investment / periodic_net_benefit
```

投入为零、未知，或 periodic net benefit 非正时，不输出对应 ROI/回收周期。

## 4. 必要门禁

量化 ROI 前必须有可追溯的：具体方案、估值窗口、人口范围、effect、采用率、单位价值、归因折扣、完整成本和去重策略。主观严重度、满意度或启发式等级不能直接换算金额。

长期项目按需使用折现；短期试点不强制。币种或窗口不可比时禁止汇总。

## 5. 敏感性

至少检查对结果影响最大的 effect、conversion、adoption、unit value、attribution 和 investment。输出参数变化对净收益/ROI 的方向与范围，不把敏感性情景写成预测事实。

未确认高敏感参数进入 `assumption_ledger`，预测状态不得超过 `provisional_forecast`。

## 6. 负向影响与不可补偿风险

同时计算 benefit、disbenefit 和 guardrail。关键分群受损、合规、安全、公平性或重大客户风险不得被高 ROI 抵消，必须进入人工评审。无法货币化的负向影响单独保留。

## 7. 非能力

不计算 break-even，不生成替代方案，不输出最终资源排序、预算、工期或立项结论。
