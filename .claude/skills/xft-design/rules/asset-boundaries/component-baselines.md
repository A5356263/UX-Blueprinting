# 控件实现基线

## 目标

定义哪些内容属于稳定的控件实现基线，必须直接继承，不应在区域生成时被 AI 自由重写。

本文件解决的问题不是“页面该有哪些模块”，而是：

- 按钮默认尺寸为什么不能漂移
- 输入框 placeholder 为什么不能每次变色
- 展开收起为什么必须按 runtime 契约接入

## 基本原则

页面生成时，内容分为两类：

### 1. 需求变量

这些内容允许 AI 根据需求和规则推理：

- 页面是否整页生成还是局部生成
- 页面包含哪些区域
- 每个区域包含多少字段、模块、动作
- 字段名称、按钮文案、说明文案
- 哪些字段进入基础区，哪些进入高级区
- 区域之间的组合顺序

### 2. 实现常量

这些内容不应每次重新推理，而应继承稳定基线：

- button 的默认尺寸档位
- input / select / datepicker 的高度、padding、placeholder、状态样式
- modal / drawer / tabs 等组件的基础结构和状态行为
- `data-collapse-*`、`data-overlay-*`、`data-tab-*` 等 runtime 契约接法
- token 使用边界

## 基线来源

控件实现基线来自：

- `references/components/ant/*/summary.md`
- `references/components/ant/*/component.html`
- `runtime/basic-interactions.js`
- `design-systems/`

其中：

- `summary.md` 用于快速判定尺寸档位、间距、状态层级
- `component.html` 用于继承真实 HTML / CSS 写法
- `runtime/` 用于继承真实交互契约
- `design-systems/` 用于继承 token 与视觉边界

## 区域生成规则

区域块生成时，遵循以下顺序：

1. 先根据 `rules/` 判断区域职责和结构边界
2. 再从稳定资产块中选取最接近的区域底座
3. 区域内部涉及的控件，继承对应的控件实现基线
4. AI 只改需求变量，不自由重写实现常量

## 允许改写

- 字段数量
- 字段名称
- 模块组合
- 局部区块顺序
- 是否展示高级区
- 与当前需求直接相关的结构裁剪

## 不允许自由改写

- button 默认档位与基础状态
- input / select 的默认尺寸、padding、placeholder 样式
- focus / hover / disabled / error 等状态实现
- runtime 交互契约接法
- token 命名与使用边界

## 区域块与控件基线的关系

`references/blocks/` 的长期定位是：

> AI 允许拿来组合和改写的稳定区域资产块。

但区域块内部的控件实现，必须继续继承控件基线。

也就是说：

- 区域块可改
- 控件基线不可漂

## 失败信号

若生成结果出现以下情况，优先判断为“未继承控件基线”，而不是优先补提示词：

- placeholder 颜色不对
- 默认按钮尺寸漂移
- 输入框高度漂移
- 交互按钮存在但 runtime 不生效
- hover / focus / disabled 状态缺失

## 使用结论

后续生成时应遵循：

- 真正需要 AI 推理的是需求变量
- 真正需要系统定死的是实现常量

不要让 AI 每次重新发明按钮、输入框和交互接法。
