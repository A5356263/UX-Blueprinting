# 报告、交接与风险规则

## 1. JSON 与 Markdown

JSON 是唯一结构化事实源。交付载体只由 `requested_deliverables[]` 决定；Markdown 不能新增 JSON 中没有的数字、假设或推荐。

报告结构：

```text
§0 核心业务判断
§1 评估范围、输入与可信边界
§2 问题及受影响企业/用户
§3 用户、产品、服务、业务与组织影响
§4 不处理损失与可触达机会
§5 具体方案与指标价值映射（如有）
§6 投入、收益、ROI 与敏感性（条件满足时）
§7 业务价值视角与决策建议
§8 假设、缺口、风险与不可比较项
§9 下游交接
```

不具备量化条件时不保留空 ROI 章节，改为说明降级原因。`§0` 明确当前为问题影响、方案预测或效果后重估。

## 2. 敏感数据

包级 `data_classification` 使用 `internal | confidential | restricted`。每项成本和单位价值记录 `sensitivity` 与 `display_policy`。

- 不保存姓名、手机号、账号、客户明细或企业 ID 列表；
- 不复制完整预算、合同价格或客户收入明细；
- 可读报告默认隐藏 restricted 参数，使用区间、指数化或“受限数据”；
- 用户要求保留原始金额时仍限制下游访问；
- 错误信息不得泄露敏感值或本地私有路径。

## 3. 业务价值视角

`business_value_priority_view` 不是产品路线图。禁止 P0—P3、不透明总分和确定排期。只比较口径、窗口、币种和成熟度可比的 Case。

- Problem Impact：业务价值 × 证据成熟度；
- Solution Value：预期价值 × 相对投入 × 估值可信度。

最终立项、资源排序和排期由人工决定。

## 4. 下游权限

- Experience Blueprint：可读受影响对象、场景、价值方向和约束；不得把价值当作方案成立证据。
- Outcome Validation：可读方案引用、价值相关指标和估值窗口；不得把预测收益当效果证据。
- Data Visualization：可表达 Case、派生链、情景和敏感性；不得重算。
- Evidence Archive：仅人工允许后保存脱敏决策快照和血缘；不得写 Evidence/Baseline Store。
- Knowledge Wiki：不消费项目估值；稳定规则另行审阅。
- Evidence Govern、Root Cause：不得读取本包改变证据或因果结论。

使用 `downstream_handoffs[]` 明确目标技能、Payload 与 allowed/forbidden uses，默认最小权限。

Evidence Archive Handoff 不等于写入授权。只有用户明确批准 `approve_archive_decision_snapshot`，并由 Archive 再次校验字段白名单和敏感等级后，才允许长期保存聚合决策快照。

## 5. 重复运行与写入

不创建运行目录或 history log。普通运行只更新 latest。Validated Revaluation 只在显式引用上一预测时保留轻量 `prior_valuation_snapshot`；需要长期留存时由用户显式交给 Evidence Archive。

候选 JSON 先在临时位置 normalize/validate，通过后原子替换 latest。失败保留上一版，不得声明正式完成。

## 6. 多方案

多方案比较不是核心门禁。只有多个具体方案被明确提供且使用同一问题、人口、baseline、窗口、币种和价值规则时，才程序派生 `solution_comparison_view`。单方案正常完成，不把缺少替代方案列为数据缺口。
