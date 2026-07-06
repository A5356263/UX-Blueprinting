# 弹窗规则

## 1. 规则标识

- `Rule ID`：`MODULE.MODAL`
- 适用范围：确认弹窗、补录弹窗、详情弹窗、选择弹窗

## 2. 触发条件

- 当前内容已经确定在覆盖层内完成确认、补录、选择或查看
- 用户无需离开当前页面主线即可完成该任务

## 3. 结构关系

必须：
- 弹窗必须保持 `header + body + footer actions` 的基本结构。
- 标题、关闭入口、主体内容、底部动作必须服务同一个覆盖层任务。
- 底部动作必须承担确认、取消、关闭或提交职责，不得漂移到主体内容内部。

## 4. 禁止事项

- 禁止把需要完整页面承载的长流程硬塞进弹窗。
- 禁止让弹窗同时承担多个无关主任务。
- 禁止把弹窗主体写成和底部动作完全脱节的独立页面片段。
- 禁止新增 runtime 之外的自定义弹窗 JS。
- 禁止在规则层重写真实 class 名和完整 HTML 实现。

## 5. 条件分支

- 若任务只是轻量确认，可以使用简化弹窗主体。
- 若任务需要录入或选择，可以在弹窗主体中承载表单区块或表格组件。
- 若内容复杂到需要完整导航与长主线，不套用本规则。

## 6. Reference Binding

- Primary Reference：`references/components/ant/modal/component.html`
- Related References：
  - `references/layouts/modal-task.md`
  - `references/components/ant/form/component.html`
  - `references/components/ant/table/component.html`
  - `references/overlays/copy-modal.html`
- Required Boundaries：
  - `rules/asset-boundaries/reference-rewrite-boundaries.md`
  - `rules/asset-boundaries/component-baselines.md`

## 7. Runtime Contract

弹层打开关闭必须使用：
- `data-overlay-open`
- `data-overlay-close`
- `data-overlay`
- overlay target `id`
- `hidden`
- `aria-hidden`

不得新增 runtime 之外的 JS。

## 8. Checklist Binding

- 若存在对应弹窗 checklist，则绑定对应文件。
- 若暂时无模块 checklist，则至少使用 `checklists/page/page-consistency.md` 做页面级检查。

## 9. 失败回退

- 无法确认是否适合使用弹窗时，优先回到整页方案判断。
- 无法确认是否需要复杂主体时，优先保持单任务、短主线。
