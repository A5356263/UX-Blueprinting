---
name: xft-design
version: "11.0"
description: Generate enterprise admin web prototypes — minimum reads, one-pass write, zero-iteration output.
triggers:
  - 业务后台页面
  - 后台管理页面
  - 表格页 / 列表页
  - 详情页 / 审批详情页
  - 表单页 / 新建页 / 编辑页
  - 设置页 / 报表页
  - 弹窗 / 抽屉
  - 原型页面

od:
  mode: prototype
  preview:
    type: html
    entry: output/
  outputs:
    primary: output/
  design_system:
    requires: true
    sections:
      - color
      - typography
      - layout
      - components
      - interaction
      - quality_check
---

# XFT Design Skill（v11 — 精简高效版）

你是企业后台页面原型生成 agent。**核心原则：最少文件读取、一次写对、零迭代修复。**

---

# 0. 流程总览（3 步，非 10 步）

```
① 并行读取（链式模式 5-6 文件 / 独立模式 3-4 文件）→ ② 一次写出合规 HTML → ③ check 脚本验证
```

步骤 ① 和 ② 之间不做中间文件读取。步骤 ③ 修复上限 1 轮。

---

# 0.5 链式接入（接在 page-spec 之后）

当当前项目中存在以下产物时，默认按链式模式执行：

- `spark-output/context/page-spec.json`
- `spark-output/page_spec.md`

输入职责：

- `page-spec.json`：页面实体、页面类型、结构骨架、状态与异常范围的主输入
- `page_spec.md`：页面结构、交互规则、文案与状态的补充输入

链式模式下，不再自行猜测页面目标、实体边界和主次流程范围，优先以 page-spec 产物为准。

如果上述两个文件都不存在，再回退到独立原型生成模式。

---

# 1. 按 Page Type 的最小读取集

**永远并行读取以下文件。** 不要串行，不要读无关文件。

## 链式模式先读（2 个）

| 文件 | 用途 |
|------|------|
| `spark-output/context/page-spec.json` | 页面实体、结构骨架、状态与异常范围的主输入 |
| `spark-output/page_spec.md` | 结构、交互、文案与补充说明 |

## 所有页面类型必读（3 个）

| 文件 | 用途 |
|------|------|
| `design-systems/tokens.css` | CSS 变量（颜色/字体/间距/圆角/阴影） |
| `design-systems/components.html` | 组件 CSS class（btn/input/table/modal/tag/checkbox/pagination/alert） |
| `assets/shells/admin-side-shell.html` | 页面骨架 DOM + Runtime JS |

## 按页面类型加读（最多 1 个）

| 页面类型 | 加读 |
|---------|------|
| TablePage / 列表页 | `assets/content-assets/knowledge/table-patterns.html` |
| DetailPage / ApprovalDetailPage | `assets/content-assets/knowledge/doctype.html` |
| 其他（Create/Edit/Settings/Report） | 不加读，按组件 CSS 直接写 |

**禁止读取的文件（与原型生成无关或内容已内化到本 SKILL.md）：**
- 所有 CSV（`content-assets.csv`、`recipe-*.csv`、`field-columns.csv` 等）
- 所有 references/（`intent-model.md`、`page-type-router.md`、`detail-page/` 等）
- `blank-shell.html`（除非用户明确不需要侧导航）
- `scripts/` 下的所有脚本（仅在 check 阶段执行，不在读取阶段）
- 状态模板 / SVG / 图标文件（按需内联，不需要预读）

---

# 2. Page Type 路由（内化，不读文件）

不需要读 `page-type-router.md` 或 CSV。按以下规则直接判定：

| 需求特征 | Page Type |
|---------|-----------|
| 表格 + 筛选 + 分页 + 行操作 | **TablePage** |
| 查看单据详情 + 可能有审批流 | **DetailPage**（无审批流）/ **ApprovalDetailPage**（含审批流） |
| 新建 / 提交申请 | **CreatePage** |
| 回填表单 + 修改保存 | **EditPage** |
| 配置开关 / 参数 | **SettingsPage** |
| 弹窗 / 抽屉为主（承载在已有页面之上） | 对应承载页面类型 + Modal/Drawer overlay |
| 都不确定 | 问用户确认，不猜测 |

---

# 3. 写前自检清单（写入 HTML 时必须同时满足）

**以下规则来自 `check_skill_output.py`，写的时候逐项对齐，不做事后修复。**

## 3.1 文件头部

```
<!DOCTYPE html><!-- XFT_ROUTE Route: ... scope: Full Page overlay_type: modal shell: admin-side-shell --><!-- CONTENT_ASSET_DECISION {"intent":{...},"page_type":"...","shell":"admin-side-shell"} --><html lang="zh-CN">
```

- `XFT_ROUTE` 紧跟 `<!DOCTYPE html>`，同一行，中间无换行
- `XFT_ROUTE` 内必须包含 `scope:`（Full Page 或 Overlay Only）和 `shell:`
- 有 overlay 时必须包含 `overlay_type: modal`（或 drawer）
- `CONTENT_ASSET_DECISION` 紧跟 XFT_ROUTE，内容是合法 JSON（单行）

## 3.2 CSS 注入

- **第一个 `<style>` 块内首行必须是 `/* design-systems/xft/tokens.css — inlined */`**
- 紧接着是 tokens.css 全部 CSS 变量
- 之后是 shell CSS（从 admin-side-shell.html 的 `<style>` 完整复制）
- 再之后是组件 CSS（从 components.html 的 `<style>` 复制组件部分）
- 最后是页面自定义 CSS
- 所有 `<style>` 块中不得出现旧 token 名（`--color-brand-*`、`--color-text-primary` 等）

## 3.3 零违规

| 规则 | 检查方式 |
|------|---------|
| **零 `<link>` 外部样式** | 无 `<link rel="stylesheet">` |
| **零 `style=""` 属性** | 所有样式必须用 class，包括 JS 动态生成的 HTML |
| **零 shell slot 注释残留** | 无 `<!-- PAGE_CONTENT_SLOT -->`、`<!-- OVERLAY_SLOT -->` 等 |
| **零占位文案** | 无「页面主体内容将在这里填充」「字段名称」「页面标题」等 |
| **零旧 token** | 无 `--color-brand-primary`、`--radius-sm` 等 38 个旧变量名 |
| **零 banned class 前缀** | class 名不以 `custom`、`new`、`random` 开头 |
| **`[hidden] { display: none !important; }`** | 必须在全局 reset 中（紧跟 `* { box-sizing }`），防止 CSS `display:flex` 覆盖 hidden 属性 |

## 3.4 结构要素

- Full Page 必须包含：`class="top-nav"`、`class="side-nav"`、`class="xft-tab-header"`、`class="page-content"`、`class="micro-wrapper"`、`class="page-content-container"`
- 必须有 `<div id="overlay-root">` 且其内所有 overlay 元素必须有 `data-overlay` 属性
- 文件名格式：`output/{slug}-{YYYY-MM-DD}-v{N}.html`（小写字母+数字+连字符）

## 3.5 壳子不可变

- top-nav / side-nav / xft-tab-header 的 DOM 结构、CSS、class 名原样保留
- 只改文案（产品名、导航项、用户信息、页签标题）
- 同批次多页面壳子一致

---

# 4. 写入顺序（一次成型）

```
① <!DOCTYPE html> + XFT_ROUTE + CONTENT_ASSET_DECISION（单行）
② <style> tokens.css（首行带注释）
③ <style> shell CSS（从 shell 复制）
④ <style> 组件 CSS（从 components.html 复制需要的部分）
⑤ <style> 页面自定义 CSS（含 [hidden] 规则 + inline-style 替代 class）
⑥ </head><body> shell DOM（从 shell 复制，改文案）
⑦ 页面内容区（基于 table-patterns 规则或自主设计）
⑧ overlay-root 内弹窗/抽屉（带 data-overlay 和 hidden）
⑨ <script> shell Runtime JS（从 shell 复制）
⑩ <script> 页面交互 JS（状态机、事件绑定、Toast）
⑪ </body></html>
```

---

# 5. 交互建模（写 JS 前过一遍）

每个按钮/链接必须有明确行为：
- **打开 Overlay**：`onclick="openXxx()"` → 设置 `el.hidden = false`
- **关闭 Overlay**：`data-overlay-close` 自动绑定 + `onclick="closeXxx()"`
- **危险操作**：必须有确认弹窗
- **Loading 态**：按钮 disabled + spinner
- **空态**：列表为空时展示空态文案
- **Toast**：操作结果反馈，3 秒自动消失

---

# 6. 组件 class 速查（内化，不翻文件）

| 组件 | class |
|------|-------|
| 主按钮 | `btn btn-primary` |
| 默认按钮 | `btn` |
| 文字按钮 | `btn btn-text` |
| 危险按钮 | `btn btn-danger` |
| 小按钮 | `btn btn-sm` |
| 表格 | `table.data-table`（`border-collapse: separate` + 边框 + 圆角，不可覆盖） |
| 输入框 | `input` |
| 复选框 | `label.checkbox > input.checkbox-input + span.checkbox-label` |
| 标签 | `span.status-tag.status-{info\|success\|warning\|error\|neutral}` |
| 分页 | `.pagination > .pagination-info + .pagination-actions > .page-btn` |
| 弹窗 | `.overlay-mask[data-overlay] > .modal > .overlay-header + .overlay-body + .overlay-footer` |
| 提示 | `.alert.alert-{info\|success\|warning\|error}` |

---

# 7. TablePage 硬性规则（内化 table-patterns.html）

- 一级列表页（从侧导航直接进入）**不展示页面标题**
- 操作按钮统一放在筛选区上方一行，从左至右按优先级排列
- 标题区只放标题和说明文字，不放操作按钮
- 表格表头 `#f3f4f6`，文字 `--color-text-neutral-gray50`，14px bold
- 数据行 `--color-text-neutral-gray40`，14px，行高 40px
- 行内操作 ≤ 3 个，超出放入「...」菜单

---

# 8. 禁止事项

0. 禁止修改壳子 DOM/CSS/class
1. 禁止用 div 模拟表格，禁止覆盖 `.data-table` 边框和圆角
2. 禁止硬编码已有 token 可表达的视觉值（颜色/间距/字号/圆角/阴影一律用 var()）
3. 禁止在非审批场景默认展示审批流
4. 禁止生成无行为定义的按钮或无法关闭的 overlay
5. 禁止危险操作没有确认
6. 禁止输出占位文案
7. 禁止读取 CSV / references / scripts（除最终 check 脚本验证一步）

---

# 9. 输出约定

- 单文件 HTML → `output/{slug}-{YYYY-MM-DD}-v{N}.html`
- 顶部 `<!DOCTYPE html><!-- XFT_ROUTE ... --><!-- CONTENT_ASSET_DECISION ... --><html>`
- 可直接在浏览器预览
- 输出后执行 `python3 scripts/check_skill_output.py output/<filename>` 验证；有错 1 轮修完
- 链式模式完成后，额外写入 `spark-output/context/xft-design.json`

`xft-design.json` 最小字段：

```json
{
  "skill": "xft-design",
  "version": "11.0",
  "generated_at": "",
  "source": "page-spec",
  "primary_html": "",
  "html_files": []
}
```
