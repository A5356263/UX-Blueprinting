# 页面承载语义专题

- page_id: PG-TOPIC-0002
- page_type: topic
- canonical_name: 页面承载语义专题
- aliases: [页面承载语义图谱]
- status: stable
- confidence: medium
- source_refs: [SRC-BIZ-0010, SRC-BIZ-0012, SRC-BIZ-0020]
- related_pages:
  - knowledge/wiki/topics/permission-domain-index.md
  - knowledge/wiki/topics/configuration-and-explanation-chains.md
  - knowledge/wiki/relations/query-page-vs-configuration-page-boundary.md
- created_at: 2026-04-05
- updated_at: 2026-04-09

## 0. 文件定位

- 页面类型：Topic Page
- 专题名称：页面承载语义专题
- 适用范围：权限域中页面为什么存在、各页面承担什么业务语义、为什么采用 Page / Drawer / Modal
- 不处理内容：视觉样式、组件设计、开发实现方案

## 1. 结论

- 页面承载语义是权限域从“业务规则”落到“体验蓝图”的关键中间层
- 当前权限域已经形成了相对稳定的页面分工：
  - Page：承担工作台、总览、治理与大信息量配置
  - Drawer：承担从主上下文展开的连续配置步骤
  - Modal：承担就地解释、确认或单对象补充配置
- 若没有页面承载语义层，体验蓝图容易把查询页写成配置页，或把治理模式写成普通开关

## 2. 适用范围与边界

- 覆盖问题：
  - 页面目标与职责
  - 上下游跳转
  - 为什么适合用某种承载类型
- 不覆盖问题：
  - 不输出视觉稿
  - 不输出组件规格
  - 不直接替代业务规则合同
- 相关主题：
  - 查询与配置边界
  - 权限域配置链路
  - 治理模式体系

## 3. 主体内容

### 3.1 专题目标

- 把权限域页面从“名称列表”转化为“可被体验蓝图消费的承载语义”
- 帮助后续任务快速判断：
  - 该去哪个页面
  - 页面为什么这样承载
  - 页面不该承担什么职责

### 3.2 结构分解

<!-- AUTO-SYNC:BEGIN block_id=structure_breakdown source=knowledge/raw/business/permission/15_page_carrier_semantics.md mode=replace_block -->
### 托管同步结果

- 来源真源：`knowledge/raw/business/permission/15_page_carrier_semantics.md`
- 同步页面数：16

#### 页面分组清单

- 全局治理相关页面：双管理员模式配置页、子管理员列表页、子管理配置页、权限变更审批模式配置页、权限管理模式
- 协作可见性相关页面：成员协作权限
- 应用级入口治理相关页面：应用管理、应用设置页
- 查询排障相关页面：按用户查询结果、权限查询
- 用户直授相关页面：功能授权、数据授权、权限详情、用户授权
- 角色授权相关页面：授权规则、角色管理
<!-- AUTO-SYNC:END block_id=structure_breakdown -->

### 3.3 关键结论

- `Page` 适合高信息量工作台与系统级治理
- `Drawer` 适合从既有上下文中展开的连续授权步骤
- `Modal` 适合单对象、短链路、只读解释或集中确认
- 页面名相近时，必须靠“页面目标 + 必须解释点 + 承载判断”来防止职责混淆

### 3.4 适用与非适用场景

- 适用：
  - 做体验蓝图
  - 做页面职责梳理
  - 做路由和承载边界判定
- 非适用：
  - 直接产出视觉稿
  - 直接产出开发方案
  - 替代页面事实来源

## 4. 关键关系

- 关联实体：
  - `knowledge/wiki/entities/permission-detail-view.md`
- 关联概念：
  - `knowledge/wiki/concepts/governance-mode-system.md`
  - `knowledge/wiki/concepts/single-app-admin.md`
- 关联关系页：
  - `knowledge/wiki/relations/query-page-vs-configuration-page-boundary.md`

## 5. 证据与来源

<!-- AUTO-SYNC:BEGIN block_id=evidence_sources source=knowledge/raw/business/permission/15_page_carrier_semantics.md mode=merge_unique_list -->
- `knowledge/raw/business/permission/15_page_carrier_semantics.md`
- `knowledge/raw/business/permission/31_experience_translation_requirements.md`
- `knowledge/raw/business/permission/13_route_map.md`
<!-- AUTO-SYNC:END block_id=evidence_sources -->

## 6. 关联页面

- `knowledge/wiki/topics/permission-domain-index.md`
- `knowledge/wiki/topics/configuration-and-explanation-chains.md`

## 7. 缺口与冲突

<!-- AUTO-SYNC:BEGIN block_id=coverage_and_gaps source=knowledge/raw/business/permission/15_page_carrier_semantics.md mode=replace_block -->
### 托管同步缺口

- [GAP] 数据授权页的页面事实材料尚未补充
- [GAP] 权限查询中的按角色查、按权限查、按功能点查的现状承载尚未核实
- [GAP] 部分治理弹窗和配置页的下游跳转未在现有页面事实中给出
- [GAP] 权限明细视图的独立页面语义尚未在现有材料中展开
<!-- AUTO-SYNC:END block_id=coverage_and_gaps -->
- [CONFLICT] 暂未发现直接冲突

## 8. 变更记录

- 日期：2026-04-05
- 变更：新增首版专题页
- 原因：把权限域页面清单升级为可被体验蓝图消费的页面承载语义专题
