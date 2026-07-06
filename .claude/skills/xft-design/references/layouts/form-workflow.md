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
<div class="xftv0-layout xftv0-layout-form-workflow">
  <section data-region="header">
    <!-- PAGE_HEADER_REFERENCE -->
  </section>

  <section data-region="form-content">
    <!-- FORM_COMPONENT_REFERENCE -->
  </section>
</div>
```
