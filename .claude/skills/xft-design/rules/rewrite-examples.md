# 常见改写错误对照

本文件列出 AI 改写资产时最常犯的错误。生成前应先看这些例子，避免重蹈覆辙。

## 错误 1：自创样式值

❌ 错误：把筛选区控件高度从 32px 改成 36px，或把间距从 24px 改成 20px。

```css
/* 错误写法 */
.xftv0-filter-region-field-item {
  column-gap: 12px;  /* 资产是 var(--xftv0-filter-field-inline-gap, 8px) */
}
```

✅ 正确：保持资产原有的 CSS 变量值，不修改任何数值。

```css
/* 正确写法 - 直接继承，不重写 */
.xftv0-filter-region-field-item {
  column-gap: var(--xftv0-filter-field-inline-gap);
}
```

## 错误 2：用硬编码值替代 token

❌ 错误：自写 CSS 时直接写 `color: #333`、`border-radius: 8px`。

```css
/* 错误写法 */
.my-custom-section {
  color: #333;
  border-radius: 8px;
  padding: 20px;
}
```

✅ 正确：新增结构也必须使用 design-systems 的 token。

```css
/* 正确写法 */
.my-custom-section {
  color: var(--color-text-neutral-gray50);
  border-radius: var(--border-radius-large);
  padding: var(--spacing-5);
}
```

## 错误 3：重写交互逻辑

❌ 错误：自己写一套展开/收起的 JavaScript，不使用 runtime 的 data-collapse 契约。

```html
<!-- 错误写法 -->
<button onclick="toggleFilter()">更多筛选</button>
<script>
function toggleFilter() {
  var el = document.getElementById('advanced');
  el.style.display = el.style.display === 'none' ? 'block' : 'none';
}
</script>
```

✅ 正确：使用 runtime 的 data-collapse 契约。

```html
<!-- 正确写法 -->
<button data-collapse-toggle="filter-bar-advanced" aria-expanded="false">
  <span class="toggle-collapsed">更多筛选</span>
  <span class="toggle-expanded">收起筛选</span>
</button>
```

## 错误 4：改写 FROZEN 区域的结构

❌ 错误：觉得资产的外层 div 嵌套"多余"，简化为更少的层级。

```html
<!-- 错误写法 - 去掉了 wrapper 层 -->
<div class="xftv0-filter-region" data-collapse-root>
  ...
</div>
```

✅ 正确：保持资产原有的 div 嵌套结构，即使在 EDITABLE 区域也不要改变外层容器。

```html
<!-- 正确写法 - 保持 wrapper -->
<div class="xftv0-filter-region-wrapper">
  <div class="xftv0-filter-region" data-collapse-root data-collapse-expanded="false">
    ...
  </div>
</div>
```

## 错误 5：自创控件实现

❌ 错误：不看组件基线，自己写一个 select 或 input 的完整样式。

```css
/* 错误写法 - 自写 select 全套样式 */
.my-select {
  appearance: none;
  height: 36px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #fff url("data:image/svg+xml,...");
}
```

✅ 正确：继承 `references/components/ant/` 中对应组件的 CSS 和 HTML 结构。

```html
<!-- 正确写法 - 使用资产中已有的 class -->
<select class="xftv0-select input">
  <option value="">请选择</option>
</select>
```

## 错误 6：同视窗多主按钮

❌ 错误：从 filter-bar 资产复制了 primary 的"查询"按钮，从 action-bar 资产复制了 primary 的"+ 添加"按钮，两者出现在同一视窗。

```html
<!-- 错误：同一视窗有 2 个 primary -->
<nav class="xftv0-filter-region-actions">
  <button class="btn">重置</button>
  <button class="btn btn-primary">查询</button>  <!-- primary 1 -->
</nav>
<div class="xftv0-action-bar">
  <button class="btn btn-primary">+ 添加子管理员</button>  <!-- primary 2 -->
</div>
```

✅ 正确：生成完成后执行全局去重，只保留 action-bar 的主操作为 primary，filter 的"查询"降为默认按钮。

```html
<!-- 正确：只有 1 个 primary -->
<nav class="xftv0-filter-region-actions">
  <button class="btn">重置</button>
  <button class="btn">查询</button>  <!-- 去掉 btn-primary -->
</nav>
<div class="xftv0-action-bar">
  <button class="btn btn-primary">+ 添加子管理员</button>  <!-- 保留唯一 primary -->
</div>
```

优先级规则：弹窗确认按钮 > action-bar 主操作 > filter 查询按钮。

## 错误 7：无资产区域自创 class 泛滥

❌ 错误：弹窗 body 内没有匹配到 block 资产，于是发明了 `.xftv0-source-info`、`.xftv0-section-title`、`.xftv0-checkbox-item`、`.xftv0-target-item` 等十几个新 class。

```css
/* 错误：大量自创 class */
.xftv0-source-info { font-size: var(--font-size-regular); ... }
.xftv0-section-title { font-size: var(--font-size-regular); font-weight: ... }
.xftv0-checkbox-item { display: flex; ... }
.xftv0-target-item { display: flex; ... }
```

✅ 正确：复用 overlay 已有的 class + token inline style。

```html
<!-- 正确：复用 .xftv0-inline-note、.xftv0-checkbox-group、.xft-btn -->
<div class="xftv0-inline-note" style="margin-bottom: var(--spacing-4);">
  说明文字
</div>
<div class="xftv0-checkbox-group" style="flex-direction: column;">
  <label class="xftv0-checkbox-chip"><input type="checkbox" checked />可授权组织</label>
  <label class="xftv0-checkbox-chip"><input type="checkbox" checked />可授权功能</label>
</div>
```

原则：先翻 overlay / component 已有的 class 表，找到能用的就直接用。找不到才新建，新建必须用 token。
