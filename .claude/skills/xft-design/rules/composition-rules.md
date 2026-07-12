# 组合规则

## FilterBar 与 ActionBar

- 默认分成两个相邻区域
- 当筛选字段很少且操作极少时，可合并进同一个 `Panel`
- 即使合并，筛选职责与操作职责仍需保持分区

## PageHeader

- 仅承载顶层语义
- 若动作只影响主数据区，不上移到 Header

## DataTable

- 优先与 `ActionBar` 成组
- 若存在筛选区，通常位于 `FilterBar` 与 `ActionBar` 之后

## DetailSection

- 同一对象的信息可以拆 section
- 不把无关说明和批量操作混进 detail 主线

## Panel 使用

- 需要视觉边界时使用 `Panel`
- 纯布局分组优先用 flex / gap，不额外套第二层重 Surface
