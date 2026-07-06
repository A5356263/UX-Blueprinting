# Layout References

本目录存放主内容区布局骨架资源。
它用于帮助 AI 在已经完成页面类型判断后，稳定组织主内容区的区域顺序与区域组合。

## 1. 职责

`references/layouts/` 负责：
- 主内容区内部的区域组织骨架
- 页面主线下的默认区域顺序
- 可直接改写的极简 HTML 骨架
- layout 与稳定资产的映射关系

## 2. 不负责

`references/layouts/` 不负责：
- 最外层页面壳
- topbar / sidebar / page-tabs 这类框架块
- 单个业务块的具体实现
- button / input / table / modal 等控件实现
- 完整整页实例
- runtime 交互实现

## 3. 使用顺序

1. 先读 `rules/page-types/`，判断页面类型。
2. 再读 `rules/page-structure/`，确认区域落位、先后顺序与冲突优先级。
3. 再选择一个最接近的 layout 文件。
4. 再根据区域职责选择合适的 `references` 资产：
   `blocks/`、`chrome/`、`components/`
5. 最后使用 `design-systems/`、`runtime/`、`checklists/` 完成样式、交互和验收。

## 4. Layout Map

| 页面主任务 | 使用 layout |
|---|---|
| 多条记录管理、筛选、批量处理 | `list-management.md` |
| 创建、编辑、提交、配置 | `form-workflow.md` |
| 查看单条记录、状态、结果 | `detail-reading.md` |
| 覆盖层内确认、补录、选择、查看 | `modal-task.md` |
| 左右主从查看、树表联动、对象配置 | `master-detail.md` |
| 多指标概览、运营看板、工作台 | `dashboard-overview.md` |

## 5. 选择原则

- 先保页面主任务清晰，再保布局紧凑。
- 先选更简单的 layout，再按需求增加区域。
- 不为了覆盖所有组合而新增大量相似 layout。
- 若只是局部区域变化，优先改写 blocks，不新增 layout。
- 若只是控件变化，优先继承 components，不新增 layout。
- 不是每个 layout 区域都必须对应一个 block；若区域主体本身就是单一复杂组件，应直接映射到 component。
- `modal-task.md` 只承接覆盖层内部任务内容骨架，不承接 Modal 通用实现与打开关闭。
- 若 layout 与 rules 冲突，以 rules 为准。
