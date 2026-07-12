# React 资产边界

## 硬规则

- 禁止直接在页面代码中 `import { ... } from "antd"`
- 必须优先使用 `registry` 中声明的正式资产
- `composition` 足够时，不下探到底层 `primitive`
- `primitive` 足够时，不写第二套重复 JSX
- 局部补充 JSX 时，仍必须使用 `design-systems/` token

## 允许的下探顺序

1. shell
2. composition
3. primitive
4. 局部 JSX 补充

## 禁止行为

- 直接暴露完整 AntD Table / Form API 给 AI
- 为一次性结构建立第二套常用组件
- 在页面文件中散写大量样式常量
- 绕过 `Panel` / `StatusTag` 这类正式基础资产
