# 耗时记录：uxb-qc-004-sub-admin-copy

## 1. 基本信息

- case-id：uxb-qc-004-sub-admin-copy
- project-id：uxb-qc-004-sub-admin-copy
- 执行时间：2026-05-25
- 执行环境：Windows 10, Python 3.x, PowerShell
- 执行人/AI：Claude Code
- 是否完整跑完：是（status: warning, 0 blockers）

## 2. 命令耗时记录

| 顺序 | 命令/动作 | 耗时 | exit code | 结果 |
|---|---|---|---|---|
| 1 | 创建测试项目与输入文件 | ~1s | 0 | 成功 |
| 2 | 生成 uxb_route_decision.json | ~30s | - | AI手动构建（10条biz+3条guide+13条reasons） |
| 3 | python -m packages route-decision | ~0.1s | 0 | 通过 |
| 4 | python -m packages assemble | ~0.2s | 0 | 22个引用装配 |
| 5 | 读取 context_bundle 知识文件 | ~30s | - | 读取31_翻牌叠加模式 |
| 6 | 生成 facts.md | ~4min | - | AI手动生成（10条明确规则+6项异常与边界） |
| 7 | python -m packages generate-facts | <0.1s | 0 | 更新provenance |
| 8 | python -m packages gate-facts | ~0.1s | 1→0 | 返工1次（缺少"异常与边界"章节） |
| 9 | 生成 business_blueprint.md | ~5min | - | AI手动生成（含31_翻牌叠加的知识引用） |
| 10 | python -m packages generate-business | <0.1s | 0 | 更新provenance |
| 11 | python -m packages gate-business | ~0.1s | 0 | 一次通过 |
| 12 | 生成 experience_blueprint.md | ~5min | - | AI手动生成（复制弹窗设计+4步校验+阻断文案） |
| 13 | python -m packages generate-experience | <0.1s | 0 | 更新provenance |
| 14 | python -m packages gate-experience | ~0.2s | 0 | 一次通过 |
| 15 | python -m packages validate | ~0.2s | 0 | status: warning |
| 16 | python -m packages coverage | ~0.2s | 0 | 2/4风险承接 |

## 3. 返工记录

| 阶段 | 返工次数 | 原因 | 处理方式 |
|---|---|---|---|
| facts | 1 | gate检测到缺少"异常与边界"章节（原文用了"已知规则缺陷"标题） | 重命名为"异常与边界"并调整内容结构 |
| business | 0 | - | 一次通过 |
| experience | 0 | - | 一次通过 |

## 4. 耗时分析

- 总耗时（命令执行）：~1.2s
- 总耗时（含AI生成）：约18分钟
- 最耗时阶段：business_blueprint + experience_blueprint 撰写（各约5分钟）
- 是否出现异常耗时：否
- 是否与返工有关：是（1次返工：facts章节重命名，约2分钟）
- 本用例信息相对完整，business推理可以基于31_翻牌叠加知识快速锚定核心规则——不需要像Case 001那样大量探索性推理
- 是否建议优化链路：命令链路无需优化。coverage的2/4风险承接提示了experience需要更显式地引用business中的风险条目
