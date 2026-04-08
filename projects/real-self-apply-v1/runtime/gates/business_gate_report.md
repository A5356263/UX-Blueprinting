# Stage Gate Report

## Summary

- project_id: real-self-apply-v1
- stage: business
- status: warning
- next_stage: experience
- can_proceed: true
- blocker_count: 0
- warning_count: 12
- info_count: 2

## Checked Files

- projects/real-self-apply-v1/workspace/facts.md
- projects/real-self-apply-v1/workspace/business_blueprint.md
- projects/real-self-apply-v1/runtime/gates/facts_gate_status.json

## Blockers

- none

## Warnings

- business_blueprint.md 仍使用旧结构，建议升级到 business review layer 模板
- business_blueprint.md 尚未显式建立领域基线
- business_blueprint.md 尚未显式给出能力归位判断
- business_blueprint.md 尚未显式比较备选路径
- business_blueprint.md 尚未显式给出判断追踪映射
- 部分事实尚未在 business_blueprint.md 中显式承接：F-03
- business_blueprint.md 尚未显式提炼判断标识（J-xx）
- business_blueprint.md 尚未显式提炼基线标识（BL-xx）
- business_blueprint.md 尚未显式提炼立场标识（POS-xx）
- business_blueprint.md 尚未显式提炼备选路径标识（OPT-xx）
- business_blueprint.md 尚未显式提炼风险或反模式标识（RSK-xx / AP-xx）
- 当前业务蓝图未显式保留 GAP 标识，建议确认关键缺口

## Infos

- facts 阶段状态：warning
- business_blueprint.md 已承接 11 条事实