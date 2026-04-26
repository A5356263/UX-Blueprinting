# Experience Map Composer 合同

## 目标

定义 Experience Map Composer 的职责、输入输出、边界与验收标准，确保体验核心区由 AI 组织，代码仅负责输入包准备、结构校验与渲染。

## 核心职责

Composer 必须负责：

- 读取原始需求：`projects/<project_id>/source/requirement.md`、`projects/<project_id>/source/background.md`
- 读取结构化依据：`facts.md`、`business_blueprint.md`、ExperienceModel 摘要、命中 guidelines/principles 摘要
- 按角色组织主流程、次流程、异常流程
- 生成 `projects/<project_id>/workspace/interaction_map.json`
- 可选生成 `projects/<project_id>/workspace/interaction_map_draft.md` 供人工审阅

Composer 禁止负责：

- 直接输出最终 `experience_blueprint.md` / preview HTML
- 写死具体业务域场景
- 删除追踪信息（事实、判断、原则）

## AI 与代码分工

- AI 负责：交互路径组织与页面文案草案生成。
- 代码负责：输入包生成、schema 校验、渲染 `experience_blueprint.md`、渲染 preview、质量告警。

## 输入要求

至少包含以下输入：

- 原始需求关键片段（页面、流程、状态、异常、文案）
- `facts.md`
- `business_blueprint.md`
- ExperienceModel 摘要（仅作辅助，不是主结构来源）
- guidelines/principles 命中摘要

输入包必须保留上下文连续语义，不得只给编号列表。

## 输出要求

主输出：

- `interaction_map.json`

可选输出：

- `interaction_map_draft.md`

主输出必须是 JSON，不允许仅以自由 Markdown 作为正式结果。

## interaction_map 必含字段

`interaction_map.json` 必须包含并正确组织以下关键字段：

- `role_flows`
- `main`
- `secondary`
- `exception`
- `page_designs`
- `concrete_copy`
- `source_refs`
- `fact_refs`
- `judgment_refs`

并满足：

- 每个节点具备 `node_id`、`title`、`user_action`、`carrier`、`system_feedback`、`next_step`、`copy_strategy`
- 每个节点具备状态与异常表达（`state_refs` 或 `states`；`exception_refs` 或 `exceptions`）
- 每个节点具备追踪引用（`trace_refs` 或等价字段）

## 通用性与边界约束

- 字段设计必须通用，禁止把权限场景硬编码为 schema 固定字段。
- 禁止将具体页面名、角色名、流程名写成全局常量模板。
- 禁止把文档路径、编号痕迹（如 `EV-xxx`、`source_path`）混入核心表达。

## 质量要求

必须通过以下质量要求：

- 至少存在一条 `main` 流程
- `role_flows` 非空，且角色视角可读
- `page_designs` 非空，且页面包含 `concrete_copy`
- 关键节点有追踪信息，不可整体丢失 trace
- 核心表达无机器痕迹（如“从当前输入直接抽取”“未做模板补全”等）

## 与下游对接

- `generation` 阶段消费 `interaction_map.json` 渲染核心区
- `validate` 阶段对 `interaction_map.json` 做结构与内容质量检查
- `preview` 阶段优先展示 `interaction_map.json`，不回写正式蓝图

## 验收标准

通过标准：

- `interaction_map.json` 存在且可解析
- `role_flows`、`main`、`secondary`、`exception`、`page_designs`、`concrete_copy`、`source_refs`、`fact_refs`、`judgment_refs` 可在结构中找到
- 核心区可读且不出现机器痕迹
- 禁止具体场景硬编码规则被满足
