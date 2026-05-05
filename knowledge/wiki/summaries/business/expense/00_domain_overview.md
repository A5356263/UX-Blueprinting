# 00_domain_overview

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-EXPENSE-00_DOMAIN_OVERVIEW
- page_type: summary
- source_path: knowledge/raw/business/expense/00_domain_overview.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-05
- updated_at: 2026-05-05
- source_refs: [knowledge/raw/business/expense/00_domain_overview.md]
- related_summaries:
  - knowledge/wiki/summaries/business/expense/README.md
  - knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/00_domain_overview.md
  - knowledge/wiki/summaries/business/app_management/00_domain_overview.md
  - knowledge/wiki/summaries/business/approval_management/00_domain_overview.md
  - knowledge/wiki/summaries/business/collaboration/00_domain_overview.md

## 1. 知识定位

定义费用管理域的职责边界与覆盖范围：回答「费用管理域管什么、包含哪些子域、与哪些外部系统对接」这一判断问题。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要判断某个能力或概念是否属于费用管理域时
- 需要了解费用管理域的整体定位和四个子域的职责划分时
- 需要了解费用管理域与外部系统（OA审批、招行支付、智能记账、国税局、商旅平台）的集成关系时
- 需要区分费用管理域与其他业务域的边界时

## 3. 覆盖内容

本 raw 覆盖：

- 费用管理域的四个子域：差旅服务（出差申请-预定-报销-支付）、日常报销（提单-审批-支付-记账）、对公报账（供应商-合同-付款）、通用配置（系统配置+支付管理+会计核算）
- 五个主要外部集成方：OA审批、招商银行代发/云直联/CBS、智能记账、国税局发票验真、携程/同程/美团等商旅平台

不涉及：

- 各子域的具体能力细节和操作流程（需查对应子域 raw）

## 4. 可直接使用的稳定结论

- 费用管理域覆盖企业费用管控全流程，包含差旅服务、日常报销、对公报账、通用配置四个子域
- 报销单审批流程通过 OA 审批配置，与审批管理域紧密集成
- 支付能力依赖招商银行代发、云直联和 CBS 跨行支付
- 发票验真验重对接国税局接口
- 差旅预订对接携程、同程、美团等主流商旅平台

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

- knowledge/wiki/summaries/business/expense/README.md
- knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/00_domain_overview.md
- knowledge/wiki/summaries/business/app_management/00_domain_overview.md
- knowledge/wiki/summaries/business/approval_management/00_domain_overview.md
- knowledge/wiki/summaries/business/collaboration/00_domain_overview.md

> summary_path: knowledge/wiki/summaries/business/expense/00_domain_overview.md
