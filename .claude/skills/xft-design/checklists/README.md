# Checklists

本目录用于生成完成后的最终验收。

## 子目录分工

- `modules/`：检查单个模块是否满足自身边界与实现约束。
- `page/`：检查整页结构、视觉层级与一致性。
- `demand/`：检查结果是否还原真实需求，没有遗漏核心功能或加入无关内容。

## 不负责

- 重新定义页面结构
- 重新定义模块职责
- 用 checklist 补资产缺陷

## 使用原则

- 若 checklist 与 `rules/` 冲突，以 `rules/` 为准。
- 若 checklist 与 `design-systems/` 冲突，以 `design-systems/` 为准。
- 若 checklist 与 `runtime/` 冲突，以 `runtime/` 为准。
- 验收问题应可直接用于生成后自检与修正。
