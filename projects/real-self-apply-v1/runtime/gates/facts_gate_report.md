# Stage Gate Report

## Summary

- project_id: real-self-apply-v1
- stage: facts
- status: warning
- next_stage: business
- can_proceed: true
- blocker_count: 0
- warning_count: 8
- info_count: 1

## Checked Files

- projects/real-self-apply-v1/source/task_card.md
- projects/real-self-apply-v1/source/requirement.md
- projects/real-self-apply-v1/source/background.md
- projects/real-self-apply-v1/runtime/task_card_resolved.json
- projects/real-self-apply-v1/runtime/context_manifest.json
- projects/real-self-apply-v1/workspace/facts.md

## Blockers

- none

## Warnings

- facts.md 仍使用旧结构，建议升级到结构化提取层模板
- facts.md 尚未显式提炼规则标识（R-xx）
- facts.md 尚未显式提炼状态标识（S-xx）
- facts.md 尚未显式提炼动作标识（A-xx）
- facts.md 尚未显式提炼异常标识（EX-xx）
- facts.md 尚未显式提炼依赖标识（D-xx）
- facts.md 尚未显式提炼范围标识（SC-xx）
- facts.md 追踪映射信息较弱，建议补充标识到来源的映射关系

## Infos

- facts.md 已提炼 12 条事实