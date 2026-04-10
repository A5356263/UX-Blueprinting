# Project Sample Governance

## 样例治理清单

| 项目名 | 当前角色 | 当前状态 | 是否活跃 | 处置建议 | 是否可删 | 删除前依赖 |
| --- | --- | --- | --- | --- | --- | --- |
| demo-permission-v1 | golden sample（黄金样例）/ 迁移试点 | 协议已迁移，作为全链路默认演示项目 | 是 | 保留并持续收口为默认 end-to-end 样例 | 否 | 无 |
| demo-smoke-v1 | smoke sample（轻量冒烟样例） | 协议已迁移，作为轻量回归验证项目 | 是 | 保留并升级为轻量回归样例 | 否 | 若后续删除，需先明确替代样例并清理引用 |

## 分类结论

- 保留：`demo-permission-v1`、`demo-smoke-v1`
- 归档：当前无新增归档项目
- 删除候选：当前无删除候选项目

## 角色边界

- `demo-permission-v1`：用于完整复跑与对外演示，优先用于 onboarding 与主线讲解
- `demo-smoke-v1`：用于快速回归与链路健康检查，输入轻量、验证快速

## 治理动作记录

- 已统一两者 task card 到 v0.2 协议
- 已统一执行链入口为 `assemble -> gate-facts -> gate-business -> gate-experience -> validate -> coverage -> archive`
- 已清理旧命名残留（`01_facts* / 02_business* / 03_experience*`）
- 已补充样例索引文档并明确黄金样例与 smoke 样例分工
