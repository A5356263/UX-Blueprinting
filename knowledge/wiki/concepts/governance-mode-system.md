# 治理模式体系

- page_id: PG-CONCEPT-0005
- page_type: concept
- canonical_name: 治理模式体系
- aliases: [权限治理模式]
- status: stable
- confidence: medium
- source_refs: [SRC-BIZ-0007, SRC-BIZ-0008, SRC-BIZ-0009, SRC-BIZ-0010, SRC-BIZ-0012, SRC-BIZ-0017, SRC-BIZ-0018, SRC-BIZ-0021]
- related_pages:
  - knowledge/wiki/concepts/role-template-authorization.md
  - knowledge/wiki/relations/query-page-vs-configuration-page-boundary.md
  - knowledge/wiki/topics/permission-domain-index.md
- created_at: 2026-04-05
- updated_at: 2026-04-09

## 0. 文件定位

- 页面类型：Concept Page
- 概念名称：治理模式体系
- 适用范围：权限域中的子管理员模式、双管理员互审模式、权限变更审批模式及其状态影响
- 不处理内容：审批引擎内部实现、组织架构建模、具体按钮交互文案

## 1. 结论

- 治理模式体系回答的是“权限变更如何被约束、何时生效、由谁负责”，不是“权限内容本身是什么”
- 在当前权限域中，治理模式属于系统级规则，不能被写成普通局部开关
- 治理模式不会改变授予事实来源，但会改变结果何时生效、谁可以改、谁需要复核
- 当前仓库中的治理模式至少包括：子管理员范围隔离、双管理员互审、权限变更审批

## 2. 适用范围与边界

- 定义边界：覆盖系统级治理范式、状态模型、生效链路、责任边界
- 非目标：不覆盖单个菜单按钮权限定义，不覆盖应用前台入口可见性
- 常见误解：
  - 认为治理模式只是显示层的流程提示
  - 认为治理模式会替代功能权限或数据权限本身
  - 认为治理模式开启后立即等于结果生效

## 3. 主体内容

### 3.1 概念定义

- 治理模式体系是权限域中的上层约束模型
- 它用于决定：
  - 谁有资格修改
  - 修改是否需要复核或审批
  - 结果在哪个状态才真正生效
- 它是对授权动作的过程性约束，不是对授权内容的直接定义

### 3.2 判定规则

- 子管理员模式：
  - 通过范围隔离限制谁能看、谁能改、谁能授予
- 双管理员互审模式：
  - 高危变更需双方处理后才生效
- 权限变更审批模式：
  - 变更需进入审批流，状态可能经历 `draft`、`pending`、`approved`、`effective` 等阶段
- 治理模式的状态不会改写事实来源，但会修饰最终是否生效

### 3.3 与相近概念的区分

- 与功能权限的区分：
  - 功能权限管能做什么
  - 治理模式管改动怎么被约束、何时生效
- 与数据权限的区分：
  - 数据权限管作用范围
  - 治理模式管过程状态与责任边界
- 与查询页的区分：
  - 查询页可解释治理状态
  - 治理模式页负责配置治理框架

## 4. 关键关系

- 上位概念：生效状态、审计闭环、责任分层
- 下游对象：`权限管理模式`、`子管理配置页`、`双管理员模式配置页`、`权限变更审批模式配置页`
- 常见组合关系：
  - 治理模式 + `state_model`
  - 治理模式 + 审计合同
  - 治理模式 + 解释文案策略

## 5. 证据与来源

- `knowledge/raw/business/permission/10_capability_map.md`
- `knowledge/raw/business/permission/11_task_scenarios.md`
- `knowledge/raw/business/permission/12_query_and_configuration_paths.md`
- `knowledge/raw/business/permission/13_route_map.md`
- `knowledge/raw/business/permission/15_page_carrier_semantics.md`
- `knowledge/raw/business/permission/24_governance_state_model.md`
- `knowledge/raw/business/permission/25_audit_contract.md`
- `knowledge/raw/business/permission/32_copy_and_explanation_strategy.md`

## 6. 关联页面

- `knowledge/wiki/concepts/role-template-authorization.md`
- `knowledge/wiki/relations/query-page-vs-configuration-page-boundary.md`
- `knowledge/wiki/topics/permission-domain-index.md`

## 7. 缺口与冲突

- [GAP] 当前业务知识中关于“子管理员模式与双管理员模式不可同时开启”的表述，与页面语义文件中“子管理员模式和其他模式不互斥”的表述存在潜在不一致，需要后续核实
- [GAP] 治理模式与应用级单点治理之间的交叉边界尚未单独沉淀
- [CONFLICT] `24_governance_state_model.md` 与 `15_page_carrier_semantics.md` 对模式互斥关系存在潜在冲突，当前未强行裁决

## 8. 变更记录

- 日期：2026-04-05
- 变更：新增首版概念页
- 原因：补齐权限域中系统级治理约束的统一定义
