# 关系图与价值表达规则

## 1. 保留生产者语义

关系图必须携带：

- `producer`
- `relation_type`
- `source_refs`
- `nodes[]`
- `edges[]`
- `confidence`
- `caveats[]`

Data Visualization 可以改变位置、颜色和标签密度，但不得新增、删除或升级关系。

| 生产者 | 允许表达 | 禁止改写 |
| --- | --- | --- |
| Evidence Govern | 支持、限制、矛盾、重复、情境影响 | 统一改为因果 |
| Root Cause | 候选机制、替代解释、反证、待验证项 | 候选根因改为最终根因 |
| Outcome | 干预、观测、归因、护栏、验证结论 | 弱归因改为已验证效果 |
| Business Impact | 问题、方案、指标影响、用户影响、业务价值 | 预测价值改为实际收益 |
| Heuristic | Finding、Evidence、Validation Request | 启发式风险改为用户事实 |

## 2. 桑基、漏斗与关系流

### Sankey

仅在每条边存在可比较的非负 `weight` 和统一 `weight_unit` 时使用。节点流入、流出无法解释时，必须写限制。

### Funnel

仅用于有顺序的阶段转化。阶段的分母变化必须由上游明确给出。不得从节点数量自行计算转化率。

### Relationship flow

用于没有定量流量的关系。边采用统一线宽；类型通过颜色、线型和文字标签区分。

### Mechanism chain

保留 Root Cause 的节点类型、候选状态、证据引用、替代解释与待验证状态。不得把链路布局理解为证明顺序。

## 3. Business Impact 价值链

只有 Business Impact 已输出 `impact_value_chains[]`，或用户给出完整 chart-ready 价值链时才绘制。

- 不强制固定五层。
- 不补齐缺失节点或跨层关系。
- `preliminary`、`evidence_backed`、`provisional_forecast`、`decision_ready_forecast`、`validated_revaluation` 必须原样标记。
- 价值范围、成本范围、ROI 和敏感性只展示上游结果，不重算。
- 若一条链混合观测事实和预测，逐节点标记 epistemic status。

## 4. 复杂度控制

- 优先展示主链，其他关系进入明细表。
- 节点超过可读范围时按上游已有分组折叠；不得自行合并不同语义节点。
- 反证、混杂、护栏和分群伤害不得因为“图更简洁”而隐藏。
