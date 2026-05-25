# 耗时记录：<case-id>

## 1. 基本信息

- case-id：
- project-id：
- 执行时间：
- 执行环境：
- 执行人 / AI：
- 是否完整跑完：是 / 否

## 2. 命令耗时记录

| 顺序 | 命令 / 动作 | 开始时间 | 结束时间 | 耗时 | exit code | 结果 |
|---:|---|---|---|---:|---:|---|
| 1 | 创建测试项目与输入文件 | | | | | |
| 2 | 生成 uxb_route_decision.json | | | | | |
| 3 | python -m packages route-decision <project-id> | | | | | |
| 4 | python -m packages assemble <project-id> | | | | | |
| 5 | python -m packages generate-facts <project-id> | | | | | |
| 6 | python -m packages gate-facts <project-id> | | | | | |
| 7 | python -m packages generate-business / lite / note <project-id> | | | | | |
| 8 | python -m packages gate-business / lite / note <project-id> | | | | | |
| 9 | python -m packages generate-experience <project-id> | | | | | |
| 10 | python -m packages gate-experience <project-id> | | | | | |
| 11 | python -m packages validate / validate-lite <project-id> | | | | | |
| 12 | python -m packages coverage / coverage-lite <project-id> | | | | | |
| 13 | python -m packages archive <project-id> | | | | | |
| 14 | 旁路评估报告生成 | | | | | |
| 15 | 汇总报告更新 | | | | | |

## 3. 返工记录

| 阶段 | 返工次数 | 原因 | 处理方式 |
|---|---:|---|---|
| route_decision | | | |
| facts | | | |
| business | | | |
| experience | | | |
| validate / coverage | | | |

## 4. 耗时分析

- 总耗时：
- 最耗时阶段：
- 是否出现异常耗时：
- 异常耗时原因：
- 是否与上下文大小有关：
- 是否与需求复杂度有关：
- 是否与返工有关：
- 是否建议优化链路：
