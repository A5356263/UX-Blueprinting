# XFT 设计语言基线

除非任务明确符合例外条件，生成 XFT 页面时应遵循以下默认规则。设计语言基线先于内容 Pattern 判断生效；没有匹配的 Pattern，不代表页面可以忽略 XFT 的应用结构与视觉层级。

## 应用结构

默认：

- Application Frame 占满应用 viewport。
- 顶部导航、左侧导航和可选的 `workspaceTop` 不随页面内容滚动。
- workspace canvas 是页面内容的主要纵向滚动容器。
- `body` 和 document 不承担正常页面的主要滚动。
- `workspaceTop` 是通用位置，只承载确实属于整个 workspace、且必须位于滚动内容之外的轻量 chrome；没有需求时不渲染。
- 可选的 `workspaceBottomDock` 位于 canvas 下方，不随 canvas 滚动；它只提供通用位置，不绑定具体操作栏组件。

使用：

- `template.application-frame`

检查：

- 滚动 canvas 时，应用导航、`workspaceTop` 和 `workspaceBottomDock` 保持位置。
- 页面内容不会使 document 成为主要滚动容器。

## 标准工作页面

默认：

- 在 muted canvas 上使用一个主要白底 Primary Work Surface。
- Primary Work Surface 是 canvas 的直接子元素，并拥有自己的外部 inset、居中和 max-width 约束。
- 单 region 页面不在 region 外额外增加标题栏或 tabs bar。
- 主表面通常直接从内容、tabs（如有）或返回导航（如有）开始；对象名称或状态确有必要时，在主表面内部紧凑表达，不默认生成页面大标题和描述。
- 内容导航、表单、表格和普通内容区块在主表面内部组织。
- inner Tabs 和 Anchor 是可选组合方式；没有需求时不渲染，也不保留空占位。
- inner Tabs 随页面内容滚动，不使用 `workspaceTop` 的非滚动规则。
- 普通内容分组优先使用留白、对齐、标题层级和内缩 Divider，不自动生成多张同权 Card。
- 默认不使用阴影表达主表面或普通内容层级。

例外：

- 页面同时存在两列以上主要布局和多个相对独立的内容区块时，可以使用 multi-region canvas。
- multi-region 页面可以直接在 canvas 中组织多个独立区域，不强制套用 Primary Work Surface。
- 边界不清时，默认使用 Primary Work Surface。

相关物料：

- `template.primary-work-surface`

检查：

- 标准页面只有一个主要内容表面。
- multi-region 页面没有被永久白底 page wrapper 包裹。

## 内容分割线

默认：

- 普通内容 Divider 相对 owning container 的视觉边缘左右各内缩 `4px`。
- 普通 Divider 只表达同一内容责任内部的轻量分组，不建立新的 Card 或 surface。
- Divider 使用 XFT neutral border alias，不依赖阴影加强层级。

例外：

- `XftContentActionBar` 的顶部边界不是普通内容 Divider；它贯穿组件所在 container 的完整宽度。

相关物料：

- Inset Divider declaration-only Recipe：`inset-divider`（使用 literal `4px`）

## 页面级操作

默认：

- 当页面级操作需要在内容滚动期间持续可用时，在 `workspaceBottomDock` 中组合 page-private dock host 和 `XftContentActionBar`。
- Application Frame 只提供非滚动的 `workspaceBottomDock`；page-private dock host 决定宽度和水平位置；`XftContentActionBar` 不写 fixed、sticky 或 absolute 定位。
- dock 占据独立布局高度，不覆盖 canvas 内容。
- `XftContentActionBar` 与 Primary Work Surface、multi-region canvas 分开使用，不依赖某一种 surface DOM 或 CSS。
- `XftContentActionBar` 只负责 `width: 100%`、自身背景、贯穿所在 container 的顶部边界和紧凑 padding。
- 页面负责按钮对齐、顺序、强调、业务语义、handlers、loading 和 disabled 状态。
- standard work page 的 dock host 可以与 Primary Work Surface 同宽；multi-region page 的 dock host 应横向贯穿整个 muted workspace 灰底，不跟随内容 root 的 inset 或 padding 缩进。

相关物料：

- `component.content-action-bar`
- Public component：`XftContentActionBar`
- 最小输入：`children: ReactNode`、`ariaLabel: string`
- 组件输出 `role="toolbar"`，不提供 alignment、actions 数组、业务状态、`className` 或 `style`。
