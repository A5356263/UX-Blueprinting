# 生命周期与模式候选规则

## Outcome 反馈刷新

只在 Evidence Govern 已吸收 reviewed Outcome 结果并形成 Root Cause 精确 Handoff 后执行。

三层语义不得混用：

- 反馈信号：`strengthened / weakened / contradicted / stable / resolution_observed / regression_observed / unknown`
- 生命周期状态：`active / pending_review / resolved / stale / reopened / rejected`
- Patch 动作：`retain / amend / mark_resolved / mark_stale / reopen / reject / request_review`

一次 `strengthened` 不自动改变生命周期；`mark_resolved`、`reopen` 和 `reject` 必须人工批准。所有 Patch 必须引用 Govern absorption，且 `can_auto_apply=false`。

## 历史相似性

比较机制、旅程节点、分群、症状组合、规则、情境因素、干预、效果、护栏和副作用。每次匹配同时记录相同维度和差异维度。

历史案例只能支持候选或验证方向，不替代当前证据，也不能直接提高当前 `causal_confidence`。

## 模式候选

至少需要两个：

- 可比；
- Outcome 已完成人工审查；
- 已被 Evidence Govern 吸收；
- 能说明共同机制、适用边界、失败条件和反例。

允许正向模式、负向模式、部分模式和情境依赖模式。案例不足时不生成正常 Pattern Candidate。

Root Cause 是唯一的模式候选生成者，但不得自动发布。交给 Knowledge Wiki 前还要经过人工 publication review 和 ingestion gate。单次候选根因、未经回检机制和治理方向不得入库。

## 未来自动化

当前技能只生成 Patch 和候选。持续拉数、调度、告警、自动重跑、状态写入与回滚属于延期的 Automation Controller，不在 Root Cause 2.0 内实现。
