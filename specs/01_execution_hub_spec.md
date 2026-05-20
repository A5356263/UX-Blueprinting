# Execution Hub Spec

## Goal

定义执行中枢如何在第四阶段之后推进主链路。

## High-Level Flow

1. 读取 `source/task_card.md`
2. 读取 `runtime/uxb_route_decision.json`
3. 执行 context assemble，生成 `runtime/context_manifest.json` 和 `runtime/context_bundle/`
4. 生成 facts / business / experience 正式产物
5. 执行 gate / validate / coverage
6. 归档正式产物

## Runtime Principles

- `uxb_route_decision.json` 是唯一判断源
- `context_manifest.json` 是唯一正式装配记录
- `task_card.md` 只承载执行说明，不承载语义判断
- generation 只能消费已装配到 `context_bundle/` 的材料

## Removed Runtime Artifacts

以下文件不再是执行中枢正式产物：

- `runtime/task_card_resolved.json`
- `runtime/knowledge_usage_report.json`
- `runtime/route_decision.json`

## Strictness

- 缺少显式引用时必须报错，不得静默降级
- wildcard 引用不得直接复制
- 发现 UXB 判断不足时，必须返回 `needs_rejudgment`
