# XFT 使用说明

面向  Design Agent 的设计系统包使用指南。

## 阅读顺序

1. 先读本文件，理解 Token 命名约定。
2. 再读 `DESIGN.md`，了解视觉意图、色彩模型、间距规则和反模式。
3. 将 `tokens.css` 粘贴到产物第一个 `<style>` 块中，再编写组件 CSS。
4. 需要时可查阅 `design-tokens.json` 获取机器可读的 Token 清单。

## Token 命名约定

所有 Token 遵循固定维度顺序：`type-object-attribute-intention-prominence-size-direction-index-state`。

- **颜色：** `color-{object}-{attribute}-{intention}-{prominence}[-{state}]`
- **字体：** `font-{object}-{size}[-{index}]` 或 `font-{attribute}-{size}`
- **阴影：** `shadow-{size}-{direction}`
- **间距：** `spacing-{n}`（n = 0-12）
- **圆角：** `border-radius-{size}`

## 关键约定

### 颜色

- `layout` = 页面级不透明背景；`container` = 卡片/面板（允许半透明）
- `intention=neutral` → 布局/结构色。`intention=accent|error|warning|success|info` → 语义色。
- 中性文字：gray50（最强）→ gray10（最弱）。反转文字：inverse50（最亮）→ inverse20（最淡）。
- 容器中性背景为半透明（`bright` 除外），可自动适配父级背景色。

### 间距归属

- 只有 **Surface**（具备填充/边框/阴影的元素）拥有 `padding`。
- **Wrapper**（纯布局容器）使用 `itemSpacing`，默认 `padding: 0`。
- 若容器 `padding >= 16` 但无视觉边界——将 padding 上移或改为 `itemSpacing`。

### Surface 常用视觉组合

```
页面背景:    --color-layout-bg-neutral-gray
卡片背景:    --color-container-bg-neutral-bright
卡片边框:    --color-border-neutral
卡片阴影:    --shadow-regular-bottom
```

### 桌面端表单推荐默认值

| 层级 | 间距 |
|------|------|
| 页面内边距 | `--spacing-7`(32) 或 `--spacing-8`(40) |
| 卡片/Surface 内边距 | `--spacing-6`(24) |
| 章节间距 | `--spacing-6`(24) |
| 章节标题与内容 | `--spacing-3`(12) |
| 字段列表 itemSpacing | `--spacing-4`(16) |
| Label 与控件 | `--spacing-2`(8) |
| 行内控件（按钮组） | `--spacing-2`(8) 或 `--spacing-3`(12) |

## 应当

- 严格使用 `tokens.css` 中定义的 Token 名称。
- 白色卡片表面使用 `--color-container-bg-neutral-bright`。
- 按分隔手段优先级处理区块：标题+间距 → 分割线 → 新 Surface。
- 组件级 itemSpacing 默认使用 `--spacing-4`(16)。

## 避免

- 避免在 `:root` Token 块之外使用裸色值。
- 避免连续两层 Surface 都具有较大 padding。
- 避免给无视觉边界的 Wrapper 设置 `padding >= 16`。
- 避免正文使用 `--color-text-neutral-gray10`（太淡）。
- 避免使用 Token 体系外的装饰效果（大面积渐变、玻璃拟态、超大圆角）。
