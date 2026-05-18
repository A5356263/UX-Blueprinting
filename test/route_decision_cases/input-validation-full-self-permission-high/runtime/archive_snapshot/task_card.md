# Task Card

## Protocol

- Protocol Name: UXB Test Task
- Protocol Version: 1.0
- Task ID: input-validation-full-self-permission-high
- Task Name: 员工自助权限申请完整能力
- Domain: permission

## Task Goal

- 设计员工自助申请权限的完整业务和体验闭环。

## Task Scenario

- 员工选择可申请权限并提交，审批人处理后权限自动生效或拒绝。

## Required Inputs

- projects/input-validation-full-self-permission-high/source/requirement.md
- projects/input-validation-full-self-permission-high/source/background.md

## Required Outputs

- projects/input-validation-full-self-permission-high/workspace/facts.md
- projects/input-validation-full-self-permission-high/workspace/business_blueprint.md
- projects/input-validation-full-self-permission-high/workspace/experience_blueprint.md
- projects/input-validation-full-self-permission-high/workspace/gap_list.md
- projects/input-validation-full-self-permission-high/workspace/check_report.md
- projects/input-validation-full-self-permission-high/workspace/check_status.json

## Constraints

- 只依据 source 中的真实需求片段和背景，不引入无来源的新业务范围。
- 按 route_decision 的实际路线输出对应正式产物，不能用聊天回复替代正式文档。

## Knowledge

## Wiki

## Design Guidelines

## Templates

- templates/facts.template.md
- templates/business_note.template.md
- templates/business_blueprint_lite.template.md
- templates/business_blueprint.template.md
- templates/experience_blueprint.template.md

## Checks

- specs/16_business_note_contract.md
- specs/17_business_blueprint_lite_contract.md
- specs/09_business_blueprint_contract.md
- specs/10_experience_blueprint_contract.md
- specs/18_routed_main_contract.md

## Result Locations

- facts: projects/input-validation-full-self-permission-high/workspace/facts.md
- business_note: projects/input-validation-full-self-permission-high/workspace/business_note.md
- business_lite: projects/input-validation-full-self-permission-high/workspace/business_blueprint_lite.md
- business: projects/input-validation-full-self-permission-high/workspace/business_blueprint.md
- experience: projects/input-validation-full-self-permission-high/workspace/experience_blueprint.md

## Completion Criteria

- routed-main 能按 auto 路线完成到最终检查产物。
- 产物必须承接当前需求正文中的关键边界，不外扩判断维度。

## Facts Output Requirements

### Required Sections

- 任务概述

### Boundary

- 不输出体验方案。

## Business Output Requirements

### Required Sections

- 路线对应业务产物

### Boundary

- 不越过 route_decision 的业务深度。

## Experience Output Requirements

### Required Sections

- 交互流程总览

### Boundary

- 不输出前端实现方案。
