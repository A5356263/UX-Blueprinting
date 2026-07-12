# Reference Notes

`references/` 不再保留多层参考目录，只保留这一份压缩说明。

## 1. 用途

这里只回答三类辅助问题：

- React 高概率页面模式有哪些
- 旧 HTML 到新 React 资产的迁移关系是什么
- 历史 HTML 资产现在被挪到了哪里

## 2. React 高概率模式

- 列表管理页：`AdminSideShell -> PageHeader -> FilterBar -> ActionBar -> Panel + DataTable`
- 详情阅读页：`PageHeader -> SummaryStrip/Panel -> DetailSection`
- 框架层优先稳定，业务差异主要发生在 composition 级别，而不是 shell 级别

## 3. 迁移判断

- 旧 `shells/*.html` -> `react-system/shells/*`
- 旧 `blocks/*.html` -> `react-system/compositions/*`
- 旧 `components-ant/*.html` -> `react-system/primitives/*` 或 `vendor/ant6-subset/adapters/*`
- 旧运行时 `data-*` 机制不再作为正式主状态层

## 4. 历史资产位置

旧 HTML 历史资产已移出 skill，归档到：

`docs/archive/xft-design/legacy-html/`

正式主链不得回退依赖这些文件。
