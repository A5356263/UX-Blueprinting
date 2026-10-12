# 统一启发式走查规则

按需用于 10 类走查、Finding 去重、Coverage、Severity 与 Evidence Promotion。

## 主分类

每条 Finding 只选择一个最能解释主要风险的 category：

| category | 检查重点 |
| --- | --- |
| `flow-continuity` | 入口、推进、返回、取消、终态和恢复路径 |
| `ia` | 导航、分组、层级、命名和任务可达性 |
| `components` | 项目设计系统、语义组件、token 与状态一致性 |
| `visual-hierarchy` | 主行动、信息层级、扫读与发现风险 |
| `edge-states` | 空、加载、错误、权限、网络、部分成功和极端数据态 |
| `copy` | 标签、按钮、术语、错误和帮助信息是否可理解、可行动 |
| `responsive` | 不同视口、设备、方向、溢出和触控线索 |
| `feedback` | 操作反馈、进度、防重复、确认、撤销与恢复 |
| `accessibility` | 可感知、可操作、可理解和语义健壮性的基础线索 |
| `brief-consistency` | 与明确 Brief、UXB、Stories、验收条件或蓝图的偏离 |

Nielsen 原则、视觉清晰度、WCAG 原则、平台和项目规则只写入 `heuristic_lenses[]` 或 `risk_tags[]`，不得生成第二条 Finding。

## Severity

- `blocker`：材料直接证明主任务无法继续、无恢复路径，或明确违反已确认红线。
- `major`：明显影响理解、完成、信任、可达性或关键状态恢复。
- `minor`：不阻断，但影响效率、一致性或清晰度。
- `note`：材料不足或需要进一步验证的观察。

Severity 不表示发生率、影响人数、业务价值或投入。未确认的规则风险不得标为 blocker。

## Finding 写法

必须区分：

- `observation`：材料中实际可见或可定位的事实；
- `risk_hypothesis`：该观察可能带来的体验风险；
- `design_attention`：后续设计必须解决的问题，不是具体方案。

禁止用“用户一定”“必然导致”“已验证根因”“建议使用某组件”等表述。

## 去重

使用 `finding_key` 跨透镜与跨运行识别同一问题。Key 由产品范围、页面或流程、任务节点或位置、状态、category 与 risk type 组成，不依赖整段自然语言。

- 同一位置、同一风险、多透镜命中：合并。
- 同一风险位于不同页面、流程或关键状态：可分开。
- 无法可靠判断：不强制合并，记录候选关联。

## Coverage

- `evaluated_with_findings`：已检查且有 Finding。
- `evaluated_no_finding`：现有材料下未发现风险，不等于完整审计通过。
- `not_evaluable`：范围内但材料不足，必须说明限制。
- `not_in_scope`：本次明确未检查，必须说明原因。

禁止用空数组、零 Finding 或 Coverage 状态生成整体 pass/fail。

## Evidence Promotion

Finding 必须同时满足来源可读、位置可定位、Observation/Risk 分开、规则、隐私和用途边界明确、无阻断性补证请求，才允许生成一个 Evidence。用户描述、Brief、规范或业务规则不能单独证明界面问题；`privacy_status=blocked` 时不得 Promotion。

每个 Finding 最多一个 Evidence。未通过时使用：

```text
evidence_status = not_promoted
not_promoted_reasons[]
```

Summary 只从去重后的 Findings 派生；Evidence 不重复计数。
