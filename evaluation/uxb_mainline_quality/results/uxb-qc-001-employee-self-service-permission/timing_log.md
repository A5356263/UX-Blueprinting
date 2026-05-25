# 耗时记录：uxb-qc-001-employee-self-service-permission

## 1. 基本信息

- case-id：uxb-qc-001-employee-self-service-permission
- project-id：uxb-qc-001-employee-self-service-permission
- 执行时间：2026-05-25
- 执行环境：Windows 10, Python 3.x, PowerShell
- 执行人/AI：Claude Code
- 是否完整跑完：是（status: warning, 0 blockers）

## 2. 命令耗时记录

| 顺序 | 命令/动作 | 耗时 | exit code | 结果 |
|---|---|---|---|---|
| 1 | 创建测试项目与输入文件 (bootstrap + 写入源文件) | ~1s | 0 | 成功 |
| 2 | 生成 uxb_route_decision.json | ~60s | - | AI手动构建（含知识枚举和16条selection_reasons） |
| 3 | python -m packages route-decision | 0.14s | 0 | 通过 |
| 4 | python -m packages assemble | 0.20s | 0 | 25个引用装配成功，0个缺失 |
| 5 | 读取 context_bundle 知识文件 | ~90s | - | 读取5个核心知识文件（00_/14_/21_/24_/30_）和审批管理文件 |
| 6 | 生成 facts.md | ~5min | - | AI手动生成（基于需求文档+知识术语校准） |
| 7 | python -m packages generate-facts | <0.1s | 0 | 更新provenance |
| 8 | python -m packages gate-facts | 0.16s | 0 | 一次通过 |
| 9 | 生成 business_blueprint.md | ~8min | - | AI手动生成（含附录"事实+知识→判断"推导链路） |
| 10 | python -m packages generate-business | <0.1s | 0 | 更新provenance |
| 11 | python -m packages gate-business | 0.16s | 0 | 一次通过 |
| 12 | 读取设计准则知识文件 | ~60s | - | 读取5个guideline文件（IA/U/流程/认知/反馈） |
| 13 | 生成 experience_blueprint.md | ~10min | - | AI手动生成（含附录"设计指南消费说明"） |
| 14 | python -m packages generate-experience | <0.1s | 0 | 更新provenance |
| 15 | python -m packages gate-experience | 0.16s | 0 | 一次通过 |
| 16 | python -m packages validate | 0.23s | 0 | status: warning |
| 17 | python -m packages coverage | 0.22s | 0 | 通过 |
| 18 | 旁路评估报告生成 | ~8min | - | AI手动撰写（本文件对应项） |

## 3. 返工记录

| 阶段 | 返工次数 | 原因 | 处理方式 |
|---|---|---|---|
| route_decision | 0 | - | - |
| facts | 0 | - | 一次通过 |
| business | 0 | - | 一次通过 |
| experience | 0 | - | 一次通过 |
| validate/coverage | 0 | - | - |

## 4. 耗时分析

- 总耗时（命令执行）：~1.5s
- 总耗时（含AI生成）：约35分钟
- 最耗时阶段：experience_blueprint.md 手动撰写（~10min）——6个页面ASCII布局+26对状态反馈文案+10条设计指南消费说明
- 是否出现异常耗时：否
- 异常耗时原因：无
- 是否与上下文大小有关：否（25个引用对命令执行无影响）
- 是否与需求复杂度有关：是——低完整度（15个GAP需逐一评估）+ 复杂业务能力（三端侧×多状态×多风险）
- 是否与返工有关：否（所有gate一次通过）
- 是否建议优化链路：命令链路无需优化；AI生成耗时取决于需求复杂度，不是链路机制问题
