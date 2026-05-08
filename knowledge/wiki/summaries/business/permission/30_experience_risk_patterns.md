# 30_experience_risk_patterns

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-30_EXPERIENCE_RISK_PATTERNS
- page_type: summary
- source_path: knowledge/raw/business/permission/30_experience_risk_patterns.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-08
- updated_at: 2026-05-08
- source_refs: [knowledge/raw/business/permission/30_experience_risk_patterns.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

定义权限域体验设计中 6 条通用转译原则（UX-TR）和 8 个高频风险模式（RISK-001 到 RISK-008），每个风险模式包含触发条件、用户伤害和必须暴露的业务字段，用于在体验蓝图中提前识别和规避权限认知风险。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 评估权限相关页面的体验风险时，需要对照已知风险模式检查是否有遗漏
- 设计权限页面的可解释性、可验证性时需要参照 UX-TR 原则
- 需要判断某个交互模式是否会触发入口选择困难、来源不透明、覆盖规则违背直觉等问题
- 需要确认页面是否暴露了风险模式要求的必填业务字段（如 entry_strategy、source_enum、conflict_reason_code 等）

## 3. 覆盖内容

本 raw 覆盖：

- 6 条 UX-TR 原则：可解释性优先、优先级外显、概念不增殖、结果可验证、查询闭环、安全第一
- 8 个风险模式：入口选择困难、权限来源不透明、覆盖规则导致结果违背直觉、范围类型与条件组心智不一致、跨模块散落导致查询分裂、治理模式引入流程不确定性、批量操作安全风险、协作权限形成第三套认知模型
- 每个风险模式包含：触发条件、用户伤害、必须暴露的业务字段

不涉及：

- 具体的交互设计方案、视觉表达方式、页面布局

## 4. 可直接使用的稳定结论

- 6 条 UX-TR 是权限体验设计的底线原则：必须回答"为什么有/没有、来自哪里、谁改的、何时生效"；存在覆盖规则时必须声明最终判定链路；新增权限概念默认高风险
- RISK-004（范围类型与条件组心智不一致）是高危风险：用户误以为平台自动按并集放大，实际组内交集可能导致结果窄于预期
- RISK-006（治理模式引入流程不确定性）：下钻排查困难在于用户不知道何时生效、谁卡住、能不能改，必须暴露 state_model 和 actor_responsibility
- 每个风险模式都对应一组必须暴露的业务字段，体验蓝图应从对应 raw 文件中获取这些字段的准确定义

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

> summary_path: knowledge/wiki/summaries/business/permission/30_experience_risk_patterns.md
