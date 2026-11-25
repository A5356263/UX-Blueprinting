read_frequency: on_demand
execution_critical: true

# Evidence Link, Context and Change Rules

## 关系类型

- `corroborates`：独立来源在可比范围支持同一现象。
- `counterevidence`：降低原判断支持程度，但未构成直接矛盾。
- `contradicts`：同口径和范围内不能同时成立。
- `qualifies_scope`：原判断只适用于特定范围。
- `non_independent`：同源或派生，不能计为独立互证。
- `unresolved_match`：可能相关但信息不足。

检查维度：

```text
用户或企业范围
任务、旅程或业务环节
可观察现象
时间窗口
产品、版本或场景
指标、问题分类或数据口径
```

`corroborates` 不表示因果。`evidence_link_confidence` 依据范围匹配、血缘完整和来源独立性判断，不能只按数量判断。

## 情境分类

```text
service_incident
product_change
operation_or_training
policy_or_process
measurement_or_data_change
population_or_scope_change
seasonality_or_external_event
other
```

最小判断：

```text
source refs
time overlap
scope overlap
possible effect direction
disposition
assessment confidence
rationale
```

Disposition：

```text
no_material_overlap
add_caveat
separate_scope
request_reanalysis
manual_review
unknown
```

Evidence Govern 不自行排除原始数据或重算指标。没有情境资料时使用 `unknown`，不得输出“未发现混杂”。

## 变化信号

- `strengthened`
- `weakened`
- `stable`
- `resolved`
- `stale`
- `contradicted`

变化信号必须引用当前与 prior Evidence/Baseline/Outcome。它可以触发 Patch 建议，但不能直接改变生命周期。

## 禁止

不得使用 `causes`、`drives`、`explains` 等因果关系。Root Cause 负责候选机制；Outcome 负责效果归因。
