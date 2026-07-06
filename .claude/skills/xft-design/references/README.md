# 参考资料说明
本目录存放的是可信参考代码，不是必须命中的模板。

## 目的

这些文件用于稳定：
- 局部结构
- 间距节奏
- 元素组合关系
- 常见企业后台局部写法
- 控件实现基线

## 使用规则

- 参考块只是可信样例，不是强制模板。
- AI 可以按当前需求改写参考块。
- 改写后仍必须服从 `rules/` 中的硬规则。
- 如果参考块与硬规则冲突，以硬规则为准。
- 区域块允许改写，但块内部控件实现应优先继承组件基线。
- 若某些信息属于稳定默认实现，而不是需求决策边界，应优先放在 `references/`，不要重复堆进 `rules/`
- 高频区域块应尽量做到单独打开时也能成立，至少结构、默认样式和已支持的轻交互要自洽

## 与规则的分工

- `rules/` 负责回答：这个区域该不该出现、结构关系如何决策、哪些写法被禁止
- `references/` 负责回答：在这些边界内，默认实现通常怎样写更稳
- `references/` 可以比 `rules/` 更具体，但不能反向定义新的决策规则
- 同一条信息若已经是稳定默认值，应只保留在 `references/`，避免与 `rules/` 双写
- `references/blocks/` 的目标不是截图式静态片段，而是完整可改写的区域资产
- `references/blocks/` 允许改写，但稳定部分默认冻结；具体边界以 `rules/asset-boundaries/reference-rewrite-boundaries.md` 为准

## 目录职责

- `shells/`：最外层页面壳与整页宿主结构
- `layouts/`：内容区布局骨架资源
- `chrome/`：框架级界面块，如侧边菜单、顶部导航、页签栏
- `blocks/`：区域级 HTML 参考块
- `overlays/`：仅承接有独立复用价值的业务覆盖层组合资产，不作为 Modal 通用基础实现的第二来源
- `components/`：本地组件实现基线与参考资料

## shells 边界

`references/shells/` 负责：
- 最外层页面宿主结构
- shell 内主要区域槽位
- 页面整体滚动与宿主关系
- chrome、content、overlay 的装配位置

`references/shells/` 不负责：
- topbar 具体实现
- sidebar 具体实现
- page-tabs 具体实现
- 主内容区业务结构
- 单个业务模块实现

shell 中的框架块应继续由 `references/chrome/` 提供。
