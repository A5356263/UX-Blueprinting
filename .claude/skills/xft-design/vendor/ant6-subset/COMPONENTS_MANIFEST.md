# AntD6 Components Manifest

## 目的

这份清单用于明确：

1. 哪些组件会被抽取到本地
2. 资源来源在哪里
3. 当前组件抽取进度是什么
4. 上层最终会映射成哪些 XFT 资产

## 来源约定

组件源码主参考来源：

1. `node_modules/antd/es/<component>`
2. Ant Design 官方仓库对应版本源码

样式、工具函数和局部依赖允许按需抽取，但不允许整包复制整个 AntD。

## 第一批组件

| 本地目录 | AntD 源组件 | 当前状态 | 上层 adapter | 上层 primitive |
| --- | --- | --- | --- | --- |
| `components/button` | `antd/es/button` | 已接入 | `xft-button.tsx` | `Button` |
| `components/select` | `antd/es/select` | 待抽取 | `xft-select.tsx` | `SelectField` |
| `components/date-field` | `antd/es/date-picker` | 待抽取 | `xft-date-field.tsx` | `DateField` |
| `components/table` | `antd/es/table` | 待抽取 | `xft-table.tsx` | `DataTable` |
| `components/tag` | `antd/es/tag` | 待抽取 | `xft-status-tag.tsx` | `StatusTag` |
| `components/modal` | `antd/es/modal` | 待抽取 | `xft-modal.tsx` | `ModalTask` / 基础 modal 能力 |
| `components/layout` | `antd/es/layout` + `antd/es/menu` | 待抽取 | `xft-layout.tsx` | `AdminSideShell` |

## 第一阶段明确不抽取

1. `form`
2. `upload`
3. `tree`
4. `cascader`
5. `transfer`
6. `drawer`
7. `notification`
8. `message`
9. `tour`
10. `mentions`
11. `auto-complete`
12. `anchor`

## 状态定义

1. `待抽取`：目录已立，但未开始提取真实源码
2. `抽取中`：已开始拆依赖和样式
3. `可预览`：已接入 preview，可在本地预览
4. `已接入`：已由 adapter 和 primitive 正式消费
