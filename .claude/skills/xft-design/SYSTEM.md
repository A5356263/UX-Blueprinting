# XFT Design System Brief

## 核心目标

`xft-design` 用于生成企业 B 端高保真 React 页面与关键业务区域。

目标不是让 AI 从零发明控件，而是：

- 先用明确规则判断页型、区域职责和模块边界
- 再基于正式 React 资产进行编排
- 最终输出符合设计系统、可稳定复用、可在内网落地的页面原型

## 系统分工

- `rules/`：页型判断、模块职责、资产选择、组合约束、资产边界
- `design-systems/`：token、视觉规则、配方、主题桥接
- `react-system/`：正式 React 实现层
- `checklists/`：最终验收
- `references/reference-notes.md`：压缩后的辅助参考
- `vendor/ant6-subset/`：本地私有 UI 底层能力

## 资产层级

```txt
vendor
-> primitives
-> compositions
-> shells
-> page composition
```

页面层只做编排，不直接消费底层 vendor 组件。

## 结构原则

- 正式主链只保留 React 路线
- 历史 HTML 资产已移出 skill
- registry 统一保留正式资产定位、适用条件与暴露边界
- 不允许在不同层重复定义同一职责

## 生成底线

- 正式资产一旦职责匹配，必须优先复用
- 无现成 composition 时，允许下探 primitive
- 无现成 primitive 时，才允许少量局部 JSX 补充
- 不允许为了迁就资产实现而改写业务需求

## 明确避免

- 模板检索式主链
- slot 硬匹配式主链
- schema 编译式主链
- 旧 HTML 与新 React 双主链并存
- 用 checklist 补结构缺失
