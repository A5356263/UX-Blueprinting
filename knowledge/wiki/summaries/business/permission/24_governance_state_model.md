# 24_governance_state_model

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-24_GOVERNANCE_STATE_MODEL
- page_type: summary
- source_path: knowledge/raw/business/permission/24_governance_state_model.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-05
- updated_at: 2026-05-05
- source_refs: [knowledge/raw/business/permission/24_governance_state_model.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

定义权限治理的 5 个触发点和统一的 6 状态生命周期模型，明确每个状态下的角色职责（who_can_view/who_can_act/what_actions_allowed/handoff_to_next_state），用于治理审批流程设计和状态追溯。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要理解权限变更在审批链路中的状态推进过程
- 设计审批流程时需要知道各状态下谁能看、谁能操作、可执行什么动作
- 需要判断某个治理模式的触发条件和互斥约束
- 需要确定成员离职/停用/删除时的权限自动回收逻辑

## 3. 覆盖内容

本 raw 覆盖：

- 5 个治理触发点：双管理员模式、关闭双管理员模式、权限变更审批模式、子管理员范围隔离、成员停用/删除/离职
- 6 个状态：draft（发起人可编辑）、pending（审批人处理）、approved（已通过但未必已生效）、rejected（被拒绝）、effective（已生效）、revoked（已撤销/已回收）
- actor_responsibility：每个状态需声明 who_can_view/who_can_act/what_actions_allowed/handoff_to_next_state
- 补充约束 3 条

不涉及：

- 审批流程的具体节点设计（由审批域负责）

## 4. 可直接使用的稳定结论

- 治理状态生命周期：draft -> pending -> approved/rejected -> effective/revoked
- 双管理员模式下，关闭双管理员本身也需要另一位管理员审批通过
- 仅开启权限变更审批模式不等于审批闭环完成，若审批中台未配置则后续权限变更可能无法闭环
- 治理状态影响结果何时生效，但不改变授予事实来源
- 子管理员模式与双管理员模式不可同时开启

## 5. 必须回查 raw 的情况

以下情况不能只读 summary：

- 需要完整规则细节或精确条款时
- 需要正式证据或原文引用时
- 需要页面或流程的完整描述时
- 涉及 [GAP] / [CONFLICT] / [QUESTION] 标记项时
- summary 无法覆盖当前判断点或信息量不足时

## 6. 缺口 / 冲突 / 不确定项

- none

## 7. 邻近阅读

弱指向 3-5 个相关 summary。

- knowledge/wiki/summaries/business/permission/00_domain_overview.md
- knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
- knowledge/wiki/summaries/business/permission/02_glossary.md
- knowledge/wiki/summaries/business/permission/03_business_objects.md
- knowledge/wiki/summaries/business/permission/04_object_relations.md

> summary_path: knowledge/wiki/summaries/business/permission/24_governance_state_model.md
