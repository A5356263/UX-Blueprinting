# 资产选择规则

## 列表管理页

- shell 优先：`admin-side-shell`
- header 优先：`page-header`
- filter 区优先：`filter-bar`
- action 区优先：`action-bar`
- primary content 优先：`data-table`
- 状态字段优先：`status-tag`

## 表单页

- shell 优先：`admin-side-shell`
- header 优先：`page-header`
- 表单字段优先从 `primitive` 组合
- 最终动作落在 `footer actions`

## 详情页

- shell 优先：`admin-side-shell`
- header 优先：`page-header`
- summary / detail 区优先：`detail-section`
- 顶部摘要优先：`summary-strip`

## 弹层任务页

- 容器优先：`modal-task`
- 主体内容优先复用已存在的 composition 或 primitive

## 选择顺序

1. 优先选择 `composition`
2. `composition` 不足时再下探 `primitive`
3. 仅在两者都不足时，允许局部 JSX 补充
