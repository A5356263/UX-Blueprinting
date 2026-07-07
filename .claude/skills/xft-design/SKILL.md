---
name: xft-design
version: "14.1"
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

- 链式模式下，优先读取 `page-spec` 产物作为本次原型生成的主输入。
- `Design Spec` 或用户需求先决定本次有哪些界面设计对象要生成。
- `rules/` 决定这些对象如何组织。
- `references/` 提供稳定代码起点；匹配到稳定资产时，直接从资产代码起稿。
- `design-systems/` 提供视觉基线。
- `runtime/` 负责公共轻交互。
- 页面本地 JavaScript 只负责当前页面确定性业务状态。

## 链式接入（接在 page-spec 之后）

当当前项目中存在以下产物时，默认按链式模式执行：

- `spark-output/context/page-spec.json`
- `spark-output/page_spec.md`

链式模式下的输入职责：

- `page-spec.json`：页面实体、页面类型、状态与异常范围的主输入
- `page_spec.md`：页面结构、交互规则、文案与补充说明

链式模式下，不再自行猜测页面目标、实体边界、主次流程范围，优先以 `page-spec` 产物为准。

如果上述两个文件都不存在，再回退到独立模式，读取 `Design Spec` 或用户需求直接生成。

## 工作流

### Step 0：确定生成对象

优先读取 `spark-output/context/page-spec.json` 和 `spark-output/page_spec.md`。若不存在，再读取用户需求或 `Design Spec`，列出本次明确要求生成的全部界面设计对象。

界面设计对象包括：

- 独立页面
- 页面所属的 Modal / Drawer
- 明确要求生成的独立区域
- 同一界面中的关键业务状态

默认生成 `Design Spec` 中被明确描述为设计对象的全部对象；只有明确标记"不生成"的内容排除。
不得使用"主生成 / 关联生成"重新划分需求范围。

以下内容不自动视为界面设计对象：

- 纯背景事实
- 外部系统名称
- 仅被提到的跳转目标
- 非界面实体
- 未被描述为设计对象的流程上下文

### Step 1：确定页面结构

读取 `rules/page-structure.md`，完成以下决策：

1. 确定页面类型（列表管理 / 表单 / 详情 / 弹窗）。
2. 确定区域列表（按页面类型的主线结构列出本次页面包含的区域）。
3. 确定页面壳选择（admin-side-shell 或 admin-top-shell）。

若存在冲突，按 `rules/page-structure.md` 末尾的冲突优先级处理。

若当前页面涉及特定模块（筛选区、操作区、详情区、弹层），读取 `rules/modules.md` 中对应章节，确认该模块的结构关系和禁止事项。

### Step 2：确定改写边界

读取 `rules/rewrite-boundaries.md`，明确：

- 当前页面的每个区域中，哪些内容属于需求变量（允许改写）。
- 哪些内容属于实现常量（不可改写）。
- 在什么条件下允许突破冻结。

同时读取 `rules/rewrite-examples.md`，了解最常见的改写错误，避免在 Step 4 中重蹈覆辙。

### Step 3：读取资产基线

按当前页面涉及的区域，依次读取：

1. 对应的 `references/layouts/` 文件，获取主内容区骨架和资产映射关系。
2. 对应的 `references/shells/` 文件，获取页面壳代码。
3. 对应的 `references/chrome/` 文件，获取框架级界面块代码。
4. 对应的 `references/blocks/` 文件，获取业务区域块代码。
5. 对应的 `references/components/ant/` 文件（先 summary.md 判断适用性，再 component.html 获取实现代码）。
6. `design-systems/` 下相关文件，获取 token 和视觉边界。
7. `runtime/README.md`，获取可用交互契约。

只读当前页面涉及的资产，不读全集。layout 文件的 "Asset Mapping" / "Block Mapping" 节列出了需要读取的具体资产文件。

### Step 4：生成 HTML

**强制程序：复制后修改，不是参考后重写。**

对每个待生成界面对象，按以下顺序生成：

1. **复制**：将匹配到的资产代码原样写入输出文件。包括 `<style>` 内容、HTML 结构、`<script>` 内容。不做任何修改。
2. **定位**：在输出文件中找到 `<!-- EDITABLE -->` 标记的区域。
3. **替换**：只在 EDITABLE 区域内，按需求做内容替换（改字段名称、字段数量、文案、数据行等）。
4. **冻结确认**：`<!-- FROZEN -->` 区域内的代码不做任何修改。
5. **合成**：按当前 layout 骨架的 Composition 规则，用 `.xftv0-surface` 包裹区域组，用 `.xftv0-wrapper` 控制内部间距。参照 `design-systems/token-recipes.md` 确认所有间距、颜色、圆角、阴影使用 token。
6. **全局去重**：扫描同一可视视窗内的所有主按钮（`.xft-btn-primary`、`.btn-primary`、`.xftv0-button-primary`）。只保留 1 个 primary，其余去掉 primary class 降为默认按钮。优先级：弹窗确认按钮 > action-bar 主操作 > filter 查询按钮。

约束：

**资产内部（FROZEN/EDITABLE 区域内）：**

- 不新增 CSS 规则，除非需求明确要求了资产中不存在的结构。
- 不修改已有 CSS 的属性值（颜色、间距、尺寸、圆角、阴影等）。
- 不添加资产中不存在的装饰性元素（图标、分隔线、背景色块等）。
- 不以"看起来更好"为由重写任何 FROZEN 区域的代码。

**合成层（资产之间的包裹和组合）：**

- 必须按当前 layout 骨架的 Section 7.1 Composition 规则，使用 `.xftv0-surface` 包裹区域组。
- 合成层的所有样式必须使用 `design-systems/` 的 token，禁止硬编码值。
- 合成层禁止自创 CSS class（使用 `.xftv0-surface`、`.xftv0-surface--nested`、`.xftv0-wrapper` 或 `design-systems/token-recipes.md` 中定义的 token）。
- 合成层禁止添加装饰性元素（渐变、玻璃拟态、超大圆角、装饰图标等）。

**全局：**

- 页面对象必须完整生成页面。非页面对象不主动扩成整页。
- 已有稳定资产优先继承，不重写同职责第二套实现。
- 最终产物统一输出到 `spark-output/xft-design/`。
- 全页面禁止自创 CSS class。有资产的区域用资产 class；无资产的区域优先复用 overlay / component 已有的 class（如 `.xftv0-inline-note`、`.xftv0-checkbox-group`、`.xftv0-tag-row`、`.xft-btn`、`.xft-tag`），配合 token inline style 组织内容。仅在已有 class 确实无法覆盖时允许新建，新建 class 必须使用 token 变量。

若某个区域无匹配资产：按 `rules/page-structure.md` 的区域规则 + `design-systems/` 的 token 体系直接生成。此情况下不受 EDITABLE/FROZEN 约束（因为没有资产可继承），但必须优先复用当前页面已加载的 overlay / component class（如 `.xftv0-inline-note`、`.xftv0-checkbox-group`、`.xft-btn`、`.xft-tag`），不足时才允许新建 class。新建 class 必须使用 token 变量，禁止硬编码值。

### Step 5：交互接入

交互职责按三层处理：

- 公共轻交互使用 `runtime/basic-interactions.js`（tabs、collapse、menu、overlay、disclosure、switch、anchor）。
- `references/` 本地脚本只做只读适配（已在 FROZEN 区域中，不修改）。
- 页面本地 JavaScript 只负责当前页面确定性业务状态。

页面本地 JavaScript 只允许三种操作：

- 调用 `runtime/` 提供的函数或 data-* 契约。
- 切换 DOM 元素的 class 或 data-* 属性。
- 响应 `runtime/` 派发的事件。

页面本地 JavaScript 不得：

- 重写 Runtime 已有能力。
- 新增公共状态框架。
- 伪造真实网络、数据库、权限服务或真实后端过程。
- 使用 fetch、setTimeout 模拟异步操作。
- 实现自定义路由跳转逻辑。

### Step 6：自检与输出

读取以下清单，逐项自检并修正：

- `references/ui-review.md`（**P0 必须全部通过，P1 应该通过**）
- `checklists/modules/`
- `checklists/page/`
- `checklists/demand/`

重点验证（在现有 checklist 基础上新增的检查项，详见任务 E）：

- FROZEN 区域代码是否未被修改（对比资产原文）。
- CSS 变量名和值是否与资产一致。
- 是否只修改了 EDITABLE 区域内的内容。

自检通过后，按独立页面分别输出最终 HTML。

## 输入

本技能读取：

- `spark-output/context/page-spec.json`（如存在）
- `spark-output/page_spec.md`（如存在）
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
- 全部 HTML 文件统一落到 `spark-output/xft-design/`
- 链式模式额外写入 `spark-output/context/xft-design.json`

输出约束：

- 按独立页面分别输出 HTML
- 页面所属弹层与页面内状态保留在所属页面文件中
- 不把多个独立页面合并成一个超级 HTML

`xft-design.json` 最小字段：

```json
{
  "skill": "xft-design",
  "version": "14.1",
  "generated_at": "",
  "source": "page-spec | standalone",
  "primary_html": "",
  "html_files": []
}
```

## 生成前确认

- `Design Spec` 中的界面设计对象是否都已纳入输出，且只排除了明确不生成的内容？
- 有稳定资产的部分是否真的复制了资产代码（不是自己重写了一套相似的）？
- FROZEN 区域代码是否与资产原文一致？
- 当前实现是否保持了需求业务语义，没有为了迁就资产或 Runtime 改写需求？
- **合成层是否按 layout 骨架的 Composition 规则包裹了 Surface？所有合成层样式是否使用了 token？**

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

1. `rules/page-structure.md`
2. `rules/rewrite-boundaries.md`
3. `rules/rewrite-examples.md`
4. `rules/modules.md`（只读当前页面涉及的模块章节）
5. `references/layouts/` 下匹配的文件（**特别注意 Section 7.1 Composition**）
6. `references/shells/` 下匹配的文件
7. `references/chrome/` 下匹配的文件
8. `references/blocks/` 下匹配的文件
9. `references/components/ant/` 下匹配的组件（先 summary.md 再 component.html）
10. `design-systems/token-recipes.md`（**合成层 token 配方，生成时直接查表**）
11. `design-systems/` 下其他相关文件
12. `runtime/README.md`
13. `checklists/` 下相关文件

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
