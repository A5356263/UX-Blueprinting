# 耗时记录：uxb-qc-006-permission-find-tricky

## 1. 基本信息

- case-id：uxb-qc-006-permission-find-tricky
- project-id：uxb-qc-006-permission-find-tricky
- 执行时间：2026-05-25
- 执行环境：Windows 10, Python 3.x, PowerShell
- 执行人/AI：Claude Code
- 是否完整跑完：是（status: warning, 0 blockers, 2 warnings）

## 2. 命令耗时记录

| 顺序 | 命令/动作 | 耗时 | exit code | 结果 |
|---|---|---|---|---|
| 1 | 创建测试项目与输入文件 | ~1s | 0 | 成功 |
| 2 | 生成 uxb_route_decision.json | ~30s | - | AI手动构建（2条biz+4条guide+6条reasons） |
| 3 | python -m packages route-decision | ~0.1s | 0 | 通过 |
| 4 | python -m packages assemble | ~0.2s | 0 | 引用装配 |
| 5 | 生成 facts.md | ~4min | - | 含4种矛盾说法的分类表+9项功能分类 |
| 6 | python -m packages gate-facts | ~0.1s | 0 | 一次通过 |
| 7 | 生成 business_note.md | ~3min | - | 核心判断：查找本次做，筛选拆出去 |
| 8 | python -m packages gate-business-note | ~0.1s | 0 | 一次通过 |
| 9 | 生成 experience_blueprint.md | ~3min | - | 仅设计查找交互，不含筛选 |
| 10 | python -m packages gate-experience-lite | ~0.2s | 0 | 返工1次（章节标题"页面设计"→"页面/弹窗/抽屉设计"） |
| 11 | python -m packages validate-lite | ~0.1s | 0 | status: warning |
| 12 | python -m packages coverage-lite | ~0.1s | 0 | 通过 |

## 3. 返工记录

| 阶段 | 返工次数 | 原因 | 处理方式 |
|---|---|---|---|
| experience | 1 | 章节标题不精确（"页面设计"→"页面/弹窗/抽屉设计"） | 修改标题 |

## 4. 耗时分析

- 命令总耗时：~1.0s
- AI生成总耗时：约12分钟
- 最耗时环节：facts（4min，含4种矛盾的分类识别）+ business_note（3min，含查找vs筛选区分逻辑）
- 与Case 003对比：AI生成耗时略多（12min vs 9min）——因为需要额外识别混淆语言并做出区分判断
