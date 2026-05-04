# 24_governance_state_model

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-24_GOVERNANCE_STATE_MODEL
- page_type: summary
- source_path: knowledge/raw/business/permission/24_governance_state_model.md
- source_group: business
- status: active
- confidence: medium
- updated_at: 2026-05-04
- source_refs: [knowledge/raw/business/permission/24_governance_state_model.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

本文件围绕「1) 治理触发点」组织内容，具体知识定位待从 raw 中进一步确认。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 涉及治理模式、审批链路或审计追溯

## 3. 覆盖内容

本 raw 覆盖：

- 规则：1) 治理触发点
- 状态：2) state_model
- 章节：3) actor_responsibility, 4) 补充约束

不涉及：

- 本 raw 未显式覆盖的内容需回查其他相关 raw 或补充来源

## 4. 可直接使用的稳定结论

- 双管理员模式：变更需双方审批后生效
- 关闭双管理员模式：同样需要另一位管理员审批通过后方可关闭
- 权限变更审批模式：进入“发起 -> 审批 -> 生效”链路，但仍依赖审批管理侧完成流程设计、发布与授权配置
- 子管理员范围隔离：只能修改管辖范围内对象
- 成员停用、删除、离职：触发既有管理权限的自动回收或关闭
- `draft`：发起人可编辑

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
