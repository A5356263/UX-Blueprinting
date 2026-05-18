# Task Card

## Protocol

- Protocol Name: UXB Test Task
- Protocol Version: 1.0
- Task ID: input-validation-standard-subadmin-copy-basic
- Task Name: 子管理员权限复制基础能力
- Domain: permission

## Task Goal

- 支持把一个子管理员的可授权组织和功能权限复制给多个目标用户。

## Task Scenario

- 超级管理员为同岗位人员批量配置子管理员权限。

## Required Inputs

- projects/input-validation-standard-subadmin-copy-basic/source/requirement.md
- projects/input-validation-standard-subadmin-copy-basic/source/background.md

## Required Outputs

- projects/input-validation-standard-subadmin-copy-basic/workspace/facts.md
- projects/input-validation-standard-subadmin-copy-basic/workspace/business_blueprint_lite.md
- projects/input-validation-standard-subadmin-copy-basic/workspace/experience_blueprint.md
- projects/input-validation-standard-subadmin-copy-basic/workspace/check_report.md
- projects/input-validation-standard-subadmin-copy-basic/workspace/check_status.json

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

- facts: projects/input-validation-standard-subadmin-copy-basic/workspace/facts.md
- business_note: projects/input-validation-standard-subadmin-copy-basic/workspace/business_note.md
- business_lite: projects/input-validation-standard-subadmin-copy-basic/workspace/business_blueprint_lite.md
- business: projects/input-validation-standard-subadmin-copy-basic/workspace/business_blueprint.md
- experience: projects/input-validation-standard-subadmin-copy-basic/workspace/experience_blueprint.md

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
