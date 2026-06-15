# Task Card：员工自助申请权限

## Protocol

- Protocol Name: uxb_task_card
- Protocol Version: 1.0
- Task ID: self-permission-apply
- Task Name: 员工自助申请权限
- Domain: 权限管理

## Required Inputs

- projects/self-permission-apply/source/requirement.md
- projects/self-permission-apply/source/background.md

## Required Outputs

- projects/self-permission-apply/workspace/facts.md
- projects/self-permission-apply/workspace/business_blueprint.md
- projects/self-permission-apply/workspace/experience_blueprint.md

## Constraints

- 不改变现有权限判断决策链（VisibilityGate → FunctionGrant → DataScope → GovernanceState）
- 可申请范围必须是管理员预配置的有限集合
- 员工侧必须做权限概念翻译，不暴露内部来源模型
- 不改变现有权限来源体系（直授、角色、应用可见性、协作可见性）
- 不单独设计审批后台底层能力扩展，仅做业务承接判断

## Templates

此任务不引用模板。

## Checks

self-permission-apply
