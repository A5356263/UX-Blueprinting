# 10_approval_management

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-APPROVAL_MANAGEMENT-10_APPROVAL_MANAGEMENT
- page_type: summary
- source_path: knowledge/raw/business/approval_management/10_approval_management.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-05
- updated_at: 2026-05-05
- source_refs: [knowledge/raw/business/approval_management/10_approval_management.md]
- related_summaries:
  - knowledge/wiki/summaries/business/approval_management/00_domain_overview.md
  - knowledge/wiki/summaries/business/approval_management/README.md
  - knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/10_enablement_paths.md
  - knowledge/wiki/summaries/business/app_management/10_application_management.md
  - knowledge/wiki/summaries/business/collaboration/collaboration_tools/10_collaboration_tools.md

## 1. 知识定位

描述OA审批的完整能力体系，包括表单管理、审批流程、自动化任务、审批操作和智能分析，回答「OA审批提供哪些能力、如何配置和使用审批流程」这一判断问题。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要了解OA审批的整体能力范围和产品定位时
- 需要了解表单管理（预置模板/自定义表单/自定义控件/打印模板）时
- 涉及审批流程配置（分支条件/并行分支/动态流程/子流程）时
- 需要了解审批操作（批量审批/委托审批/流程转派/流程交接/超时处理）时
- 涉及自动化任务和数据联动时
- 需要了解智能分析的统计维度时
- 需要理解系统审批（如权限变更）与审批管理的关系时

## 3. 覆盖内容

本 raw 覆盖：

- 产品定位：综合性在线审批平台，联动考勤、报销、人员异动、定薪调、离职交接、耗材领用等业务版块
- 表单管理：预置模板（用车申请/开票申请等）、自定义表单（拖拽设计+组件关联）、自定义控件、自定义打印模板
- 审批流程：按岗位/职级/角色指定审批流、分支条件与并行分支、动态流程（运行时决策）、子流程（嵌套审批）、审批人可修改限定内容
- 自动化任务：表单数据与业务数据联动、审批后自动发起下一流程、审批结束自动更新花名册
- 审批操作：批量审批（需管理员开启）、委托审批（需单独授权）、流程转派（离职/无法处理场景）、流程交接（审批人变更）、超时处理（超时提醒+智能审批）
- 多渠道提醒：PC端+移动端，待办通知+短信通知，短信频率可限
- 智能分析：审批明细统计（通过率/完成率/耗时/趋势）、超时明细统计（节点完成率/平均耗时/超时率）
- 入口：PC端工作台-最近待办/OA审批-审批中心；移动端掌上薪福通APP
- 与系统治理：审批管理可承接系统类审批（如权限变更审批），需配置流程后形成「申请->审批->生效」闭环

不涉及：

- 完整表单组件类型清单
- 分支条件的完整条件类型枚举
- 自动化任务可联动的全部业务数据范围

## 4. 可直接使用的稳定结论

- OA审批联动多个业务版块：考勤、报销、人员异动、定薪调、离职交接、耗材领用等
- 表单支持拖拽自定义设计，组件间可配置关联关系
- 审批流程支持分支条件、并行分支、动态流程和子流程四种高级模式
- 委托审批需单独授权功能权限，管理员可代理所有审批人设置委托
- 批量审批需管理员开启，范围可选全部人员或部分员工
- 审批后自动更新花名册
- 系统类审批（如权限变更）需在审批管理配置流程才能形成闭环

## 5. 必须回查 raw 的情况

以下情况不能只读 summary：

- 需要完整规则细节或精确条款时
- 需要正式证据或原文引用时
- 需要页面或流程的完整描述时
- 涉及 [GAP] / [CONFLICT] / [QUESTION] 标记项时
- summary 无法覆盖当前判断点或信息量不足时

## 6. 缺口 / 冲突 / 不确定项

- [GAP] 完整表单组件类型清单未展开
- [GAP] 分支条件支持的完整条件类型枚举未给出
- [GAP] 自动化任务可联动的全部业务数据范围未完整列出
- [GAP] 自定义控件的完整数据源协议和接口规范未采集
- [GAP] 32条FAQ的完整正文未逐条入库

## 7. 邻近阅读

弱指向 3-5 个相关 summary。

- knowledge/wiki/summaries/business/approval_management/00_domain_overview.md
- knowledge/wiki/summaries/business/approval_management/README.md
- knowledge/wiki/summaries/business/account_and_enterprise_lifecycle/10_enablement_paths.md
- knowledge/wiki/summaries/business/app_management/10_application_management.md
- knowledge/wiki/summaries/business/collaboration/collaboration_tools/10_collaboration_tools.md

> summary_path: knowledge/wiki/summaries/business/approval_management/10_approval_management.md
