# 筛选区规则

## 1. 规则标识

- `Rule ID`：`LAYOUT.FILTER_BAR`
- 适用范围：页面主筛选区、列表页顶部筛选区、查询表单条

## 2. 触发条件

- 当前区域承担“筛选结果集”的职责
- 区域内存在查询条件与查询动作
- 区域位于表格、卡片列表、数据结果区之前

## 3. 结构关系

必须：

- 筛选区只承载查询条件、查询动作、重置动作、展开收起动作。
- 同一字段项必须保持 `label + control` 两段语义关系。
- 动作组必须与字段区同属一个筛选区，不得插入任一字段项内部。
- 动作组顺序必须为：`重置 -> 查询 -> 展开/收起`。
- 展开 / 收起必须只依赖一个真实状态源。
- 高级筛选字段与默认筛选字段可以分区，但仍属于同一个筛选区字段系统，不得拆成不同职责模块。

## 4. 禁止事项

- 禁止把批量操作、表格行操作、结果统计主体放入筛选区。
- 禁止拆分同一字段项内的 `label` 与 `control`。
- 禁止让两个不同 toggle 分别维护同一高级筛选区域的展开状态。
- 禁止把筛选区写成表格工具栏、批量操作栏或结果摘要栏。
- 禁止在规则层重写真实 class 名和完整 HTML 实现。

## 5. 条件分支

- 若字段数量较少，则可以不使用展开区。
- 若字段数量较多，则允许将一部分字段放入展开区。
- 若高级字段数量很少，则可以默认展开，并省略展开控件。
- 若当前区域本质不是结果筛选，而是普通表单、搜索框组或工具栏，则不套用本规则。

## 6. Reference Binding

- Primary Reference：`references/blocks/filter-bar.html`
- Required Boundaries：
  - `rules/asset-boundaries/reference-rewrite-boundaries.md`
  - `rules/asset-boundaries/component-baselines.md`

## 7. Runtime Contract

若存在展开 / 收起能力，必须使用：

- `data-collapse-root`
- `data-collapse-toggle`
- panel `id`
- `aria-expanded`

不得新增 runtime 之外的 JS。

## 8. Checklist Binding

- `checklists/modules/filter-bar.md`

## 9. 失败回退

- 无法判定是否属于筛选区时，不套用本规则。
- 无法确认是否需要展开区时，默认全部展开。
- 参考资产与真实需求冲突时，优先保留本规则中的职责边界，并对资产做最小改动。
