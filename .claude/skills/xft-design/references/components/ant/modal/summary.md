# 弹窗 Summary

## 1. 组件定位

- 弹窗用于承接需要遮罩聚焦处理的临时任务、确认动作与轻量表单。
- 适合确认、补录、选择、查看这类短任务，不承接长流程页面。

## 2. 默认结论

- 默认保持 `header + body + footer actions` 三段结构。
- 默认宽度档位使用 `740`，高频轻任务档位使用 `480`。
- `1060 / 1200` 只在内容信息量明显增加时使用。
- 多状态弹窗复用同一套 `header + body + footer actions` 结构。
- 状态切换只替换各段内容；body 继续承担滚动，footer 始终位于 body 之外。
- 内容较高时由 body 区域承担滚动。
- 打开关闭沿用 runtime overlay 契约。
- 主按钮唯一性在页面级检查中统一约束。

## 3. 改写边界

- 可改：标题、空 body 中实际承载的内容、宽度档位、底部动作文案、body 承载的表单/表格/详情内容。
- 默认不改：overlay 与 modal 的层级关系、header/body/footer 结构、关闭入口位置、body 滚动方式、footer 位置、runtime 契约。
- 多状态切换不得重复或嵌套完整 Modal 结构，也不得由状态容器接管 body 的滚动职责。

## 4. 关联规则

- 使用边界受 `rules/page-types/modal-page.md` 与 `rules/modules/modal.md` 共同约束。
- 页面一致性检查使用 `checklists/page/page-consistency.md`。
- 真实默认实现以 `component.html` 为准。
