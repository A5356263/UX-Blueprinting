---
name: xft-design
version: "18"
description: 基于稳定 React 资产、页面编排规则与设计系统，生成企业 B 端高保真页面原型。
---

# XFT 设计技能

## 定位

本技能用于生成企业 B 端页面、弹层与关键业务区域的 React 原型。

它不再走这些旧路径：

- HTML 模板复制
- 参考块改写
- 旧 HTML runtime 拼装

它只走一条正式主链：

```txt
理解需求
-> 判断页型
-> 判断区域职责
-> 选择 shell
-> 选择 composition
-> 选择 primitive
-> 按规则编排页面
-> 用 token 配方收口
-> 用统一 checklist 自检
```

## 正式物料层

正式物料只包括：

```txt
rules/
design-systems/
react-system/
checklists/review-checklist.md
vendor/ant6-subset/
```

旧 HTML 历史资产已移出 skill，归档到：

`docs/archive/xft-design/legacy-html/`

这些归档文件不得回到正式起稿链路。

## 读取顺序

生成前按以下顺序读取：

1. `rules/page-structure.md`
2. `rules/module-responsibilities.md`
3. `rules/asset-selection.md`
4. `rules/composition-rules.md`
5. `rules/react-asset-boundaries.md`
6. `react-system/registry/shell-registry.ts`
7. `react-system/registry/composition-registry.ts`
8. `react-system/registry/component-registry.ts`
9. `react-system/registry/props-contract.md`
10. 目标 `shell` / `composition` / `primitive` 源码
11. `design-systems/component-recipes.md`
12. `design-systems/token-recipes.md`
13. `checklists/review-checklist.md`

只有正式层无法回答问题时，才允许补读：

- `references/reference-notes.md`

## 输入

本技能读取：

- 用户需求 / `Design Spec`
- `rules/`
- `design-systems/`
- `react-system/`
- `vendor/ant6-subset/`
- `assets/`

## 输出

默认输出为：

- React 页面原型
- 受控的 `shell / composition / primitive` 组合结果
- 遵循 token 配方的样式收口

## 工作流

### Step 0: 确认对象

先明确本次要生成的是：

- 整页
- 弹层
- 局部业务区域

只生成被明确要求设计的对象。

### Step 1: 判断页型

从 `rules/page-structure.md` 判断当前对象属于：

- 列表管理页
- 表单页
- 详情页
- 弹层任务页

并确定页面壳类型。

### Step 2: 判断区域职责

从 `rules/module-responsibilities.md` 判断当前页面需要哪些区域：

- Header
- Filter
- Action
- Primary Content
- Detail Section
- Footer Actions

这一层只做职责判断，不做实现。

### Step 3: 选择正式资产

读取：

- `rules/asset-selection.md`
- `rules/composition-rules.md`
- `rules/react-asset-boundaries.md`
- `react-system/registry/*.ts`

完成：

1. shell 选择
2. composition 选择
3. primitive 补充选择

规则：

- 优先用 composition
- composition 不足时才下探 primitive
- 页面层禁止直接 `import antd`
- 禁止绕过 registry 临时造第二套高频资产

### Step 4: 编排页面

页面编排遵守：

- 页面结构来自页型规则
- 区域职责来自模块规则
- 资产选择来自 registry
- 视觉收口来自 token 配方

输出应是 React 组合结果，不是 HTML 代码块拼装。

### Step 5: 设计系统收口

读取：

- `design-systems/component-recipes.md`
- `design-systems/token-recipes.md`

检查：

- 是否绕过 token
- 是否错误使用 Surface / Wrapper
- 是否出现同层多个主按钮竞争
- 是否出现硬编码颜色、间距、圆角、阴影

### Step 6: 最终自检

读取：

- `checklists/review-checklist.md`

重点检查：

- 是否直接依赖底层库
- 是否越过 composition 边界
- 是否偏离页型主线
- 是否造出 token 体系外样式
- 是否破坏模块职责

## 约束

- 不要重新引入 HTML 复制改写主线
- 不要让历史归档资产回到正式链路
- 不要在页面中直接 `import antd`
- 不要绕过 registry 长出第二套常用资产
- 不要为了灵活性破坏页型主线与模块职责
- 不要硬编码颜色、间距、圆角、阴影

## 第一阶段闭环

第一阶段正式闭环页型：

```txt
列表管理页
```

最低闭环资产：

- `admin-side-shell`
- `page-header`
- `filter-bar`
- `action-bar`
- `data-table`
- `status-tag`
- `panel`

## 成功标准

输出结果至少满足：

- 结构来自页型规则
- 区域职责清晰
- 正式资产优先被使用
- 视觉由 token 与 component recipes 收口
- 不依赖整段 HTML 参考资产起稿
