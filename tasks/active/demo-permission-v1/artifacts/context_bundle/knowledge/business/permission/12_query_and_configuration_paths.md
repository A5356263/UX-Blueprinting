# 12_query_and_configuration_paths

> 权限域必须同时说明查询语义与配置路径；即使现状承载分散，也要明确应输出的路径能力。

## 查询路径

### 1. People Query
- 语义：某人有什么权限、来源是什么、数据范围是什么、为何不可用
- 现状承载：用户授权、个人权限详情聚合入口
- 蓝图最低输出字段：
  - `effective_permissions[]`
  - `source_enum[]`
  - `final_effective_rule`
  - `conflict_reason_code`

### 2. Resource Query
- 语义：某功能、菜单、操作点由哪些人或哪些角色拥有
- 现状痛点：查询困难、入口分散
- 蓝图最低输出字段：
  - `resource_id`
  - `action`
  - `holders.users[]`
  - `holders.roles[]`
  - `why_effective` 或 `gaps`

### 3. Change Query / Audit
- 语义：谁在何时对谁做了什么变更、是否审批、何时生效
- 蓝图最低输出字段：
  - `audit_requirement`
  - `state_model`
  - `actor_responsibility`

### 4. feasible_level
- `feasible`：现状已有明确承载
- `partial`：部分可查，但解释、来源或审计存在缺口
- `unavailable`：现状无承载，必须显式输出风险与依赖建议

## 配置路径

### 功能权限配置
- 按末级菜单或操作点产生授权
- 可通过按人或按角色入口承载

### 数据权限配置
- 以前置功能权限为条件
- 取值为：全部 / 部分 / 无
- 部分权限通过条件组与多维度交集表达
- 可存在独立入口，也可存在从功能权限联动进入的入口
