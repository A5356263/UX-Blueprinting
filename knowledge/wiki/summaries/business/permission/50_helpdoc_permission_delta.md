# 50_helpdoc_permission_delta

- page_id: PG-SUMMARY-BUSINESS-BUSINESS-PERMISSION-50_HELPDOC_PERMISSION_DELTA
- page_type: summary
- source_path: knowledge/raw/business/permission/50_helpdoc_permission_delta.md
- source_group: business
- status: active
- confidence: medium
- summary_role: ai_route_card
- semantic_status: ai_generated
- semantic_updated_at: 2026-05-07
- updated_at: 2026-05-07
- source_refs: [knowledge/raw/business/permission/50_helpdoc_permission_delta.md]
- related_summaries:
  - knowledge/wiki/summaries/business/permission/00_domain_overview.md
  - knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
  - knowledge/wiki/summaries/business/permission/02_glossary.md
  - knowledge/wiki/summaries/business/permission/03_business_objects.md
  - knowledge/wiki/summaries/business/permission/04_object_relations.md

## 1. 知识定位

提取帮助文档中与权限域相关的现有事实和表述，供与现有 permission 真源对比融合，标注了增量内容（可融入）和冲突内容（[CONFLICT] 需核对），是帮助文档知识向权限知识库迁移的桥梁文件。

## 2. 任务触发线索

当任务涉及以下问题时，应优先读取本 summary，并按需回查 raw：

- 需要了解帮助文档中已有的权限相关表述是否与 permission 真源一致
- 需要核对帮助文档中数据权限的旧口径是否与新的"范围类型+条件组"模型冲突
- 需要补充帮助文档中的非冲突增量到对应编号文件
- 需要了解超级管理员继承规则、成员离职权限回收等帮助文档有但 permission 真源未详细展开的事实

## 3. 覆盖内容

本 raw 覆盖：

- 12 个章节：管理后台权限定位（用户授权+角色管理）、授权前置顺序（3 步）、用户授权表述、角色管理表述、子管理员模式表述、双管理员互审表述、权限变更审批表述、成员离职与权限关闭表述、超级管理员职责承接表述、应用可见范围与功能权限表述、数据权限旧口径冲突标注、融合要求
- [CONFLICT]：帮助文档中数据权限旧口径（维度 Tab + 默认全部数据权限 + 多维度取交集）与现有 permission 真源的"范围类型+条件组"模型存在冲突

不涉及：

- 帮助文档的具体行文和截图

## 4. 可直接使用的稳定结论

- 帮助文档中非冲突增量可融入现有 permission 对应编号文件
- 帮助文档确认：新超级管理员自动继承全量功能权限（除代发付款）+ 表单审批管理员权限；普通成员离职后自动回收权限
- 帮助文档确认：应用可见范围与功能权限是同时生效、同时存在的关系
- [CONFLICT] 数据权限旧口径（"每个功能至少选一个维度、多维度取交集、未设置维度默认全部数据权限"）与现有真源的"范围类型+条件组"模型不一致，需核对后再决定是否覆盖

## 5. 必须回查 raw 的情况

以下情况不能只读 summary：

- 需要完整规则细节或精确条款时
- 需要正式证据或原文引用时
- 需要页面或流程的完整描述时
- 涉及 [GAP] / [CONFLICT] / [QUESTION] 标记项时
- summary 无法覆盖当前判断点或信息量不足时

## 6. 缺口 / 冲突 / 不确定项

- [CONFLICT] 当前帮助文档仍存在以下数据权限表述，是否与现有 permission 真源一致，需进一步核对：

## 7. 邻近阅读

弱指向 3-5 个相关 summary。

- knowledge/wiki/summaries/business/permission/00_domain_overview.md
- knowledge/wiki/summaries/business/permission/01_scope_and_boundary.md
- knowledge/wiki/summaries/business/permission/02_glossary.md
- knowledge/wiki/summaries/business/permission/03_business_objects.md
- knowledge/wiki/summaries/business/permission/04_object_relations.md

> summary_path: knowledge/wiki/summaries/business/permission/50_helpdoc_permission_delta.md
