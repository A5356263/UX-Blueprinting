# Stage Gate Report

## 1. 检查结果

- status: warning
- 是否阻断: 否
- has_blocker: false
- blocker_count: 0
- warning_count: 1
- info_count: 0

- project_id: sub-admin-copy
- stage: experience_lite
- next_stage: final-validate
- can_proceed: true

## 2. 问题列表

- warning: experience_blueprint.md 主流程、异常或页面设计核心区包含表格，建议优先使用节点化 Markdown 层级表达

## 3. 检查范围

- projects/sub-admin-copy/workspace/facts.md
- projects/sub-admin-copy/workspace/business_note.md
- projects/sub-admin-copy/workspace/business_blueprint_lite.md
- projects/sub-admin-copy/workspace/experience_blueprint.md
- projects/sub-admin-copy/runtime/provenance.json

## 4. 建议处理

- 当前为 warning，可复核后接受，或补强对应内容后重跑。
