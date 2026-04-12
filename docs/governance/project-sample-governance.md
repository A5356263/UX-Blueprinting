# Project Sample Governance

## 样例治理清单

| 项目名 | 当前角色 | 当前状态 | 是否活跃 | 处置建议 | 是否可删 | 删除前依赖 |
| --- | --- | --- | --- | --- | --- | --- |
| real-self-apply-v1 | positive sample（正向标准样例） | 已按现行 09/10 spec 重生并通过全链路校验 | 是 | 长期保留，作为“新标准可通过”基准样例 | 否 | 无 |
| demo-smoke-v1 | negative sample（反向回归样例） | 保留旧摘要式产物，用于验证新 gate / validate 拦截效果 | 是 | 长期保留，作为“旧标准不可通过”基准样例 | 否 | 若后续删除，需先补替代反例并清理引用 |

## 分类结论

- 保留：`real-self-apply-v1`、`demo-smoke-v1`
- 归档：当前无新增归档项目

## 角色边界

- `real-self-apply-v1`：用于完整复跑、对外演示与正向验收，证明现行模板 + gate + validate 可通过
- `demo-smoke-v1`：用于反向回归，证明旧摘要式 business / experience 产物在现行标准下会被拦截

## 使用约束

- 两个样例目录都是长期基准案例，不用于承接新的日常任务。
- 后续真实任务必须使用新的 `project_id`，禁止复用 `real-self-apply-v1` 或 `demo-smoke-v1` 当作新任务工作区。
- 若要刷新样例，只能在明确“更新正例”或“更新反例”时定向修改。

## 治理动作记录

- 已统一保留样例的 task card 到 v0.2 协议
- 已统一执行链入口为 `assemble -> gate-facts -> gate-business -> gate-experience -> validate -> coverage -> archive`
- 已收敛样例集合为“一正一反”
