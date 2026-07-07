# Ant 组件本地资料

本目录用于存放从 Ant Design 提炼后的本地静态参考资料。

## 用途

- 组件结构参考
- 尺寸与间距参考
- 状态层级参考
- HTML 原型可直接仿写的代码级参考
- 作为区域生成时应继承的控件实现基线

## 不用于

- 直接作为 React 运行时代码
- 直接照搬 props 表
- 整仓库原样堆放
- 作为“匹配到就直接套用”的模板命中系统

## 文件组织

每个组件目录下包含：

- `summary.md` — 组件定位、尺寸档位、间距、字号字重、状态、适用场景等 10 个固定字段
- `component.html` — 基础形态 / 尺寸档位 / 状态 / 高频变体四个 section，CSS 优先引用 token
- `images/` — 可选截图目录

## 基线原则

这些组件资料不只是“看看怎么写”，而是：

- 生成区域块时应优先继承的实现常量来源
- button / input / select / tabs / modal 等控件的稳定底座

允许 AI 改：

- 文案
- 字段数量
- 组合方式

不允许 AI 自由漂移：

- 默认尺寸档位
- 基础状态样式
- placeholder / focus / disabled 等实现
- runtime 契约接法

## 当前覆盖

| 批次 | 组件 | 状态 |
|------|------|------|
| 第一批 | button, modal, form, pagination, table | 已创建 / 已检查 |
| 第二批 | input, select, datepicker, tabs, drawer, tag | 已创建 / 已检查 |
