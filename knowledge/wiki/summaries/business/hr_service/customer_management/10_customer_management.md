# 10_customer_management

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-HR_SERVICE-CUSTOMER_MANAGEMENT-10_CUSTOMER_MANAGEMENT
- page_type: summary
- source_path: knowledge/raw/business/hr_service/customer_management/10_customer_management.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-08
- updated_at: 2026-05-08
- source_refs: [knowledge/raw/business/hr_service/customer_management/10_customer_management.md]
- related_summaries:
  - knowledge/wiki/summaries/business/hr_service/customer_management/00_domain_overview.md
  - knowledge/wiki/summaries/business/hr_service/customer_management/README.md
  - knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/10_enablement_paths.md
  - knowledge/wiki/summaries/business/app_management/10_application_management.md
  - knowledge/wiki/summaries/business/approval_management/10_approval_management.md

## 1. 知识定位

描述客户管理模块的9大功能能力，回答「客户管理能做什么、业务流程是什么、有哪些关键规则」等判断问题。

## 2. 任务触发线索

涉及客户档案/合同/项目/用工/账单模板/账单管理/垫款管理的具体操作规则和前置条件时读取。

## 3. 覆盖内容

- 基本设置（字段配置/编码规则/权限/审批）、客户档案（有效/归档/删除/批量导入导出）、合同管理、项目管理、用工管理、账单模板（来源/字段/导出样式）、客户账单（生成/审批/推送账款/开票/回款）、垫款管理（OA审批流驱动）

## 4. 可直接使用的稳定结论

- 删除客户需无合同+无结算+无在职人员；归档需无执行中合同+无在职人员
- 差额纳税的差额部分不得开具增值税专用发票
- 审批完成的账单修改后不支持二次发起审批
- 锁定账单不会被批量删除
- 联动账款时回款/开票状态自动回写

## 6. 缺口/冲突/不确定项
- [GAP] 与账款管理的具体接口和数据流未展开
- [GAP] 导出样式配置的完整功能未采集

## 7. 邻近阅读
- knowledge/wiki/summaries/business/hr_service/customer_management/00_domain_overview.md
> summary_path: knowledge/wiki/summaries/business/hr_service/customer_management/10_customer_management.md

## 5. 必须回查 raw 的情况

以下情况不能只读 summary：

- 需要完整规则细节或精确条款时
- 需要正式证据或原文引用时
- 需要页面或流程的完整描述时
- 涉及 [GAP] / [CONFLICT] / [QUESTION] 标记项时
- summary 无法覆盖当前判断点或信息量不足时

## 6. 缺口 / 冲突 / 不确定项

- [GAP] 与账款管理版块的具体接口和数据流未在帮助文档中展开
- [GAP] 导出样式配置的完整功能说明未采集

## 7. 邻近阅读

弱指向 3-5 个相关 summary。

- knowledge/wiki/summaries/business/hr_service/customer_management/00_domain_overview.md
- knowledge/wiki/summaries/business/hr_service/customer_management/README.md
- knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/10_enablement_paths.md
- knowledge/wiki/summaries/business/app_management/10_application_management.md
- knowledge/wiki/summaries/business/approval_management/10_approval_management.md

> summary_path: knowledge/wiki/summaries/business/hr_service/customer_management/10_customer_management.md
