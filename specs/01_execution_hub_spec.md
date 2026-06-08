# Execution Hub Spec

## Goal

定义执行中枢如何承接“用户已确认进入正式蓝图任务”之后的主链路内部执行顺序。

## High-Level Flow

1. 用户在任务摘要后明确确认“进入正式蓝图任务”
2. 执行 `bootstrap`，创建项目目录与输入骨架
3. 用已确认分析结论覆盖 `source/requirement.md` / `source/background.md`
4. 写入并校验 `runtime/uxb_route_decision.json`
5. 执行 `run-routed-main`，继续 `context assemble`
6. 生成 facts / business / experience 正式产物
7. 执行 gate / validate / coverage
8. 归档正式产物

## Runtime Principles

- `uxb_route_decision.json` 是唯一判断源
- `context_manifest.json` 是唯一正式装配记录
- `task_card.md` 只承载执行说明，不承载语义判断
- generation 只能消费已装配到 `context_bundle/` 的材料
- `bootstrap` / 正式输入 / 判断单校验属于主链路前半段，不再视为主链路外准备动作

## Removed Runtime Artifacts

以下文件不再是执行中枢正式产物：

- `runtime/task_card_resolved.json`
- `runtime/knowledge_usage_report.json`
- `runtime/route_decision.json`

## Strictness

- 缺少显式引用时必须报错，不得静默降级
- wildcard 引用不得直接复制
- 发现 UXB 判断不足时，必须返回 `needs_rejudgment`
