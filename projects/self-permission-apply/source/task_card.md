# Task Card

## Protocol

- Protocol Name: uxb_routed_main
- Protocol Version: 5.0
- Task ID: self-permission-apply
- Task Name: 员工自助申请权限
- Domain: 权限管理

## Required Inputs

- projects/self-permission-apply/source/requirement.md
- projects/self-permission-apply/source/background.md
- projects/self-permission-apply/runtime/uxb_route_decision.json

## Required Outputs

- projects/self-permission-apply/workspace/facts.md
- projects/self-permission-apply/workspace/business_blueprint_lite.md
- projects/self-permission-apply/workspace/experience_blueprint.md

## Constraints

- 来源模型扩展（APPLICATION_APPROVAL）需要显式确认
- 审批人不可用的兜底策略标注为 GAP，不阻塞
- 数据权限全量是否允许超管覆盖标记为待定项
- 不与双管理员互审模式、权限变更审批模式同时启用

## Templates

## Checks
