# Rules

`rules/` 只负责帮助 AI 判断页面主线、区域组织、模块边界与资产改写边界。

## 目录分工

- `page-types/`：判断当前需求属于哪类页面主线。
- `page-structure/`：定义页面区域组织、区域落位与冲突优先级。
- `modules/`：定义具体模块何时使用、承担什么职责、哪些关系不能破坏。
- `asset-boundaries/`：定义基于 `references/` 改写时哪些能改、哪些默认不要改。

## 模块规则标准结构

`rules/modules/*.md` 建议统一包含：

1. 规则标识
2. 触发条件
3. 结构关系
4. 禁止事项
5. 条件分支
6. Reference Binding
7. Runtime Contract
8. Checklist Binding
9. 失败回退

## 不负责

- 默认样式说明
- 默认轻交互实现说明
- 控件尺寸与状态的实现补课
- 参考资产内部的长篇实现讲解
- 生成完成后的最终验收
- 内容区布局骨架资源本身

这些稳定默认实现优先由 `references/`、`design-systems/` 和 `runtime/` 承接，其中内容区骨架资源优先由 `references/layouts/` 承接。

## 模块规则表达原则

模块规则应写：

- 结构关系
- 职责边界
- 禁止事项
- 条件分支
- 参考资产绑定
- 运行时契约名称
- 检查清单绑定

模块规则不应写：

- 真实 class 名
- 大段 HTML 示例
- 大段 CSS 实现
- 大段 JS 实现
- 与 `references/` 重复的稳定默认实现

## 与 references 的关系

- `rules/` 决定“该不该用、怎么判断、哪些关系不能破坏”。
- `references/` 决定“在这些边界内，默认实现通常怎样写更稳”。
- 高频模块规则应声明对应的 primary reference。
- reference 与 rule 冲突时，以 rule 的职责边界为准，对 reference 做最小改动。
- 不要求一个 rule 完全对应一个 reference。
- 不允许为了绑定关系新增模板注册表或 slot 系统。

## 读取顺序

1. 先读 `page-types/`
2. 再读 `page-structure/`
3. 再读相关 `modules/`
4. 再按 `asset-boundaries/` 约束改写 `references/`
5. 生成完成后再读根目录 `checklists/`
