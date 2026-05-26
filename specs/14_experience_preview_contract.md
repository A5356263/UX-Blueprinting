# 蓝图预览层合同

## 目标

定义 Experience Preview 的正式落地方式，使其在不改变主链正式产物定位的前提下，提供统一、只读、可本地预览的业务蓝图 / 体验蓝图展示层。

## 定位

- 预览层是正式蓝图的只读派生层。
- 预览层不参与正式 gate / validate / coverage 判定。
- 预览层不回写 `business_blueprint.md` 或 `experience_blueprint.md`。
- 预览层不新增业务语义，只做结构化抽取与展示增强。

## 输入合同

体验蓝图读取优先级：

1. `projects/<project-id>/exports/final/experience_blueprint.md`
2. `projects/<project-id>/workspace/experience_blueprint.md`

业务蓝图读取优先级：

1. `projects/<project-id>/exports/final/business_blueprint.md`
2. `projects/<project-id>/workspace/business_blueprint.md`
3. `projects/<project-id>/workspace/business_blueprint_lite.md`
4. `projects/<project-id>/workspace/business_note.md`

约束：

- 预览层必须以 `experience_blueprint.md` 作为必需输入。
- 仅当归档版不存在时，才降级读取 `workspace/*.md`。

## 输出合同

运行产物目录：

```text
projects/<project-id>/runtime/preview/
```

最小输出集合：

```text
projects/<project-id>/runtime/preview/index.html
projects/<project-id>/runtime/preview/preview_model.json
projects/<project-id>/runtime/preview/preview_runtime.json
projects/<project-id>/runtime/preview/preview_build_log.md
```

约束：

- `index.html` 必须内联样式，不依赖 `assets/style.css` 或其他样式文件。
- 预览层默认覆盖更新 `runtime/preview/`。

## Preview Model 合同

当前正式中间模型为：

```text
preview_document_v3
- project_id
- meta
- business
- experience
```

### meta

```text
meta
- title
- version
- source_business
- source_experience
```

### business

```text
business
- title
- sections[]
```

其中每个 `sections[]` 至少包含：

```text
section
- heading
- body_html
```

### experience

```text
experience
- title
- sections[]
- journey
- interaction_summary
- detail_flows
- pages[]
- states[]
- state_rows[]
```

#### experience.sections[]

与 `business.sections[]` 一致，至少包含：

```text
section
- heading
- body_html
```

#### journey

```text
journey
- heading
- paths[]
- gaps[]
```

其中：

```text
journey_path
- role
- nodes[]
```

约束：

- `journey` 来源于 `## 1. 旅程图` 的正式 Markdown 路径列表。
- 每条路径使用 `角色：节点 → 节点 → 节点` 表达。
- 节点只承载旅程短节点。
- `gaps[]` 来源于 `### 旅程缺口` 的普通列表。
- 原始旅程路径列表在 section 正文 HTML 中应被移除，避免重复展示。

#### interaction_summary

```text
interaction_summary
- heading
- rows[]
```

其中：

```text
summary_row
- role
- steps[]
```

约束：

- `interaction_summary` 来源于 `## 2. 交互流程总览` 中的“涉及角色”路径块。
- 仅抽取 `角色：步骤 -> 步骤 -> 步骤` 这种轻量路径表达。
- 被抽取出的角色路径不应在 section 正文 HTML 中重复保留。

#### detail_flows

```text
detail_flows
- <section_heading>: flow_group[]
```

其中：

```text
flow_group
- name
- nodes[] | body_html
```

约束：

- `detail_flows` 仅来源于 `## 3. 主交互流程` 与 `## 4. 次交互流程`。
- 它保留结构化信息，供后续分析或扩展使用。
- 当前 HTML 预览不对 `detail_flows` 做流程图式可视化。

#### pages / states / state_rows

```text
pages[]
- name
- desc_html

states[]
- <state_text>

state_rows[]
- <table_row_map>
```

约束：

- `pages[]` 来源于 `## 6. 页面 / 弹窗 / 抽屉设计` 的三级子块。
- `state_rows[]` 来源于 `## 7. 状态与反馈文案` 的表格。
- `states[]` 来源于状态章节中的普通列表项。

## 渲染规则

统一 `index.html` 顶部必须提供以下 Tab：

1. Business Blueprint
2. Experience Blueprint
3. 承接对照
4. Warnings / Gaps

约束：

- 左侧锚点必须跟随当前 Tab 切换，不得同时展示业务与体验两套锚点。
- 左侧标题区保持紧凑，不放过高的装饰性占位。

### Experience Tab

预览层必须支持：

- `## 1. 旅程图` 的 CSS 视觉版
- `### 旅程缺口` 的普通文本区
- `## 2. 交互流程总览` 的轻量路径可视化

预览层不得：

- 重复展示原始旅程 Markdown 路径列表
- 对 `## 3. 主交互流程` 与 `## 4. 次交互流程` 插入 flow visual
- 按参考图复刻复杂泳道图、连线系统或场景化样式

### Business / 承接 / Warnings

- Business Tab 优先展示一句话结论、推荐业务方案、规则边界、风险保护、方案承接要求、待确认问题。
- 承接对照 Tab 以“业务承接要求 -> 体验承接状态”方式展示。
- Warnings Tab 聚合 unresolved、风险、开放问题、缺口与承接不足项。

## 执行入口

```bash
python -m packages preview <project-id> [--host 127.0.0.1] [--port 0]
```

补充说明：

- `--port 0` 允许系统自动分配可用端口。
- `--no-serve` 只生成静态文件，不启动本地服务。

## 地址输出合同

当本地服务可访问时，必须输出完整 URL：

```text
本地预览地址：http://127.0.0.1:<port>/
```

## 失败隔离

若预览层失败，必须满足：

- 主链正式产物不受影响
- 失败只归因于预览层
- 不得把预览层失败表述为主链整体失败

## 代码落位

```text
packages/experience_preview/
  __init__.py
  build_preview_model.py
  render_html.py
  serve_preview.py
  write_preview_runtime.py
```

## 运行原则

- 先完成主链，再执行预览层。
- 只要主链成功且存在可读的 `experience_blueprint.md`，即可后置触发预览。
- 不得伪造页面内容、流程关系或文案内容。
