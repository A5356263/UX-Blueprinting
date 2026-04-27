# 业务蓝图构建合同（方案推导与承接升级）

## 目标

定义如何基于 `facts.md` 与知识基线生成 `business_blueprint.md`，并将本阶段定位为：

- 业务判断
- 方案推导
- 方案承接要求

本阶段的核心是形成可评审、可追溯、可承接的业务骨架，而不仅是事实复述。

## 阶段定位

业务蓝图阶段负责：

- 判断需求是否成立与是否值得做
- 推导能力形态（独立能力、并入能力、配置化、规则补充、暂不产品化）
- 输出推荐业务方案（角色、职责、流程闭环、回写与沉淀）
- 输出必须守住的规则与边界
- 输出主要风险与保护策略
- 输出后续方案必须承接的要求
- 显式保留待确认问题

业务蓝图阶段不负责：

- 页面结构设计
- 具体交互细节
- 视觉方案
- 前端或后端实现方案

## 输入前置条件

进入本阶段前至少应具备：

- `projects/<project-id>/workspace/facts.md`
- 任务显式引用的 Wiki / 业务知识

可选但建议读取：

- `projects/<project-id>/workspace/gap_list.md`
- `projects/<project-id>/runtime/context_manifest.json`
- `projects/<project-id>/runtime/task_card_resolved.json`

## 知识使用边界

- 先 facts，再判断。
- 知识用于建立基线，不得替代当前任务事实。
- 对于未确认信息，必须标注为待确认或缺口，不得伪装为既定结论。

## 输出要求

至少输出：

- `projects/<project-id>/workspace/business_blueprint.md`

## `business_blueprint.md` 结构要求

核心区必须包含：

- `## 1. 一句话结论`
- `## 2. 需求是否成立`
- `## 3. 值不值得做`
- `## 4. 应该做成什么能力形态`
- `## 5. 推荐业务方案`
- `## 6. 必须守住的规则和边界`
- `## 7. 主要风险与保护策略`
- `## 8. 方案承接要求`
- `## 9. 待确认问题`

附录区必须包含：

- `## 附录：事实、知识与判断追踪`

## 核心输出质量要求

- 核心区使用业务大白话，避免内部术语堆叠。
- 必须区分：事实、业务判断、方案推导、设计建议、待确认。
- 不得再使用体验设计要注意什么作为核心章节标题，应统一为方案承接要求。
- 方案承接要求需覆盖后续方案必须承接的骨架信息，而非体验专属输入。

## 合格标准

合格的 `business_blueprint.md` 至少满足：

- 能回答需求是否成立、值不值得做、能力形态判断与推荐方案。
- 明确规则边界、风险与保护策略。
- 包含可执行的方案承接要求。
- 保留会影响后续方案的重要待确认问题。
- 可追溯到 facts 与知识基线。

## 进入下一阶段准入条件

仅当以下条件满足时进入体验阶段：

- `business_blueprint.md` 已按新结构生成。
- 方案承接要求已形成并具备可执行性。
- 关键规则、风险、待确认问题已显式暴露。

## 同步约束

本合同更新后，以下模块需保持一致：

- `templates/business_blueprint.template.md`
- `packages/generation/reasoning/business_reasoner.py`
- `packages/generation/reasoning/renderers.py`
- `packages/validate/core.py`
- `specs/10_experience_blueprint_contract.md`
