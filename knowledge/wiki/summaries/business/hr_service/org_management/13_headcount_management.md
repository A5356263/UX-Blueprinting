# 13_headcount_management

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-HR_SERVICE-ORG_MANAGEMENT-13_HEADCOUNT_MANAGEMENT
- page_type: summary
- source_path: knowledge/raw/business/hr_service/org_management/13_headcount_management.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-07
- updated_at: 2026-05-07
- source_refs: [knowledge/raw/business/hr_service/org_management/13_headcount_management.md]
- related_summaries:
  - knowledge/wiki/summaries/business/hr_service/org_management/00_domain_overview.md
  - knowledge/wiki/summaries/business/hr_service/org_management/14_position_and_rank_management.md
  - knowledge/wiki/summaries/business/hr_service/org_management/README.md
  - knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/13_super_administrator_change.md
  - knowledge/wiki/summaries/business/member/13_external_personnel.md

## 1. 知识定位

描述编制管理的完整机制，包括编制维度、强弱控制、占用规则和编制计划设置，回答「如何通过编制管控企业人员数量」这一判断问题。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要了解编制管理的开通条件和流程时
- 需要判断"组织维度"和"组织+岗位维度"的区别和选择时
- 涉及编制强弱控制的校验行为时
- 需要了解编制占用规则（兼任/待入职/待离职是否占编）时
- 涉及编制计划创建和编制数量设置时

## 3. 覆盖内容

本 raw 覆盖：

- 开通条件：需申请开通，已实名认证企业经后台审核
- 两种编制维度：组织维度、组织+岗位维度（从后者切换为前者时岗位编制信息清空）
- 强弱控制：弱控制仅提示可继续，强控制限制人员进入，支持按细分校验点配置
- 编制占用规则：占编公式固定，兼任/录用审批中/待入职/待离职是否占编可配置
- 编制计划设置流程：创建计划→设控制节点→编辑编制数→编辑岗位编制数
- 控制节点：默认叶子节点控制层层累加，支持中间层级作为控制节点（部门+岗位维度不支持）
- 岗位编制约束：部门下岗位编制总数 ≤ 部门直属编制数
- 编制变更审批通过OA审批或编制管理页面发起，变更记录可查

不涉及：

- 编制计划周期的完整枚举
- 审批流程的具体节点细节

## 4. 可直接使用的稳定结论

- 编制管理需申请开通，经后台审核
- 编制维度有两种：组织、组织+岗位，从后者切换为前者时岗位编制信息清空
- 弱控制=超编提示，强控制=超编限制进入
- 兼任是否占编可配置
- 岗位编制总数应 ≤ 部门直属编制数
- 编制变更需通过OA审批流程

## 5. 必须回查 raw 的情况

以下情况不能只读 summary：

- 需要完整规则细节或精确条款时
- 需要正式证据或原文引用时
- 需要页面或流程的完整描述时
- 涉及 [GAP] / [CONFLICT] / [QUESTION] 标记项时
- summary 无法覆盖当前判断点或信息量不足时

## 6. 缺口 / 冲突 / 不确定项

- [GAP] 编制管理的具体审批流程节点细节未在帮助文档中展开
- [GAP] 编制计划周期类型（年度/季度）的完整枚举未给出

## 7. 邻近阅读

弱指向 3-5 个相关 summary。

- knowledge/wiki/summaries/business/hr_service/org_management/00_domain_overview.md
- knowledge/wiki/summaries/business/hr_service/org_management/14_position_and_rank_management.md
- knowledge/wiki/summaries/business/hr_service/org_management/README.md
- knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/13_super_administrator_change.md
- knowledge/wiki/summaries/business/member/13_external_personnel.md

> summary_path: knowledge/wiki/summaries/business/hr_service/org_management/13_headcount_management.md
