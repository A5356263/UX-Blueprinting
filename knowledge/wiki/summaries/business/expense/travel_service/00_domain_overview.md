# 00_domain_overview

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-EXPENSE-TRAVEL_SERVICE-00_DOMAIN_OVERVIEW
- page_type: summary
- source_path: knowledge/raw/business/expense/travel_service/00_domain_overview.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-08
- updated_at: 2026-05-08
- source_refs: [knowledge/raw/business/expense/travel_service/00_domain_overview.md]
- related_summaries:
  - knowledge/wiki/summaries/business/expense/travel_service/10_travel_service.md
  - knowledge/wiki/summaries/business/expense/travel_service/README.md
  - knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/00_domain_overview.md
  - knowledge/wiki/summaries/business/app_management/00_domain_overview.md
  - knowledge/wiki/summaries/business/approval_management/00_domain_overview.md

## 1. 知识定位

定义差旅服务子域的职责范围和核心能力：回答「差旅服务提供哪些能力、支持什么流程、对接哪些平台」这一判断问题。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要判断某项能力是否属于差旅服务子域时
- 需要了解差旅服务的核心能力全景（费用管控、多平台对接、外币报销、自动报销、多次出差合并）时
- 需要了解差旅服务对接的商旅平台（携程、同程、美团等）时
- 需要确认差旅服务的采集缺口时

## 3. 覆盖内容

本 raw 覆盖：

- 差旅服务五大核心能力：费用管控（差标政策+预算方案+超标预警）、多平台对接（携程/同程/E餐通/美团）、外币报销（Visa/Master商务卡）、自动报销（出差结束自动创建报销单+智能填充+自动计算补贴）、多次出差合并报销
- 对公月结模式

不涉及：

- 差旅服务各功能的详细配置和操作流程（需查 10_travel_service 和原始产品介绍）

## 4. 可直接使用的稳定结论

- 差旅服务实现「出差申请-差旅行程预定-报销支付」全流程线上管理，所有费用对公月结
- 对接携程商旅、同程商旅、E餐通、美团商企通等主流消费平台，覆盖机票、酒店、火车、用车、用餐
- 支持外币报销，提供 Visa/Master 商务卡，支持自动汇率或公司制定汇率
- 出差结束后系统自动创建报销申请单，智能填充内容并自动计算补贴
- 多次出差可合并为一个报销单，发票行程一一对应，补助按多次行程自动计算

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

- knowledge/wiki/summaries/business/expense/travel_service/10_travel_service.md
- knowledge/wiki/summaries/business/expense/travel_service/README.md
- knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/00_domain_overview.md
- knowledge/wiki/summaries/business/app_management/00_domain_overview.md
- knowledge/wiki/summaries/business/approval_management/00_domain_overview.md

> summary_path: knowledge/wiki/summaries/business/expense/travel_service/00_domain_overview.md
