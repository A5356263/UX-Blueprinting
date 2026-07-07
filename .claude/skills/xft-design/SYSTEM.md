# XFT Design System Brief

## 核心目标

`xft-design` 用于生成企业 B 端高保真 HTML 页面、弹层与局部区域。

它的目标不是让 AI 从零发明控件，而是：

- 先用明确规则判断页面主线、区域组织和模块边界
- 再基于稳定 `references` 资产做受约束的改写
- 最终输出符合设计系统、可预览、可运行轻交互的 HTML

## 适用场景

- 列表页
- 表单页
- 详情页
- 弹窗页
- 局部区域生成
- 基于现有资产改写页面区块

## 系统原则

- `references/` 承接稳定默认实现，包括结构、样式、轻交互和已验证的适配机制。
- `references/shells/` 承接最外层页面宿主。
- `references/chrome/` 承接框架级界面块。
- `references/layouts/` 承接内容区布局骨架。
- `references/blocks/` 承接业务区域块。
- `references/components/` 承接控件基线。
- `rules/` 只承接判断边界、职责边界与改写护栏。
- `checklists/` 独立承接生成完成后的最终验收。
- `design-systems/` 承接 token、视觉语言和控件档位。
- `runtime/` 只承接公共、重复、稳定的轻交互。
- 页面本地 JavaScript 只承接当前页面确定性业务状态，不进入 `runtime/`。
- 不要为了单个页面需求扩展 Runtime。

## 规则与资产分工底线

- 若一条信息主要回答“什么时候用、承担什么职责、什么不能破坏、失败时怎么回退”，进入 `rules/`。
- 若一条信息主要回答“默认真实实现怎么写更稳”，进入 `references/`。
- 若一条信息主要回答视觉 token、排版、尺寸档位，进入 `design-systems/`。
- 若一条信息主要回答公共轻交互契约，进入 `runtime/`。

## 组件层底线

- `summary.md` 只保留组件定位、默认结论、改写边界与关联规则。
- `component.html` 统一承接组件真实默认实现，包括结构、样式、状态与已支持轻交互。
- 不允许把具体实现细节重新堆回 `summary.md`。
- 不允许在 `summary.md` 与 `component.html` 双写同一实现信息。

## 生成底线

- `Design Spec` 或用户需求先决定本次有哪些界面设计对象要生成。
- 页面对象必须完整生成页面。
- 非页面对象不主动扩成整页。
- 稳定资产一旦职责匹配，必须真正作为代码起稿基线。
- 无资产时，允许基于 `rules/`、`design-systems/` 与已有组件基线直接生成。
- 不允许为了迁就资产或 Runtime 改写需求业务语义。

## 交互底线

- Runtime 负责公共轻交互。
- Reference 本地脚本只做只读适配。
- 页面本地 JavaScript 只做当前页面确定性业务状态。
- 页面本地 JavaScript 不得重写 Runtime 已有能力。
- 页面本地 JavaScript 不得伪造真实服务端能力。
- 即使多个页面写法相似，也不要在生成阶段顺手上提为公共 Runtime。

## 明确避免

- 不做模板检索系统
- 不做 slot 硬匹配系统
- 不做 schema 编译主线
- 不让 AI 每次从零重写按钮、输入框、展开收起与适配机制
- 不把大量稳定实现说明继续堆回 `rules/`
- 不把 `checklists/` 当成补结构或补资产缺陷的地方
- 不新增 registry / schema / 状态机 / 自动校验器 / CLI 编排层
