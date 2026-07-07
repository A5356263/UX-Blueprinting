# Token 使用配方

本文件将 token 原始值映射到具体使用场景。生成页面时直接查表，不从 DESIGN.md 散文中推导。

## 1. 颜色配方

### 容器背景

| 场景 | 正确 token | 禁止 |
|------|-----------|------|
| 页面底层背景 | `var(--color-layout-bg-neutral-gray)` | `#f3f4f6`、`gray-100` |
| 白色卡片 / Surface | `var(--color-container-bg-neutral-bright)` | `#ffffff`、`white` |
| 微对比容器（嵌套卡片） | `var(--color-container-bg-neutral-gray)` | `gray-50`、自创灰色 |
| 深色反转区域 | `var(--color-container-bg-neutral-inverse)` | `#132240` |

### 边框

| 场景 | 正确 token | 禁止 |
|------|-----------|------|
| Surface / Card 边框 | `var(--color-border-neutral)` | `#ddd`、`rgba(0,0,0,0.1)` |
| 分割线 | `var(--color-divider-neutral)` | `#eee`、自创浅灰 |

### 文字

| 场景 | 正确 token | 禁止 |
|------|-----------|------|
| 主文字（标题、正文） | `var(--color-text-neutral-gray50)` | `#333`、`black` |
| 次级文字（说明、辅助） | `var(--color-text-neutral-gray40)` | `#666` |
| 弱辅助文字（时间戳、占位） | `var(--color-text-neutral-gray30)` | `#999` |
| 占位符 / 禁用态 | `var(--color-text-neutral-gray10)` | `#ccc` |

## 2. 间距配方

### 页面级间距

| 场景 | token | 实际值 | 禁止 |
|------|-------|--------|------|
| Shell 内容区与页面边缘 | `var(--spacing-6)` | 24px | `16px`、`20px` |
| 两个 Surface 之间 | `var(--spacing-6)` | 24px | `16px`、`20px`、`32px` |
| Surface 内边距 | `var(--spacing-6)` | 24px | `16px`、`20px`、`32px` |
| 章节标题与内容 | `var(--spacing-3)` | 12px | `8px`、`16px` |

### 内容级间距

| 场景 | token | 实际值 | 禁止 |
|------|-------|--------|------|
| 字段列表 itemSpacing | `var(--spacing-4)` | 16px | `12px`、`20px` |
| Label 与控件 | `var(--spacing-2)` | 8px | `4px`、`12px` |
| 按钮组内按钮间距 | `var(--spacing-2)` 或 `var(--spacing-3)` | 8px 或 12px | `16px` |
| 同 Surface 内区域分组 | `var(--spacing-4)` | 16px | `24px`、`32px` |

### 间距规则

- 只有 Surface（具备背景/边框/阴影的元素）拥有 `padding`。
- Wrapper（纯布局容器）使用 `gap` 或 `itemSpacing`，自身 `padding: 0`。
- 若容器 `padding >= 16` 但无视觉边界 → 将 padding 上移到最近的 Surface，或改为 `gap`。
- 禁止连续两层 Surface 都具有较大 padding。

## 3. 圆角配方

| 场景 | token | 实际值 |
|------|-------|--------|
| Surface / Card / Modal / Drawer | `var(--border-radius-large)` | 12px |
| 按钮、输入框、选择器 | `var(--border-radius-regular)` | 6px |
| 标签、小按钮、Checkbox | `var(--border-radius-small)` | 4px |

禁止使用 token 之外的圆角值（如 `8px`、`16px`、`50%` 用于非圆形场景）。

## 4. 阴影配方

| 场景 | token |
|------|-------|
| Card / Surface（默认） | `var(--shadow-regular-bottom)` |
| 下拉菜单 / Popover | `var(--shadow-regular-bottom)` |
| Modal / Dialog | `var(--shadow-large-bottom)` |
| Toast / Tooltip | `var(--shadow-small-bottom)` |
| 浮动主按钮 | `var(--shadow-special1-bottom)` |

禁止使用 `box-shadow` 硬编码阴影值。

## 5. 标题层级配方

| 场景 | token | 实际值 |
|------|-------|--------|
| 页面标题 | `var(--font-size-heading-3)` | 20px |
| Surface 内章节标题 | `var(--font-size-heading-5)` | 16px |
| 正文 | 默认 14px（不引用 token） | 14px |
| 辅助文字 | 默认 12px（不引用 token） | 12px |

标题层级顺序不可跨级（h1 → h2 → h3）。同一页面只有一个 h1。
字重：标题 600（加粗），正文 400（常规）。行高：正文 1.6。

## 6. Surface 与 Wrapper 的使用判定

### 什么时候用 Surface（`.xftv0-surface`）

- 内容需要与页面灰色背景产生视觉区分。
- 内容是一个独立的功能单元（如筛选+操作+表格构成一个完整的管理模块）。
- 内容需要在视觉上被"托起"，形成阅读焦点。

### 什么时候用 Wrapper（`.xftv0-wrapper`）

- 只需要排列子元素，不需要视觉区分。
- 同一 Surface 内的多个子组之间需要间距。

### 什么时候用 Surface--nested（`.xftv0-surface--nested`）

- 在一个 Surface 内部还需要再嵌套一个有独立边界的子区域。
- 极少使用，优先考虑用 Divider 或间距代替。

### 分隔手段优先级（从弱到强）

1. 标题 + 间距（同一 Surface 内，用 Wrapper 分组）
2. Divider 分割线（同一 Surface 内章节划分）
3. 新 Surface（至少选用一项：对比背景色 / 边框 / 阴影）

默认使用手段 1，只有当内容确实需要独立视觉边界时才升级到手段 3。

## 7. 常见合成错误

### 错误 1：每个区域独立一个 Surface

```html
<!-- ❌ 错误：每个区域都裹一层卡片，页面碎片化 -->
<div class="xftv0-surface"><section data-region="filter">...</section></div>
<div class="xftv0-surface"><section data-region="action-area">...</section></div>
<div class="xftv0-surface"><section data-region="primary-data-area">...</section></div>
```

```html
<!-- ✅ 正确：关联区域共享一个 Surface -->
<div class="xftv0-surface">
  <section data-region="filter">...</section>
  <section data-region="action-area">...</section>
</div>
<div class="xftv0-surface">
  <section data-region="primary-data-area">...</section>
</div>
```

### 错误 2：用硬编码值替代 token

```css
/* ❌ 错误 */
.my-card { padding: 16px; border-radius: 8px; background: #fff; }

/* ✅ 正确 */
.my-card { padding: var(--spacing-6); border-radius: var(--border-radius-large); background: var(--color-container-bg-neutral-bright); }
```

### 错误 3：无视觉边界的容器使用大 padding

```html
<!-- ❌ 错误：div 没有背景/边框/阴影，但 padding 24px -->
<div style="padding: var(--spacing-6)">
  <p>内容</p>
</div>

<!-- ✅ 正确：要么加 Surface 获得视觉边界，要么用 Wrapper + gap -->
<div class="xftv0-surface">
  <p>内容</p>
</div>
```

### 错误 4：连续两层 Surface 都有大 padding

```html
<!-- ❌ 错误：外层 Surface padding 24px，内层 Surface padding 20px，留白叠加 -->
<div class="xftv0-surface">
  <div class="xftv0-surface--nested">内容</div>
</div>

<!-- ✅ 正确：外层 Surface 有 padding，内层只用 gap 或间距 -->
<div class="xftv0-surface">
  <div class="xftv0-wrapper">
    <section>内容 A</section>
    <section>内容 B</section>
  </div>
</div>
```
