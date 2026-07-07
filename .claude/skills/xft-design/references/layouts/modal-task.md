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
<!-- EDITABLE: 区域组合 - 按需求裁剪区域是否出现、调整区域顺序 -->
<div class="xftv0-layout xftv0-layout-modal-task" data-region="modal">
  <section data-region="modal-header">
    <!-- EDITABLE: 此处使用 references/components/ant/modal/component.html 的 header 部分 -->
  </section>

  <section data-region="modal-body" style="padding: var(--spacing-6); overflow-y: auto;">
    <!-- EDITABLE: 此处按任务使用 references/components/ant/form/component.html 或 table component -->
  </section>

  <section data-region="footer-actions" style="padding: var(--spacing-4) var(--spacing-6); border-top: 1px solid var(--color-border-neutral);">
    <!-- EDITABLE: 底部确认、取消、关闭或提交动作 -->
  </section>
</div>
<!-- /EDITABLE -->
```

## 7.1 Composition

Modal 不使用 `.xftv0-surface`（Modal 组件本身已提供容器）。

间距规则：

- modal-body padding: spacing-6（24px）。
- footer-actions padding: spacing-4（16px）水平 spacing-6（24px），顶部 border 分隔。
- modal-header 间距由 Modal component 内部定义，不在此层设置。
- modal body 内无匹配 block 资产时，必须复用 overlay 已有的 class（`.xftv0-inline-note`、`.xftv0-checkbox-group`、`.xftv0-tag-row`、`.xft-btn`、`.xft-tag`）组织内容，配合 token inline style 控制间距。禁止发明新 class。

## 8. Checklist

生成后至少检查：

- modal 是否只有一个明确任务。
- body 是否服务标题表达的任务。
- footer actions 是否承担确认、取消、关闭或提交职责。
- 是否没有在 layout 中补 Modal 通用视觉或打开关闭。
