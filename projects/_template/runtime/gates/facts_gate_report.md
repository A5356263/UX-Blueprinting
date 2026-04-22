# Stage Gate Report

## Summary

- status: failed
- has_blocker: true
- blocker_count: 7
- warning_count: 1
- info_count: 1

- project_id: _template
- stage: facts
- next_stage: business
- can_proceed: false

## Checked Files

- projects/_template/source/task_card.md
- projects/_template/source/requirement.md
- projects/_template/source/background.md
- projects/_template/runtime/task_card_resolved.json
- projects/_template/runtime/context_manifest.json
- projects/_template/runtime/provenance.json
- projects/_template/workspace/facts.md

## Blockers

- provenance: provenance.source_hash 缺失
- provenance: provenance.task_card_hash 缺失
- 缺少文件：projects/_template/source/task_card.md
- 缺少文件：projects/_template/source/requirement.md
- 缺少文件：projects/_template/source/background.md
- 缺少文件：projects/_template/runtime/task_card_resolved.json
- 缺少文件：projects/_template/runtime/context_manifest.json

## Warnings

- facts.md 可能越过阶段边界：包含 高保真视觉

## Infos

- facts.md 已提炼 12 条事实
