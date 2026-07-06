# 详情区块规则

## 1. 规则标识

- `Rule ID`：`MODULE.DETAIL_SECTION`
- 适用范围：详情页主体、记录摘要下方详情区、结果说明区

## 2. 触发条件

- 当前区域承担单条记录、单个结果或单个配置对象的查看职责
- 区域内以摘要、字段信息、说明块、过程信息为主

## 3. 结构关系

必须：

- 详情区块必须服务单条对象的阅读与理解，不承担主录入职责。
- 摘要信息与详情分组可以并存，但都必须围绕同一对象展开。
- 元数据、说明信息、过程信息可以分组，但不得破坏主阅读顺序。
- 详情区块的组织应优先服务“单对象阅读主线”，不得退化为无主线的信息堆叠。

## 4. 禁止事项

- 禁止把结果列表主体、筛选区或批量操作区写成详情区块。
- 禁止把大量录入控件误写成详情主体。
- 禁止把无关的系统说明或装饰性填充混入详情主线。
- 禁止在规则层把详情规则写成完整详情组件实现。
- 禁止在规则层重写真实 class 名和完整 HTML 实现。

## 5. 条件分支

- 详情信息较少时，可以合并为单个详情区块。
- 详情信息较多时，可以分成多个 section。
- 若当前区域核心是字段录入，不套用本规则，优先判断是否属于 `form-section`。

## 6. Reference Binding

- Primary Reference：`references/blocks/detail-section.html`
- Related Reference：`references/blocks/result-panel.html`
- Required Boundaries：
  - `rules/asset-boundaries/reference-rewrite-boundaries.md`
  - `rules/asset-boundaries/component-baselines.md`

## 7. Runtime Contract

默认不要求 runtime。

若存在锚点导航或展开折叠，只能使用 `runtime/README.md` 中已声明的契约。

## 8. Checklist Binding

- 若存在对应详情模块 checklist，则绑定对应文件。
- 若暂无模块 checklist，则至少使用 `checklists/page/page-consistency.md` 做页面级检查。

## 9. 失败回退

- 无法确认是否属于详情区块时，不强行套用本规则。
- 无法确认是否需要分组时，优先保持单对象、清晰阅读主线。
