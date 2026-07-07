# Form Workflow Layout

## 1. 定位

用于已经判定为 `PAGE_TYPE.FORM` 的整页表单主内容区骨架。
不定义字段控件实现。
不用于 Modal / Drawer 内部表单。

## 2. Region Order

默认顺序：

```text
header -> form content -> final actions
```

可选分支：

- 字段较多时，form content 内可分组。
- 存在步骤流程时，可在 form content 前加入 steps。

## 3. Asset Mapping

推荐映射：

- header：`references/blocks/page-header.html`
- form content：`references/components/ant/form/component.html`

Final actions 默认继承 Form component 的稳定 actions 构造。

## 4. HTML Skeleton

```html
<!-- EDITABLE: 区域组合 - 按需求裁剪区域是否出现、调整区域顺序 -->
<div class="xftv0-layout xftv0-layout-form-workflow">
  <!-- 单个 Surface：表单整体是一个功能单元 -->
  <div class="xftv0-surface">
    <div class="xftv0-wrapper">
      <section data-region="header">
        <!-- EDITABLE: 此处使用 references/blocks/page-header.html -->
      </section>

      <section data-region="form-content">
        <!-- EDITABLE: 此处使用 references/components/ant/form/component.html -->
      </section>
    </div>
  </div>
</div>
<!-- /EDITABLE -->
```

## 4.1 Composition

默认包裹策略：

- 单个 Surface 包裹 header + form-content：表单是一个完整的功能单元，不应被拆成多个卡片。
- Surface 内部使用 `.xftv0-wrapper`（gap: spacing-4）控制 header 与表单之间的间距。

裁剪规则：

- 字段较多需分组时，在 Surface 内部使用 Divider 分隔各组（不创建新 Surface）。
- 若存在步骤流程（Steps），Steps 与表单内容同在一个 Surface 内。
