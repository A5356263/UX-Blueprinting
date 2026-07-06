# Modal Task Layout

## 1. 定位

用于覆盖层内完成确认、补录、选择或查看任务的内容骨架。
该 layout 只定义 modal 内部主线，不定义 modal 通用实现与 overlay 打开关闭。

## 2. Use When

适用于：

- 当前任务发生在覆盖层内。
- 用户无需离开当前页面即可完成确认、补录、选择或查看。
- 任务较短，不需要完整页面导航。

## 3. Must Not

禁止：
- 不把长流程硬塞进 modal。
- 不让 modal 同时承担多个无关主任务。
- 不把底部确认动作放入 body 内部。
- 不在 layout 中补 Modal 通用视觉与尺寸实现。
- 不在 layout 中实现 overlay open / close 行为。

## 4. Region Order

默认顺序：
```text
modal header -> modal body -> footer actions
```

可裁剪：

- 轻量确认可简化 body。
- 补录任务可在 body 内承载 form component。
- 选择任务可在 body 内承载 list 或 table component。
- 内容复杂到需要完整导航时，应退回整页 layout。

补充约束：

- 当 modal body 承载 form component 且外层已经提供 footer actions 时，Form 内部不重复承载最终动作。

## 5. Allowed Changes

允许改写：
- modal 标题。
- body 内容类型。
- footer actions 文案。
- modal 宽度档位。
- 是否包含说明、表单、列表。

默认不改：
- header + body + footer actions 三段关系。
- 关闭入口位置。
- footer actions 的基础位置。
- overlay 层级与 runtime 契约。

## 6. Asset Mapping

推荐映射：
- modal frame：`references/components/ant/modal/component.html`
- form body：`references/components/ant/form/component.html`
- list body：`references/components/ant/table/component.html`

如果对应 asset 不存在，应优先补对应资产。

## 7. HTML Skeleton

```html
<div class="xftv0-layout xftv0-layout-modal-task" data-region="modal">
  <section data-region="modal-header">
    <!-- modal component header -->
  </section>

  <section data-region="modal-body">
    <!-- modal body task content -->
  </section>

  <section data-region="footer-actions">
    <!-- footer actions -->
  </section>
</div>
```

## 8. Checklist

生成后至少检查：

- modal 是否只有一个明确任务。
- body 是否服务标题表达的任务。
- footer actions 是否承担确认、取消、关闭或提交职责。
- 是否没有在 layout 中补 Modal 通用视觉或打开关闭。
