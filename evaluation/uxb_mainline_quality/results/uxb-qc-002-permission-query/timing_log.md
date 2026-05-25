# 耗时记录：uxb-qc-002-permission-query

## 1. 基本信息

- case-id：uxb-qc-002-permission-query
- project-id：uxb-qc-002-permission-query
- 执行时间：2026-05-25
- 执行环境：Windows 10, Python 3.x, PowerShell
- 执行人/AI：Claude Code
- 是否完整跑完：是（status: warning, 0 blockers）

## 2. 命令耗时记录

| 顺序 | 命令/动作 | 耗时 | exit code | 结果 |
|---|---|---|---|---|
| 1 | 创建测试项目与输入文件 | ~1s | 0 | 成功 |
| 2 | 生成 uxb_route_decision.json | ~30s | - | AI手动构建（6条biz+4条guide+10条reasons） |
| 3 | python -m packages route-decision | 0.11s | 0 | 通过 |
| 4 | python -m packages assemble | 0.19s | 0 | 19个引用装配 |
| 5 | 读取 context_bundle 知识文件 | ~60s | - | 读取12_查询与配置路径/04_对象关系/01_范围与边界 |
| 6 | 生成 facts.md | ~3min | - | AI手动生成 |
| 7 | python -m packages generate-facts | <0.1s | 0 | 更新provenance |
| 8 | python -m packages gate-facts | 0.13s | 0 | 一次通过 |
| 9 | 生成 business_blueprint_lite.md | ~5min | - | AI手动生成 |
| 10 | python -m packages generate-business-lite | <0.1s | 0 | 更新provenance |
| 11 | python -m packages gate-business-lite | 0.12s | 1→0 | 返工1次（章节标题→精确匹配合同） |
| 12 | 生成 experience_blueprint.md | ~3min | - | AI手动生成 |
| 13 | python -m packages generate-experience | <0.1s | 0 | 更新provenance |
| 14 | python -m packages gate-experience-lite | 0.16s | 1→0 | 返工1次（异常覆盖补充"用户→系统→下一步"结构） |
| 15 | python -m packages validate-lite | 0.15s | 0 | status: warning |
| 16 | python -m packages coverage-lite | 0.15s | 0 | 5/5信号覆盖 |

## 3. 返工记录

| 阶段 | 返工次数 | 原因 | 处理方式 |
|---|---|---|---|
| business-lite | 1 | 章节标题不匹配合同（"边界与范围"→"边界与风险"等4处） | 逐条修改为精确匹配合同的标题 |
| experience | 1 | 异常覆盖被检测为"仅覆盖happy path" | 补充4个异常场景的"用户操作→系统响应→用户下一步"三段式描述 |

## 4. 耗时分析

- 总耗时（命令执行）：~1.0s
- 总耗时（含AI生成）：约15分钟
- 最耗时阶段：business_blueprint_lite 手动撰写（~5min）——需要对照12_查询路径的知识进行推理
- 是否出现异常耗时：否
- 是否与返工有关：是（2次返工：章节标题+异常覆盖，每次约2-3分钟）
- 是否建议优化链路：命令链路无需优化。章节标题检查的严格性导致了可避免的返工——建议在contract中更突出地标注标题格式要求
