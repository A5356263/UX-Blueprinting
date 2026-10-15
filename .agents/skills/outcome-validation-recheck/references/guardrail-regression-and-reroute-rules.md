# 护栏、回归与精准回流

## 1. 护栏与问题迁移

核心指标改善不代表体验整体改善。必须检查：

- 关键分群是否受损；
- 错误、投诉、人工介入或时长是否被转移到其他环节；
- 原问题是否以新形式出现；
- 新副作用是否超过可接受边界。

关键护栏或关键分群恶化时，不得给出单纯 `effective`。

## 2. 回归监测

当前技能只形成 `monitoring_requirements[]` 并评估已提供的监测结果，不持续拉数、不建定时任务、不配置监控平台。

要求至少描述指标、分群、baseline 和 caveat。阈值、频率、通知人必须来自正式政策引用，不能由技能自行设定。三类政策齐备时可标记 `ready_for_automation_controller`，但 `can_schedule` 始终为 `false`。

持续拉数、任务调度、平台配置、自动回滚、自动重跑和自动状态更新属于未来 Automation Controller，不在当前 Outcome 实现。

## 3. 精准回流

只回流受影响范围：

- 数据/口径/分群问题 → 对应分析技能；
- 证据强弱、冲突或陈旧 → Evidence Govern；
- 根因反馈 → 先由 Evidence Govern 吸收，再交 Root Cause；
- 估值需要已验证效果 → Business Impact；
- 全链路自动重跑始终为 `false`。

