# Stage Gate Report

## Summary

- status: warning
- has_blocker: false
- blocker_count: 0
- warning_count: 2
- info_count: 1

- project_id: 001
- stage: facts
- next_stage: business
- can_proceed: true

## Checked Files

- projects/001/source/task_card.md
- projects/001/source/requirement.md
- projects/001/source/background.md
- projects/001/runtime/task_card_resolved.json
- projects/001/runtime/context_manifest.json
- projects/001/runtime/provenance.json
- projects/001/workspace/facts.md

## Blockers

- none

## Warnings

- facts.md 可能越过阶段边界：包含 高保真视觉
- facts.md 仍包含占位内容

## Infos

- facts.md 已提炼 57 条事实
