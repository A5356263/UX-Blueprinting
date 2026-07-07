# XFT 设计系统

> 分类：企业级 & 专业
> 面向企业后台业务应用的维度化 Token 命名设计系统。清晰、克制、信息密度高。

## 1. 视觉主题与氛围

企业级后台业务设计系统，适用于管理后台、工作台、表单页、数据表格等信息密集型页面。清晰优先，结构层次优先于装饰表达。

- **视觉风格：** 清晰、专业、以信息为导向
- **色彩立场：** 强调色 + 语义色（错误/警告/成功/信息）+ 中性布局色
- **设计意图：** 每个视觉决策都应服务于内容可读性和任务效率

## 2. 色彩

### Token 命名

Color token 遵循固定的维度顺序：`type-object-attribute-intention-prominence-state`。

| 维度 | 取值 |
|------|------|
| object | `layout`（页面级背景，不透明）/ `container`（卡片、面板，允许半透明） |
| attribute | `bg` / `border` / `text` / `divider` |
| intention | `accent` / `error` / `warning` / `success` / `info` / `neutral` |
| prominence | `regular` / `light` / `subtle`（语义组）— `bright` / `lightgray` / `gray` / `inverse`（中性组） |
| state | `hover` / `active` |

### Intention 与 Prominence 分组

**语义组**（intention = accent/error/warning/success/info）：
- `regular` — 强对比，主操作按钮、状态文字
- `light` — 浅色背景色、弱强调边框
- `subtle` — 大面积背景区分（仅 accent）

**中性组**（intention = neutral）：
- `bright` — 默认白色表面（不透明）
- `lightgray` — 微对比容器背景（半透明）
- `gray` — 布局/容器背景，或浅色表面上的文字（搭配数字 10-50）
- `inverse` — 深色反转区域，或深色表面上的文字（搭配数字 20-50）

### 关键色值

- 强调色 regular: `#1966ff`
- 布局页面背景: `#f3f4f6`
- 容器卡片背景: `#ffffff`
- 中性文字: `rgba(19, 34, 64, 0.95)`（gray50）递减至 `0.25`（gray10）
- 中性边框: `rgba(19, 34, 64, 0.15)`
- 中性分割线: `rgba(19, 34, 64, 0.1)`

中性背景、边框、文字色大量使用半透明叠加。这使得元素在嵌套表面中保持稳定对比度，无需为不同背景色配置多套 token。

## 3. 字体排版

**字号阶梯：** 12 / 14 / 16 / 18 / 20 / 24 / 32

**object 分类：**
- `heading` — 标题，index 1-7（1 最大）
- `body` — 正文，默认 14px
- `paragraph` — 长文阅读
- `auxiliary` — 辅助文字、标签、元数据

**字重：** 400（常规）、600（加粗）
**行高：** 1.37（紧凑）、1.6（常规）、1.75（宽松）

**字体族：** 系统原生优先 — `-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", Arial, sans-serif`。

## 4. 间距

基于 4px 栅格。Scale：0 / 4 / 8 / 12 / 16 / 20 / 24 / 32 / 40 / 48 / 64 / 80 / 160。

### Surface 与 Wrapper

容器分两类角色，不可混用：

- **Wrapper（纯布局层）** — 仅用于排列子元素，自身不拥有视觉表现。没有背景、边框、阴影，不设置 `padding`，通过 `gap` / `direction` / `align` 控制排列。
- **Surface（视觉承载层）** — 拥有可感知的表面和边界：背景色 / 边框 / 阴影，至少具备其一。拥有 `padding`。

**选用规则：**

- 布局-only 分组 → Wrapper。不添加任何视觉属性。
- 需要可见表面或结构边界的内容块 → Surface（Card、Panel）。
- 页面级结构分区（header、footer、content body） → 区域带（带背景区分的大区块）。

**判定顺序（从弱到强）：** Wrapper → Surface → 区域带。默认使用 Wrapper，只有当内容确实需要视觉区分时才升级。

**分隔手段优先级（从弱到强）：**

1. 标题 + 间距（同一 Surface 内，用 Wrapper 分组）
2. Divider 分割线（同一 Surface 内章节划分）
3. 新 Surface — 至少选用一项：对比背景色 / 边框 / 阴影

**同一视觉边界只由一层承担 padding。** 内层 Wrapper 通过 gap 控制排列，不叠加 padding。

## 5. 圆角

| Token | 值 | 用途 |
|-------|-----|------|
| `small` | 4px | 标签、小按钮、复选框 |
| `regular` | 6px | 输入框、按钮、选择器、下拉菜单 |
| `large` | 12px | 卡片、弹窗、Banner |

## 6. 阴影

两个维度：`size`（大小）× `direction`（方向）。

**Size：** `small`（toast、tooltip）→ `regular`（下拉菜单、浮层）→ `large`（弹窗、对话框）→ `special1/2/3`（特定业务语义：浮动主按钮、吸底操作区、工作台核心卡片）。

**Direction：** `top` / `right` / `bottom` / `left`。

## 7. 布局与组合

后台业务页面默认结构：

```
页面 (layout-bg-neutral-gray)
├── 主 Surface (container-bg-neutral-bright + border-neutral + shadow-regular-bottom)
│   ├── 页面标题 (heading-regular-3)
│   ├── 章节 (spacing-6 分隔)
│   │   ├── 章节标题 (heading-regular-5)
│   │   └── 内容 (spacing-4 itemSpacing)
│   └── 章节 ...
```

桌面端推荐默认值：
- 页面内边距：`spacing-7`(32) 或 `spacing-8`(40)
- 卡片/Surface 内边距：`spacing-6`(24)
- 章节间距：`spacing-6`(24)；章节标题与内容：`spacing-3`(12)
- 字段列表 itemSpacing：`spacing-4`(16)
- Label 与控件：`spacing-2`(8)

## 8. 反模式

- 禁止给无视觉边界的容器设置 `padding >= 16`。将 padding 上移到最近的 Surface，或改为 `itemSpacing`。
- 禁止连续两层 Surface 都具有较大 padding，造成"无边界留白叠加"。
- 禁止使用 token 体系之外的配色。
- 禁止所有文字使用同一字号和字重，导致层级扁平。
- 禁止添加装饰性效果（大面积渐变、厚重阴影、超大圆角、玻璃拟态）。本系统刻意保持克制。
- 不要默认将每个功能模块包裹在可见 Surface（Card/Panel）中。如果模块不需要独立的视觉边界，使用 Wrapper 做纯布局分组即可。只有当内容需要与周围区域产生视觉区分时，才升级为 Surface。

## 9. 组件尺寸规则

组件尺寸不纳入正式 Token 体系（与开发侧打通），以参考变量形式定义在 `components.html` 的 `:root` 中，前缀 `--ref-`。

### 控件高度档位

| 档位 | 参考变量 | 值 | 适用组件 |
|------|---------|-----|---------|
| xs | `--ref-ctrl-xs` | 16px | Checkbox、Radio、Badge dot |
| sm | `--ref-ctrl-sm` | 24px | Tag、小尺寸按钮、Pagination 紧凑 |
| md | `--ref-ctrl-md` | 32px | 默认控件高度：Button、Input、Select、DatePicker、Pagination |
| lg | `--ref-ctrl-lg` | 40px | Menu item、Tab 卡片项、Table 标准行高 |

### 弹层 / 浮层宽度

| 组件 | 参考变量 | 默认宽度 |
|------|---------|---------|
| Modal | `--ref-modal-w` | 520px（宽屏 720px） |
| Drawer | `--ref-drawer-w` | 372px |
| Notification | `--ref-notification-w` | 384px |
| Tooltip / Popover | `--ref-tooltip-max-w` | 最大 250px |

### 特殊组件

- **Switch**：高度 22px / 小尺寸 16px，不遵循控件高度体系
- **Card header**：56px / 紧凑 38px（`--ref-card-header-h`）
- **Table 行高**：紧凑 40px / 标准 48px / 宽松 56px
- **Avatar**：小 24px / 标准 32px / 大 40px（与控件高度档位对齐）
