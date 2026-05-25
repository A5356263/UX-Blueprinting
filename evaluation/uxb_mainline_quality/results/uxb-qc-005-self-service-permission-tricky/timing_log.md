# 耗时记录：uxb-qc-005-self-service-permission-tricky

## 1. 基本信息

- case-id：uxb-qc-005-self-service-permission-tricky
- project-id：uxb-qc-005-self-service-permission-tricky
- 执行时间：2026-05-25
- 执行环境：Windows 10, Python 3.x, PowerShell
- 执行人/AI：Claude Code
- 是否完整跑完：是（status: warning, 0 blockers, 9 warnings）

## 2. 命令耗时记录

| 顺序 | 命令/动作 | 耗时 | exit code | 结果 |
|---|---|---|---|---|
| 1 | 创建测试项目与输入文件 | ~1s | 0 | 成功 |
| 2 | 生成 uxb_route_decision.json | ~60s | - | AI手动构建（11条biz+5条guide+16条reasons） |
| 3 | python -m packages route-decision | ~0.1s | 0 | 通过 |
| 4 | python -m packages assemble | ~0.2s | 0 | 引用装配 |
| 5 | 读取 context_bundle 知识文件 | ~60s | - | 读取21_/24_/30_三个核心文件 |
| 6 | 生成 facts.md | ~5min | - | 含6对冲突识别表和冲突分类 |
| 7 | python -m packages gate-facts | ~0.1s | 0 | 一次通过 |
| 8 | 生成 business_blueprint.md | ~5min | - | 含冲突立场表+知识依据 |
| 9 | python -m packages gate-business | ~0.1s | 0 | 一次通过 |
| 10 | 生成 experience_blueprint.md | ~3min | - | 返工1次（章节缺失→补全3-7节） |
| 11 | python -m packages gate-experience | ~0.2s | 0 | 通过 |
| 12 | python -m packages validate | ~0.2s | 0 | status: warning |
| 13 | python -m packages coverage | ~0.2s | 0 | 通过 |

## 3. 返工记录

| 阶段 | 返工次数 | 原因 | 处理方式 |
|---|---|---|---|
| experience | 1 | 章节3-7写了"略"，gate检测到缺失 | 补全全部章节 |

## 4. 耗时分析

- 命令总耗时：~1.2s
- AI生成总耗时：约15分钟
- 最耗时环节：facts（5min，含6对冲突识别表）+ business（5min，含冲突立场和知识推理）
- 与Case 001对比：facts和business耗时相当，但推理方向不同——Case 001侧重方案设计，Case 005侧重冲突识别
