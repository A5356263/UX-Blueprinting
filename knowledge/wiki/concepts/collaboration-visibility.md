# 协作可见性

- page_id: PG-CONCEPT-0002
- page_type: concept
- canonical_name: 协作可见性
- aliases: [成员协作可见性]
- status: stable
- confidence: medium
- source_refs: [SRC-BIZ-0007, SRC-BIZ-0008, SRC-BIZ-0009, SRC-BIZ-0011, SRC-BIZ-0012, SRC-BIZ-0019, SRC-BIZ-0020]
- related_pages:
  - knowledge/wiki/concepts/application-visibility.md
  - knowledge/wiki/concepts/functional-permission.md
  - knowledge/wiki/topics/permission-domain-index.md
- created_at: 2026-04-05
- updated_at: 2026-04-09

## 0. 文件定位

- 页面类型：Concept Page
- 概念名称：协作可见性
- 适用范围：权限域中员工之间、员工与外部协作对象之间的信息互见边界
- 不处理内容：后台管理授权、功能按钮权限、应用审批流实现

## 1. 结论

- 协作可见性回答的是“成员之间能不能互相看见哪些信息”，不是“能不能操作后台功能”
- 在当前权限域中，协作可见性由 `成员协作权限` 主承载，采用“全局主规则 + 补充规则 + 适用应用挂载”的模型
- 协作可见性是权限域中的独立认知模型，必须与功能权限、数据权限分开表达
- 规则只有挂载到具体应用后，才形成实际生效面

## 2. 适用范围与边界

- 定义边界：覆盖员工/外部人员之间的可见性策略、例外规则、适用应用
- 非目标：不覆盖后台菜单操作权、不覆盖数据对象范围授权、不覆盖治理审批模式
- 常见误解：
  - 认为协作可见性就是另一种数据权限
  - 认为协作可见性会自动授予后台管理能力
  - 认为只配置主规则就足以覆盖复杂矩阵组织

## 3. 主体内容

### 3.1 概念定义

- 协作可见性是横向信息边界模型
- 它用于回答不同成员或协作对象之间的资料、联系人、组织信息是否可互见
- 在企业场景中，它主要服务组织隐私、跨区域隔离、外部协作防泄露等目标

### 3.2 判定规则

- 协作可见性主要通过 `成员协作权限` 页配置
- 其结构通常包括：
  - 主规则：定义全局基线
  - 补充规则：处理例外场景
  - 适用应用：定义在哪些业务前台真正生效
- 该模型与功能权限、数据权限并行存在，但不共享同一认知入口

### 3.3 与相近概念的区分

- 与功能权限的区分：
  - 功能权限控制系统能做什么
  - 协作可见性控制成员之间能看见什么人或信息
- 与数据权限的区分：
  - 数据权限控制业务数据对象的作用范围
  - 协作可见性控制组织协作信息的互见边界
- 与应用可见性的区分：
  - 应用可见性决定应用入口是否出现
  - 协作可见性决定进入某类应用后人与人之间的信息是否暴露

## 4. 关键关系

- 上位概念：可见性边界、组织隐私、例外规则
- 下游对象：`成员协作权限`
- 常见组合关系：
  - 协作可见性 + 适用应用挂载
  - 协作可见性 + 主规则/补充规则
  - 协作可见性 + 组织边界

## 5. 证据与来源

- `knowledge/raw/business/permission/10_capability_map.md`
- `knowledge/raw/business/permission/11_task_scenarios.md`
- `knowledge/raw/business/permission/12_query_and_configuration_paths.md`
- `knowledge/raw/business/permission/14_actor_boundary.md`
- `knowledge/raw/business/permission/15_page_carrier_semantics.md`
- `knowledge/raw/business/permission/30_experience_risk_patterns.md`
- `knowledge/raw/business/permission/31_experience_translation_requirements.md`

## 6. 关联页面

- `knowledge/wiki/concepts/application-visibility.md`
- `knowledge/wiki/concepts/functional-permission.md`
- `knowledge/wiki/topics/permission-domain-index.md`

## 7. 缺口与冲突

- [GAP] 当前仍缺少把协作可见性与“业务数据范围”做更细粒度边界对照的专门关系页
- [GAP] 外部人员协作场景的状态语义尚未单独沉淀
- [CONFLICT] 暂未发现直接冲突，但后续若把协作可见性直接并入功能/数据权限，需要重新核实当前模型边界

## 8. 变更记录

- 日期：2026-04-05
- 变更：新增首版概念页
- 原因：补齐权限域中独立的横向可见性模型
