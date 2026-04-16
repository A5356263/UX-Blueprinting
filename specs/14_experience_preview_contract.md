# 体验蓝图预览层合同

## 目标

定义体验蓝图预览层 V2 的正式落地方式，使其在不改变主链路定位的前提下，从“章节顺序渲染器”升级为“页面中心 + 角色流程中心”的体验蓝图还原器。

## 定位

- 预览层是正式体验蓝图的只读派生扩展层
- 预览层不属于主链路正式产物
- 预览层不参与正式 Gate / Validate
- 预览层不回写正式体验蓝图
- 预览层不新增业务语义
- 预览层在主链路完成后执行

## 输入合同

预览层标准输入为以下任一文件：

1. `projects/<project-id>/exports/final/experience_blueprint.md`
2. `projects/<project-id>/workspace/experience_blueprint.md`

优先读取 `exports/final/experience_blueprint.md`；仅当归档版不存在时，才允许降级读取 `workspace/experience_blueprint.md`。

## 输出合同

运行时产物必须继续落在：

```text
projects/<project-id>/runtime/preview/
```

最小输出集合保持不变：

```text
projects/<project-id>/runtime/preview/index.html
projects/<project-id>/runtime/preview/assets/style.css
projects/<project-id>/runtime/preview/preview_model.json
projects/<project-id>/runtime/preview/preview_runtime.json
projects/<project-id>/runtime/preview/preview_build_log.md
```

## V2 中间模型合同

V2 预览模型必须升级为：

```text
preview_document_v2
- project_id
- meta
- global_flow
- page_views[]
- global_context
- unresolved_items[]
- source_refs[]
```

### global_flow

`global_flow` 至少包含：

```text
global_flow
- lanes[]
- chains[]
- nodes[]
- edges[]
- dependencies[]
- blockers[]
```

约束：

- `lanes[]` 必须按角色分泳道
- `chains[]` 必须按 `flow_id` 或等价任务流分链路
- `nodes[]` 至少保留 `node_id / name / type / role / chain_id / goal`
- `edges[]` 至少保留 `from / to / path_type / label / role / chain_id`
- `dependencies[]` 用于表达链路之间依赖
- `blockers[]` 用于表达流程级阻断

### page_views

`page_views[]` 中每个页面必须至少包含：

```text
page_view
- page_id
- view_name
- view_type
- roles[]
- summary
- entry
- exit
- upstream_links[]
- downstream_links[]
- sketch_blocks[]
- key_understanding[]
- states[]
- copy_items[]
- risks[]
- blockers[]
- principles[]
- design_patterns[]
- trace_items[]
- open_items[]
- gap_items[]
- source_refs[]
```

约束：

- `page_id` 是页面聚合主键
- 页面信息优先按 `page_id` 精确归属
- 仅在无法稳定命中 `page_id` 时，才允许降级到页面名 / 别名 / flow context
- 不得把无法稳定归属的信息强塞进任意页面

其中 `sketch_blocks[]` 不再只是线性块列表，至少应支持以下最小结构字段：

```text
sketch_block
- block_id
- label
- summary
- zone
- layout_kind
- position_hint
- children[]
```

推荐值：

- `zone`: `header / intro / filter / action / menu / tab / step / main / side / footer / alert / info`
- `layout_kind`: `stack / split_lr / main_side / footer_actions / header_with_actions / single`
- `position_hint`: `top / left / right / center / bottom / inline`

### global_context

V2 禁止再以单一 `global_notes[]` 作为全局兜底池，必须拆分为：

```text
global_context
- principles[]
- dependencies[]
- risks[]
- open_questions[]
- gaps[]
- notes[]
```

约束：

- `principles[]` 只放全局原则
- `dependencies[]` 只放跨页面或跨链路依赖
- `risks[]` 只放无法稳定归属到单页面的全局风险
- `open_questions[]` 只放全局开放问题
- `gaps[]` 只放全局缺口
- `notes[]` 仅作为最后兜底项

## 聚合规则

- 必须先做全文语义聚合，再做展示渲染
- 禁止按 Markdown 章节顺序直接渲染页面卡
- 必须扫描整个体验蓝图，不得只扫少数几个章节
- 聚合时至少覆盖信息架构、任务流、页面清单、关键页面蓝图、区块布局、信息优先级、状态矩阵、文案合同、风险、开放问题、体验追踪等来源

## 渲染规则

每张页面卡必须稳定输出以下固定顺序：

1. 页面摘要
2. 线框草图
3. 关键理解
4. 状态
5. 文案
6. 风险与阻断
7. 原则、设计模式与追踪
8. 开放问题 / 缺口
9. 来源说明（可折叠）

额外约束：

- 当 `page_id == view_name` 时，不得重复输出页面 ID
- 页面摘要不得重复标题语义
- 自动降级提示不得淹没蓝图原始内容
- 默认页面不再直接展示整段 `preview_model.json`
- 全局区块必须拆分为：全局流程总览、全局原则、全局依赖 / 前提、全局风险、全局开放问题、全局缺口、待人工确认
- 页面草图应优先表达 left / right / main / side / footer / step 等结构关系
- 若无法稳定识别结构关系，可安全降级为 `stack`
- preview 不得伪造蓝图中不存在的 left / right / main / side 关系

## 执行入口

当前仓库中的正式执行入口保持不变：

```bash
python -m packages preview <project-id> [--host 127.0.0.1] [--port 0]
```

补充说明：

- `--port 0` 允许系统自动分配本地可用端口
- 使用 `--no-serve` 时，只生成静态文件，不启动本地服务
- 默认应同时完成构建与本地服务启动

## 地址输出合同

当预览服务已可访问时，聊天窗口或命令输出必须明确给出完整 URL：

```text
本地预览地址：
http://127.0.0.1:<port>/
```

不得仅输出路径、目录、端口号或“服务已启动”。

## 失败隔离

若预览层失败，必须满足：

- 主链路正式产物不受影响
- 失败仅归因于预览层
- 不得把预览层失败表述成主链路整体失败
- 不得输出不可访问的伪地址

## 代码落位

仓库级能力文件应落在：

```text
packages/experience_preview/
```

当前正式落位：

```text
packages/experience_preview/
  __init__.py
  build_preview_model.py
  render_html.py
  serve_preview.py
  write_preview_runtime.py
```

## 运行原则

- 先主链路完成，再执行预览层
- 预览层默认覆盖更新 `runtime/preview/`
- 原始开放问题与缺口优先于自动降级提示
- 无法稳定归属的信息优先进入 `global_context`，仍无法归属再进入 `unresolved_items[]`
- 不得伪造页面内容、流程关系或文案内容
