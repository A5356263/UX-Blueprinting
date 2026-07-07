# 模块规则

## 筛选区

### 1. 规则标识

- `Rule ID`：`LAYOUT.FILTER_BAR`
- 适用范围：页面主筛选区、列表页顶部筛选区、查询表单条

### 2. 触发条件

- 当前区域承担"筛选结果集"的职责
- 区域内存在查询条件与查询动作
- 区域位于表格、卡片列表、数据结果区之前

### 3. 结构关系

必须：

- 筛选区只承载查询条件、查询动作、重置动作、展开收起动作。
- 同一字段项必须保持 `label + control` 两段语义关系。
- 动作组必须与字段区同属一个筛选区，不得插入任一字段项内部。
- 动作组顺序必须为：`重置 -> 查询 -> 展开/收起`。
- 展开 / 收起必须只依赖一个真实状态源。
- 高级筛选字段与默认筛选字段可以分区，但仍属于同一个筛选区字段系统，不得拆成不同职责模块。

### 4. 禁止事项

- 禁止把批量操作、表格行操作、结果统计主体放入筛选区。
- 禁止拆分同一字段项内的 `label` 与 `control`。
- 禁止让两个不同 toggle 分别维护同一高级筛选区域的展开状态。
- 禁止把筛选区写成表格工具栏、批量操作栏或结果摘要栏。
- 禁止在规则层重写真实 class 名和完整 HTML 实现。

### 5. 条件分支

- 若字段数量较少，则可以不使用展开区。
- 若字段数量较多，则允许将一部分字段放入展开区。
- 若高级字段数量很少，则可以默认展开，并省略展开控件。
- 若当前区域本质不是结果筛选，而是普通表单、搜索框组或工具栏，则不套用本规则。

### 6. Reference Binding

- Primary Reference：`references/blocks/filter-bar.html`
- Required Boundaries：`rules/rewrite-boundaries.md`

### 7. Runtime Contract

若存在展开 / 收起能力，必须使用：

- `data-collapse-root`
- `data-collapse-toggle`
- panel `id`
- `aria-expanded`

不得新增 runtime 之外的 JS。

### 8. Checklist Binding

- `checklists/modules/filter-bar.md`

### 9. 失败回退

- 无法判定是否属于筛选区时，不套用本规则。
- 无法确认是否需要展开区时，默认全部展开。
- 参考资产与真实需求冲突时，优先保留本规则中的职责边界，并对资产做最小改动。

## 操作区

### 1. 规则标识

- `Rule ID`：`MODULE.ACTION_BAR`
- 适用范围：数据页中紧邻表格、列表或结果集上方的操作工具区

### 2. 触发条件

- 当前区域承担结果集相关的页面级操作职责
- 区域与表格、列表或结果区直接关联

### 3. 结构关系

必须：

- 操作区只承载结果集相关操作，不承载查询字段主体。
- 默认采用左侧业务操作、右侧辅助工具的两区关系。
- 左侧业务操作用于推进当前数据业务或改变当前数据状态。
- 右侧辅助工具用于设置、展示调整与工具操作。
- 主按钮必须位于左侧业务操作区最前。
- 图标型工具操作必须位于整个操作区最右。
- 主操作、次操作、批量操作可以同区组织，但仍属于同一个操作区职责系统。
- 操作区中的操作必须直接作用于当前结果区，而不是全局系统设置。
- 页面主按钮唯一性仍受页面级一致性约束，不因工具栏存在而失效。
- 按钮工具区默认保持单行，不因宽度不足自动纵向堆叠。

### 4. 禁止事项

- 禁止把完整筛选字段系统写入操作区。
- 禁止把单条记录详情内容写入操作区。
- 禁止把最终表单提交动作误写成操作区主操作。
- 禁止让多个同层主按钮竞争当前窗口主任务。
- 禁止把操作区误写成筛选区。
- 禁止把页面头部操作、表单底部动作或弹窗底部动作套用成操作区。
- 禁止把批量操作固定成独立中间栏。
- 禁止在操作区使用纯文字按钮作为常规操作形态。
- 禁止把图标工具放在业务操作中间。
- 禁止因为按钮过多直接让工具区自动换成多行。
- 禁止为常规、批量、分段选择等场景拆出多个 action-bar 资产文件。
- 禁止在规则层重写真实 class 名和完整 HTML 实现。

### 5. 条件分支

- 若当前没有明确主业务操作，不强制制造主按钮。
- 若只有少量页面级操作，可以不做复杂分组。
- 高频次级操作可以保留在左侧，低频设置与图标工具继续靠右。
- 若存在批量操作，仍属于当前数据业务操作，不创建固定中间栏。
- 若需求明确表达已选状态，可在左侧业务操作区展示选择上下文与批量动作。
- 不得在 runtime 不支持的情况下伪造动态选择联动。
- 若存在分段选择器或局部上下文控制，可以作为 action-bar 的前置上下文内容。
- 若整体宽度不足，可将上下文控制移到独立前一行。
- 操作按钮本身仍保持单行。
- 若按钮总宽度超过当前可用空间，优先保留主操作与高频操作。
- 低频操作折叠进"更多"。
- "更多"必须使用 `runtime/README.md` 已声明的 disclosure 契约。
- 若当前区域主任务是查询条件输入，不套用本规则，优先判断是否属于 `filter-bar`。

### 6. Reference Binding

- Primary Reference：`references/blocks/action-bar.html`
- Related Reference：`references/components/ant/table/component.html`
- Required Boundaries：`rules/rewrite-boundaries.md`

### 7. Runtime Contract

默认不要求 runtime。

若存在更多操作、下拉显隐或弹层打开能力，只能使用 `runtime/README.md` 中已声明的契约。

### 8. Checklist Binding

- `checklists/page/page-consistency.md`

### 9. 失败回退

- 无法确认是否属于操作区时，不强行套用本规则。
- 无法确认某个动作是否属于结果集操作时，优先不放入操作区。

## 详情区

### 1. 规则标识

- `Rule ID`：`MODULE.DETAIL_SECTION`
- 适用范围：详情页主体、记录摘要下方详情区、结果说明区

### 2. 触发条件

- 当前区域承担单条记录、单个结果或单个配置对象的查看职责
- 区域内以摘要、字段信息、说明块、过程信息为主

### 3. 结构关系

必须：

- 详情区块必须服务单条对象的阅读与理解，不承担主录入职责。
- 摘要信息与详情分组可以并存，但都必须围绕同一对象展开。
- 元数据、说明信息、过程信息可以分组，但不得破坏主阅读顺序。
- 详情区块的组织应优先服务"单对象阅读主线"，不得退化为无主线的信息堆叠。

### 4. 禁止事项

- 禁止把结果列表主体、筛选区或批量操作区写成详情区块。
- 禁止把大量录入控件误写成详情主体。
- 禁止把无关的系统说明或装饰性填充混入详情主线。
- 禁止在规则层把详情规则写成完整详情组件实现。
- 禁止在规则层重写真实 class 名和完整 HTML 实现。

### 5. 条件分支

- 详情信息较少时，可以合并为单个详情区块。
- 详情信息较多时，可以分成多个 section。
- 若当前区域核心是字段录入，不套用本规则，优先判断是否属于 `form-section`。

### 6. Reference Binding

- Primary Reference：`references/blocks/detail-section.html`
- Related Reference：`references/blocks/result-panel.html`
- Required Boundaries：`rules/rewrite-boundaries.md`

### 7. Runtime Contract

默认不要求 runtime。

若存在锚点导航或展开折叠，只能使用 `runtime/README.md` 中已声明的契约。

### 8. Checklist Binding

- 若存在对应详情模块 checklist，则绑定对应文件。
- 若暂无模块 checklist，则至少使用 `checklists/page/page-consistency.md` 做页面级检查。

### 9. 失败回退

- 无法确认是否属于详情区块时，不强行套用本规则。
- 无法确认是否需要分组时，优先保持单对象、清晰阅读主线。

## 弹层

### 1. 规则标识

- `Rule ID`：`MODULE.MODAL`
- 适用范围：确认弹窗、补录弹窗、详情弹窗、选择弹窗

### 2. 触发条件

- 当前内容已经确定在覆盖层内完成确认、补录、选择或查看
- 用户无需离开当前页面主线即可完成该任务

### 3. 结构关系

必须：
- 弹窗必须保持 `header + body + footer actions` 的基本结构。
- 标题、关闭入口、主体内容、底部动作必须服务同一个覆盖层任务。
- 底部动作必须承担确认、取消、关闭或提交职责，不得漂移到主体内容内部。

### 4. 禁止事项

- 禁止把需要完整页面承载的长流程硬塞进弹窗。
- 禁止让弹窗同时承担多个无关主任务。
- 禁止把弹窗主体写成和底部动作完全脱节的独立页面片段。
- 禁止新增 runtime 之外的自定义弹窗 JS。
- 禁止在规则层重写真实 class 名和完整 HTML 实现。

### 5. 条件分支

- 若任务只是轻量确认，可以使用简化弹窗主体。
- 若任务需要录入或选择，可以在弹窗主体中承载表单区块或表格组件。
- 若内容复杂到需要完整导航与长主线，不套用本规则。

### 6. Reference Binding

- Primary Reference：`references/components/ant/modal/component.html`
- Related References：
  - `references/layouts/modal-task.md`
  - `references/components/ant/form/component.html`
  - `references/components/ant/table/component.html`
  - `references/overlays/copy-modal.html`
- Required Boundaries：`rules/rewrite-boundaries.md`

### 7. Runtime Contract

弹层打开关闭必须使用：
- `data-overlay-open`
- `data-overlay-close`
- `data-overlay`
- overlay target `id`
- `hidden`
- `aria-hidden`

不得新增 runtime 之外的 JS。

### 8. Checklist Binding

- 若存在对应弹窗 checklist，则绑定对应文件。
- 若暂时无模块 checklist，则至少使用 `checklists/page/page-consistency.md` 做页面级检查。

### 9. 失败回退

- 无法确认是否适合使用弹窗时，优先回到整页方案判断。
- 无法确认是否需要复杂主体时，优先保持单任务、短主线。
