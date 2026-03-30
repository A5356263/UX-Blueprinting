# 31_experience_translation_requirements

## 必须显性暴露的信息

### 结果解释
- 必须能回答为什么有、为什么没有、来自哪里、谁改的、何时生效
- 当结果不可达、不可操作、不生效时，必须给出 `conflict_reason_code`

### 判定逻辑
- 必须显性暴露 `decision_chain`
- 必须显性暴露 `final_effective_rule`
- 当存在覆盖关系时，必须说明覆盖来源与失败层级

### 来源与边界
- 必须显性暴露 `source_enum`
- 当来源叠加时，必须说明 `source_priority`
- 当涉及协作权限时，必须显性暴露 `model_boundary` 与 `applicability`

### 可验证性
- 当涉及数据范围、条件组、交集或动态规则时，必须输出 `scope_expression`
- 必须定义可供追溯或验算的 `evaluatable_snapshot`

### 可追踪性
- 当涉及审批、生效、撤销或回收时，必须输出 `state_model` 与 `actor_responsibility`
- 当涉及批量、高危、不可逆操作时，必须输出 `audit_requirement`

### 查询闭环
- 至少明确 people、resource、change 三类查询语义中的现状承载与可行性
- 若现状做不到，必须暴露 `gaps`
