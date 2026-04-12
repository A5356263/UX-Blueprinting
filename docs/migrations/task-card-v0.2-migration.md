# Task Card v0.2 Migration

## 升级范围

- `templates/task_card.template.md`
- `specs/01_execution_hub_spec.md`
- `projects/demo-smoke-v1/source/task_card.md`
- `projects/real-self-apply-v1/source/task_card.md`

## 从 v0.1 到 v0.2 的字段变化

- `Protocol Version` 从 `v0.1` 升级为 `v0.2`
- 新增正式协议段：
  - `## Facts Output Requirements`
  - `## Business Output Requirements`
  - `## Experience Output Requirements`
- 每个新增协议段都包含三类可解析字段：
  - `Required Sections`
  - `Recommended ID Prefixes`
  - `Boundary`

## 新增强制字段

- `facts_output_requirements`
- `business_output_requirements`
- `experience_output_requirements`

以上字段写入 `projects/<project-id>/runtime/task_card_resolved.json`，由解析与装配流程消费。

## 批量修改的历史任务

- `demo-smoke-v1`
- `real-self-apply-v1`

## 暂缓升级项目及原因

- 当前无暂缓升级项目
- `projects/` 下活跃项目已全部完成 v0.2 协议迁移

## 对业务语义的影响边界

- 本次修改只升级协议结构与可解析字段
- 不改 `Task Goal` 的业务目标含义
- 不改 `Required Inputs` / `Required Outputs` 的业务产物类型
- 不改 facts/business/experience 业务正文内容

## 如何判断某个 Task Card 已完成 v0.2 升级

- `## Protocol` 内版本为 `v0.2`
- 包含三段新增正式协议段
- 运行 `python -m packages assemble <project-id>` 时，`task_card_resolved.json` 能稳定输出：
  - `facts_output_requirements`
  - `business_output_requirements`
  - `experience_output_requirements`
- `context_manifest.json` 能稳定输出：
  - `facts_extraction_boundary`
  - `business_judgment_boundary`
  - `experience_translation_boundary`
