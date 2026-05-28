# Task Card

## Protocol

- Protocol Name: Cross-AI Task Card
- Protocol Version: v0.3
- Task ID: permission-query
- Task Name: 权限查询
- Domain: 管理后台

## Task Goal

- 补齐权限统一查询能力，支持管理员从"按人"、"按角色"、"按权限项"三个维度查询权限归属关系
- 本次输出主要服务于产品方案评审和体验设计评审

## Task Scenario

- 在现有权限管理能力基础上，新增多维权限查询视图，不改变底层授权、角色、规则等业务骨架
- 这是新建任务，属于既有能力扩展
- 本次任务覆盖 business（轻量业务判断）和 experience（体验蓝图）两层

## Required Inputs

- projects/permission-query/source/requirement.md
- projects/permission-query/source/background.md

## Required Outputs

- projects/permission-query/workspace/facts.md
- projects/permission-query/workspace/business_blueprint_lite.md
- projects/permission-query/workspace/experience_blueprint.md
- projects/permission-query/workspace/gap_list.md
- projects/permission-query/workspace/check_report.md
- projects/permission-query/workspace/check_status.json

## Read Order

1. 先读本文档
2. 再读 `Required Inputs`
3. 生成 facts.md
4. 生成 business_blueprint_lite.md
5. 生成 experience_blueprint.md
6. 运行 validate / coverage / archive / preview

## Constraints

- 不得臆造业务事实
- 信息不足处保留 `[GAP]`
- 正式产出必须写入 `workspace/`
- 不得用聊天回复替代正式文档产物
- facts 阶段不得把引用知识提升为当前任务已确认事实
- business 阶段不得输出 UI 方案或实现方案
- experience 阶段不得输出高保真视觉稿或研发实现细节
- `runtime/uxb_route_decision.json` 是执行判断与知识选择唯一来源
- `task_card.md` 不能替代 UXB 做复杂度判断、知识选择或执行深度判断

## Templates

- templates/facts.template.md
- templates/business_blueprint.template.md
- templates/experience_blueprint.template.md
- templates/gap_list.template.md
- templates/check_report.template.md

## Checks

- specs/06_check_contract.md
- specs/08_fact_extraction_contract.md
- specs/09_business_blueprint_contract.md
- specs/10_experience_blueprint_contract.md

## Result Locations

- 执行中结果: projects/permission-query/workspace/
- 归档结果: projects/permission-query/exports/final/

## Completion Criteria

- 必需输出文件全部存在
- `check_report.md` 已生成
- 无 blocker

## Facts Output Requirements

参考 `specs/08_fact_extraction_contract.md` 和 `templates/facts.template.md`

## Business Output Requirements

本次采用轻量业务蓝图（business_blueprint_lite），聚焦业务边界、角色和查询路径收敛，不做完整业务模型展开。

## Experience Output Requirements

参考 `specs/10_experience_blueprint_contract.md` 和 `templates/experience_blueprint.template.md`

## Notes

- UXB 应在执行前写好 `projects/permission-query/runtime/uxb_route_decision.json`
- 本次为中等复杂度、既有能力扩展，不走完整业务蓝图
