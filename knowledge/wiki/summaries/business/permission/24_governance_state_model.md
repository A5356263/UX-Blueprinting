# 24_governance_state_model

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-24_GOVERNANCE_STATE_MODEL
- page_type: summary
- source_path: knowledge/raw/business/permission/24_governance_state_model.md
- source_group: business
- status: active
- confidence: medium
- updated_at: 2026-04-24
- source_refs: [knowledge/raw/business/permission/24_governance_state_model.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 这份原始资料讲什么

本摘要对应原始资料《24_governance_state_model》，用于提供快速理解入口。

## 2. 适用范围 / 不适用范围

### 适用范围
- 适用于快速判断该原始资料是否与当前任务相关。
- 适用于构建 business 领域的背景理解与阅读入口。

### 不适用范围
- 不适用于替代原文证据、细节条款或最终业务裁决。

## 3. 关键事实

- 双管理员模式：变更需双方审批后生效
- 关闭双管理员模式：同样需要另一位管理员审批通过后方可关闭
- 权限变更审批模式：进入“发起 -> 审批 -> 生效”链路，但仍依赖审批管理侧完成流程设计、发布与授权配置
- 子管理员范围隔离：只能修改管辖范围内对象
- 成员停用、删除、离职：触发既有管理权限的自动回收或关闭
- `draft`：发起人可编辑

## 4. 关键术语 / 关键对象

- 1) 治理触发点
- 2) state_model
- 3) actor_responsibility
- 4) 补充约束

## 5. 当前缺口 / 冲突 / 问题

- none

## 6. 相关摘要 / 建议继续阅读

- knowledge/wiki/summaries/business/permission/00_domain_overview.md
- knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
- knowledge/wiki/summaries/business/permission/02_glossary.md
- knowledge/wiki/summaries/business/permission/03_business_objects.md
- knowledge/wiki/summaries/business/permission/04_object_relations.md

> summary_path: knowledge/wiki/summaries/business/permission/24_governance_state_model.md
