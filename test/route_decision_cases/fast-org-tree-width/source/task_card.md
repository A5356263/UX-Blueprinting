# Task Card

## Protocol

- Protocol Name: UXB Test Task
- Protocol Version: 1.0
- Task ID: fast-org-tree-width
- Task Name: 组织树宽度拖动
- Domain: test

## Task Goal

- 优化组织树宽度展示，让长部门名称更容易查看。

## Task Scenario

- 用户在组织架构页面查看层级较深的部门名称。

## Required Inputs

- projects/fast-org-tree-width/source/requirement.md
- projects/fast-org-tree-width/source/background.md

## Required Outputs

- projects/fast-org-tree-width/workspace/facts.md
- projects/fast-org-tree-width/workspace/business_note.md
- projects/fast-org-tree-width/workspace/experience_blueprint.md
- projects/fast-org-tree-width/workspace/check_report.md
- projects/fast-org-tree-width/workspace/check_status.json

## Constraints

- 不新增组织、成员、角色或权限能力。
- 不改变数据范围、审批或状态机。

## Knowledge

## Wiki

## Design Guidelines

## Templates

- templates/facts.template.md
- templates/business_note.template.md
- templates/experience_blueprint.template.md

## Checks

- specs/16_business_note_contract.md
- specs/10_experience_blueprint_contract.md
- specs/18_routed_main_contract.md

## Result Locations

- facts: projects/fast-org-tree-width/workspace/facts.md
- business_note: projects/fast-org-tree-width/workspace/business_note.md
- experience: projects/fast-org-tree-width/workspace/experience_blueprint.md

## Completion Criteria

- business_note 说明不影响核心业务规则。
- experience 承接宽度调整、边界宽度和刷新恢复。

## Facts Output Requirements

### Required Sections

- 任务概述

### Boundary

- 不输出体验方案。

## Business Output Requirements

### Required Sections

- 业务依据摘要

### Boundary

- 不输出完整业务蓝图。

## Experience Output Requirements

### Required Sections

- 体验总览

### Boundary

- 不输出前端实现。
