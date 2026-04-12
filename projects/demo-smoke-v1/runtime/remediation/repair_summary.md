# Repair Summary

## 当前状态

- repair_loop_status: blocked
- open issues: 3
- blocker: 2
- warning: 1
- info: 0

## 问题统计

- issue_count: 3
- open_issue_count: 3
- blocker_count: 2
- warning_count: 1
- info_count: 0

## 本轮修复单元

### repair-unit-001
- target: projects/demo-smoke-v1/workspace/business_blueprint.md
- goal: 修复 business_blueprint.md 中的 trace_missing 问题
- mode: patch_current_artifact
- issue_ids: BIZ-F84378DC, BIZ-7C3F1976

### repair-unit-002
- target: projects/demo-smoke-v1/workspace/experience_blueprint.md
- goal: 修复 experience_blueprint.md 中的 structure_missing 问题
- mode: patch_current_artifact
- issue_ids: EXP-5788A4A6

## 推荐重跑

```bash
python -m packages gate-business demo-smoke-v1
python -m packages gate-experience demo-smoke-v1
python -m packages validate demo-smoke-v1
python -m packages coverage demo-smoke-v1
```

## 未关闭问题

- BIZ-F84378DC | blocker | business | trace_missing | sources=validate | business 阶段发现 trace_missing 问题：final validate：business_blueprint.md 的判断追踪映射仍不足，不能视为稳定 business review
- EXP-5788A4A6 | blocker | experience | structure_missing | sources=experience_gate, validate | experience_blueprint.md 缺少必需章节：## 体验目标与任务边界, ## 体验推导依据, ## 信息架构总览, ## 任务流蓝图
- BIZ-7C3F1976 | warning | business | trace_missing | sources=business_gate, validate | business 阶段发现 trace_missing 问题：business_blueprint.md 判断追踪映射未真正追到 J-xx / POS-xx

## 已接受 warning

- none

## 已延期问题

- none
