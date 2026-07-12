# Component Recipes

本文件定义 React 语义组件如何消费 token。

## PageHeader

- 标题使用 `var(--text-h3)` + `var(--weight-bold)`
- 说明文字使用 `var(--text-tertiary)`
- 页面级动作位于右侧，避免与主体内容混排
- 仅当动作影响整个页面时，才放入 Header

## FilterBar

- 外层默认使用 `Panel`
- 字段间距使用 `var(--space-4)`
- Label 与控件间距使用 `var(--space-2)`
- 查询和重置动作放在同一操作组
- 不把结果统计或批量操作混入筛选区

## ActionBar

- 默认跟随主数据区
- 左侧放业务动作，右侧放辅助工具
- 同层主按钮只能有一个
- 不承载查询字段主体

## DataTable

- 作为主数据区默认载体
- 优先搭配 `ActionBar`、可选搭配 `FilterBar`
- 不在表格容器内重复堆叠大 padding

## DetailSection

- 用于单对象阅读
- 若信息较少，可合并为单区块
- 若信息较多，拆为多个 section，但保持单对象主线

## SummaryStrip

- 用于页面顶部关键摘要
- 摘要项之间使用 `gap` 组织，不重复叠加重 Surface
- 数字与状态优先使用主文字与辅助文字层级区分

## StatusTag

- 成功、警告、错误、信息使用语义色
- 中性状态使用默认背景和文字，不手写额外灰色

## ModalTask

- 外层由覆盖层容器承载
- 主体内容与底部动作明确分区
- 不把复杂长流程硬塞进单个弹层
