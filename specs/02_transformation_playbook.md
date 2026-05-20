# Transformation Playbook

## Goal

记录当前仓库已经收敛到的正式执行口径。

## Current Baseline

- `specs/` 是正式规则源
- `packages/` 是正式执行入口
- `projects/<project-id>/source/` 承载输入
- `projects/<project-id>/workspace/` 承载正式产物
- `projects/<project-id>/runtime/` 承载运行时状态与装配记录

## Fourth-Stage Baseline

- `runtime/uxb_route_decision.json` 是唯一判断源
- `runtime/context_manifest.json` 是唯一正式装配记录
- `task_card.md` 已降级为执行说明书
- generation 只消费已装配上下文

## No Longer Required

- `runtime/task_card_resolved.json`
- `runtime/knowledge_usage_report.json`
- `runtime/route_decision.json`

## Migration Principle

任何新的实现、模板、能力元数据和检查规则，都必须以这一套基线为准，不得再回写旧 runtime 口径。
