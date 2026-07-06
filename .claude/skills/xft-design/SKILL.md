---
name: xft-design
version: "12.0"
description: 基于页面组织规则、区域职责规则、稳定参考资产与设计系统，直接生成企业 B 端 HTML 高保真原型。
---

# XFT 设计技能

## 定位

本技能用于生成企业 B 端页面、弹层与局部区域的高保真 HTML 原型。

本技能不是：

- 模板检索系统
- 模板分配系统
- slot 填空系统
- schema 编译主线
- React 组件装配器
- 运行时组件库集成器

更准确地说：

> 系统先提供稳定的页面壳、内容骨架、功能模块、设计系统与轻交互契约，AI 再根据需求去选择、组合、裁剪、改写这些预制资产，输出页面原型。

这里的“改写”指的是：

> AI 先读取页面类型、页面组织、区域职责、模块边界与改写边界，再在稳定资产上做需求相关调整。

不是：

- 先命中模板再填空
- 先找相似块再机械套用
- 先自由生成再回头补样式

## 生成总纲

- `Design Spec` 或用户需求先决定本次有哪些界面设计对象要生成。
- `rules/` 决定这些对象如何组织。
- `references/` 提供稳定代码起点；匹配到稳定资产时，直接从资产代码起稿。
- `design-systems/` 提供视觉基线。
- `runtime/` 负责公共轻交互。
- 页面本地 JavaScript 只负责当前页面确定性业务状态。

## 工作流

### Step 0

读取用户需求或 `Design Spec`，先列出本次明确要求生成的全部界面设计对象。

界面设计对象包括：

- 独立页面
- 页面所属的 Modal / Drawer
- 明确要求生成的独立区域
- 同一界面中的关键业务状态

默认生成 `Design Spec` 中被明确描述为设计对象的全部对象；只有明确标记“不生成”的内容排除。
不得使用“主生成 / 关联生成”重新划分需求范围。

以下内容不自动视为界面设计对象：

- 纯背景事实
- 外部系统名称
- 仅被提到的跳转目标
- 非界面实体
- 未被描述为设计对象的流程上下文

### Step 1

读取 `rules/page-types/` 下相关文件，确定页面类型。

### Step 2

读取 `rules/page-structure/page-organization.md`，确定页面组织方式。

### Step 3

读取 `rules/page-structure/region-placement.md`，确定区域列表与区域职责。

### Step 4

读取 `rules/page-structure/priority-rules.md`，处理区域优先级、冲突与回退。

### Step 5

读取 `rules/asset-boundaries/component-baselines.md`，确定哪些内容属于实现常量，必须继承稳定基线。

### Step 6

读取 `rules/asset-boundaries/reference-rewrite-boundaries.md`，确定哪些 `references` 内容允许改写，哪些默认冻结。

### Step 7

按页面涉及的模块读取 `rules/modules/` 下的相关文件。

### Step 8

对每个待生成界面对象执行基线起稿：

1. 先根据 `rules/` 确定界面与区域结构。
2. 再检查是否存在职责匹配的稳定 `references`。
3. 有稳定资产时，直接以对应资产代码作为起稿基线。
4. 无高层资产但有已有 `component` 时，使用组件基线组合生成。
5. 无对应资产时，按 `rules/` + `design-systems/` 直接生成。

要求：

- 资产不存在不得阻断生成。
- 资产也不得反向决定需求对象是否存在。
- 页面实际使用仓库已有组件时，必须读取并继承对应 `component` 基线。
- 不以“最像”为理由强套资产。

### Step 9

读取 `design-systems/`，应用 token、间距、排版、尺寸与视觉边界。

### Step 10

组合并改写页面 HTML。

要求：

- 页面对象必须完整生成页面。
- 非页面对象不主动扩成整页。
- 结构决策必须来自规则。
- 已有稳定资产优先继承，不重写同职责第二套实现。
- 只改需求相关部分，不改无关稳定基线。
- 内容变化默认不自动增加图标、装饰或额外结构。
- 最终产物统一输出到项目根目录 `outout/`。

### Step 11

交互职责按三层处理：

- 公共轻交互使用 `runtime/basic-interactions.js`
- `references` 本地脚本只做只读适配
- 页面本地 JavaScript 只负责当前页面确定性业务状态

页面本地 JavaScript 不得：

- 重写 Runtime 已有能力
- 新增公共状态框架
- 伪造真实网络、数据库、权限服务或真实后端过程

### Step 12

读取 `checklists/` 下的相关清单，自检并修正：

- `checklists/modules/`
- `checklists/page/`
- `checklists/demand/`

### Step 13

按独立页面分别输出最终 HTML。

## 输入

本技能读取：

- 用户需求 / `Design Spec`
- `design-systems/`
- `rules/`
- `references/`
- `runtime/`
- `assets/`
- `test-inputs/`（用于固定测试输入时）

## 输出

默认输出为：

- 可预览的 HTML
- 遵循 `design-systems/` 的样式
- 公共轻交互使用 Runtime
- 需求特有业务状态使用页面本地 JavaScript
- 满足对应 `checklists/` 的结构、视觉与交互自检
- 全部文件统一落到项目根目录 `outout/`

输出约束：

- 按独立页面分别输出 HTML
- 页面所属弹层与页面内状态保留在所属页面文件中
- 不把多个独立页面合并成一个超级 HTML

## 生成前确认

- `Design Spec` 中的界面设计对象是否都已纳入输出，且只排除了明确不生成的内容？
- 有稳定资产的部分是否真的直接从资产代码起稿？
- 当前实现是否保持了需求业务语义，没有为了迁就资产或 Runtime 改写需求？

## 资产边界

### `design-systems/`

负责：

- 视觉 token
- 间距尺度
- 排版规则
- 组件尺寸规则
- 产品视觉语言

不负责：

- 页面结构组织
- 区域职责判断
- 布局组合决策

### `rules/`

负责：

- 页面类型判断
- 页面组织与区域落位
- 模块边界规则
- 资产改写护栏

不负责：

- 视觉样式实现
- 参考代码存档
- 轻交互实现
- 大部分稳定默认实现说明

### `references/`

负责：

- 稳定的页面壳
- 稳定的框架级界面块
- 内容区布局骨架资源
- 稳定的功能模块块
- 稳定的覆盖层参考
- 本地组件参考资产

这些文件的长期定位是：

> AI 允许拿来组合和改写的预制块资产。

同时它也承担一部分稳定默认实现职责，例如：

- menu / topbar / page-tabs 这类固定落位框架块
- 内容区默认区域顺序与组合骨架
- 区域默认骨架
- 稳定的字段排布写法
- 已验证过的动作区落位
- 不需要每次重新推理的结构默认值
- 已支持轻交互的默认接法

### `runtime/`

负责：

- 公共、重复、稳定的轻交互
- 稳定的 `data-*` 行为契约

### `assets/`

负责：

- 图标
- 图片
- Logo
- 插画
- 其他仅引用、不参与结构推理与改写的原始静态资源

### `test-inputs/`

负责：

- 固定 Skill 测试输入
- 保持测试口径一致

## 目录约束

当前技能目录只保留以下结构：

- `SYSTEM.md`
- `design-systems/`
- `assets/icons/`
- `checklists/`
- `runtime/`
- `references/`
- `rules/`
- `test-inputs/`

以下旧结构已废弃，不允许重新引入：

- 检索注册表
- 模板分配主线
- schema 编译
- slot 改写系统
- `foundation.css` 这类额外样式抽象层
- 额外的双入口说明文件

## 必读顺序

1. `rules/page-types/` 下相关文件
2. `rules/page-structure/page-organization.md`
3. `rules/page-structure/region-placement.md`
4. `rules/page-structure/priority-rules.md`
5. `rules/asset-boundaries/component-baselines.md`
6. `rules/asset-boundaries/reference-rewrite-boundaries.md`
7. `rules/modules/` 下相关文件
8. `references/shells/` 下相关文件
9. `references/chrome/` 下相关文件
10. `references/layouts/` 下相关文件
11. `references/blocks/`、`references/overlays/`、`references/components/` 下相关文件
12. `design-systems/` 下相关文件
13. `runtime/README.md`
14. `checklists/` 下相关文件

## 不可违反的约束

- 不要重新引入模板检索与模板分发逻辑
- 不要把参考块当成必须命中的模板
- 不要把稳定资产块当成匹配目标
- 不要创建类似 `foundation.css` 的第二层样式抽象
- 不要在 `runtime/` 之外发明新的交互系统
- 不要让页面本地 JavaScript 演变成第二套 Runtime
- 不要为了“更聪明”不断叠加中间机制
- 不要让不同目录共同承担同一类决策职责

## 自检要求

- 页面组织方式必须匹配主任务
- 每个区域必须只有清晰职责
- 布局决策必须来自显式规则
- token 必须来自 `design-systems/`
- 视觉节奏不得偏离 `design-systems/`
- 公共轻交互必须走 `runtime/`
- 最终输出必须通过对应 checklist
