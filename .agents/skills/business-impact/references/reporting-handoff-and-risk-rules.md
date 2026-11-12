# 报告、交接与风险规则

## 1. Markdown 报告

正式产物为 `spark-output/business-impact.md`。章节按主文件的输出结构组织。报告明确本轮属于问题影响、方案预测或效果后重估；无法量化时说明原因，数字和推荐均须可追溯。

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

- Page Spec：可读受影响对象、场景、价值方向和约束；不得把价值当作方案成立证据。
- Outcome Validation：可读方案引用、价值相关指标和估值窗口；不得把预测收益当效果证据。
- Data Visualization：可表达 Case、派生链、情景和敏感性；不得重算。
- Evidence Archive：仅人工允许后保存脱敏决策快照和血缘；不得写 Evidence/Baseline Store。
- Knowledge Wiki：不消费项目估值；稳定规则另行审阅。
- Evidence Govern、Root Cause：不得读取本包改变证据或因果结论。

使用 `downstream_handoffs[]` 明确目标技能、Payload 与 allowed/forbidden uses，默认最小权限。

Evidence Archive Handoff 不等于写入授权。只有用户明确批准 `approve_archive_decision_snapshot`，并由 Archive 再次校验字段白名单和敏感等级后，才允许长期保存聚合决策快照。

## 5. 重复运行与写入

只在本轮明确关联上一次预测时，保留用于对照的预测出处和可比范围。完成来源、计算、隐私和权限自检后再写入正式报告；写入失败时不得声明完成。长期留存由用户授权证据归档。

## 6. 多方案

多方案比较不是核心门禁。只有多个具体方案被明确提供且使用同一问题、人口、baseline、窗口、币种和价值规则时，才程序派生 `solution_comparison_view`。单方案正常完成，不把缺少替代方案列为数据缺口。
