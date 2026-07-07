# UI 质量审查

生成完成后，按 P0 → P1 → P2 顺序逐项检查。P0 必须全部通过，P1 应该通过，P2 可选。

## P0 — CRITICAL（生成前必须满足，不通过则返工）

### P0-1 单主按钮原则

同一视窗内只允许 1 个主视觉主按钮（Primary CTA）。其他操作必须降为默认按钮、次按钮或文字按钮。

检查方法：页面中 `.xft-btn-primary` 或 `btn-type="primary"` 是否只有 1 个。

### P0-2 Surface 包裹完整性

页面中每个功能区域必须被 `.xftv0-surface` 包裹。不存在裸露在灰色背景上的功能内容（如裸露的表格、裸露的表单字段、裸露的筛选栏）。

检查方法：所有 `data-region` section 是否位于某个 `.xftv0-surface` 内部。

### P0-3 Token 合规

合成层的所有间距、颜色、圆角、阴影值必须引用 `design-systems/` token。禁止硬编码值。

检查方法：搜索输出 HTML 中的 `<style>` 和 inline style，确认无 `#xxx`、`rgb()`、`Npx`（token 值之外的）硬编码。

### P0-4 间距节奏一致性

同一页面内，Surface 之间的间距统一为 `spacing-6`（24px）。Surface 内部的区域间距统一为 `spacing-4`（16px）。不存在 `spacing-3` 或 `spacing-5` 用于 Surface 间距或 Surface 内部区域间距的情况。

检查方法：搜索 `gap` 和 `margin` 属性，确认 Surface 间和区域内间距使用正确的 token。

### P0-5 无视觉边界的容器无大 padding

没有 `background` / `border` / `box-shadow` 的容器，其 `padding` 不超过 `spacing-3`（12px）。

检查方法：搜索 `padding >= 16` 的容器，确认其有至少一项视觉属性（背景/边框/阴影）。

### P0-6 FROZEN 区域未被修改

所有 FROZEN 区域的代码与资产原文完全一致，没有被"顺手"修改任何属性值。

检查方法：对比资产原文的 FROZEN 区域与输出文件的对应区域。

## P1 — HIGH（交付前应该满足）

### P1-1 内容区宽度约束

若页面主内容区（如表格、长文本）可能超宽，需要有 `max-width` 约束或使用 Shell 的自然宽度约束。超宽屏下内容不应铺满全屏。

### P1-2 标题层级连续

标题层级从 h1 开始，不跨级（h1 → h2 → h3，不出现 h1 → h3）。同一页面只有一个 h1。

### P1-3 正文行高

正文 `line-height` >= 1.5（当前系统默认 1.6 = 22px / 14px，满足要求）。

### P1-4 数据加载状态

若页面包含需要异步加载的数据区域（表格、列表），需要有 loading 占位或骨架屏，不允许空白页。

注意：HTML 原型中用静态注释或 placeholder div 标注即可。

### P1-5 空状态处理

表格、列表等数据区域在数据为空时，有明确的空状态展示（说明文字 + 引导操作），不是空白区域。

### P1-6 次级信息不压主内容

Surface 层级和视觉权重反映信息优先级。主内容区的 Surface 不应被次级面板在视觉上压过。

### P1-7 连续 Surface 不叠加 padding

不存在两层嵌套的 Surface 都具有大 padding（>= spacing-5）的情况。

## P2 — MEDIUM（建议满足）

### P2-1 覆层过渡

Modal 和 Drawer 有过渡动画（opacity + transform），不是突然出现。

### P2-2 表格数字列

包含数字的表格列使用 `font-variant-numeric: tabular-nums`，防止数字宽度跳动。

### P2-3 图标按钮可访问

所有图标按钮有 `aria-label` 或 `title` 属性。

### P2-4 响应式基本适配

页面在 1280px 宽度下不出现水平滚动条或内容溢出。
