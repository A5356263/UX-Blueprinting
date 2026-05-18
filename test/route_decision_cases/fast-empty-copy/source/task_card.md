# Task Card

## Protocol

- Protocol Name: UXB Test Task
- Protocol Version: 1.0
- Task ID: fast-empty-copy
- Task Name: 空状态文案微调
- Domain: test

## Task Goal

- 优化空状态提示文案，让用户知道当前没有可展示内容。

## Task Scenario

- 用户进入列表页时，当前筛选条件下没有数据。

## Required Inputs

- projects/fast-empty-copy/source/requirement.md
- projects/fast-empty-copy/source/background.md

## Required Outputs

- projects/fast-empty-copy/workspace/facts.md
- projects/fast-empty-copy/workspace/business_note.md
- projects/fast-empty-copy/workspace/experience_blueprint.md
- projects/fast-empty-copy/workspace/check_report.md
- projects/fast-empty-copy/workspace/check_status.json

## Constraints

- 不新增权限、审批、数据范围或状态机规则。
- 只处理当前空状态提示。

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

- facts: projects/fast-empty-copy/workspace/facts.md
- business_note: projects/fast-empty-copy/workspace/business_note.md
- experience: projects/fast-empty-copy/workspace/experience_blueprint.md

## Completion Criteria

- business_note 说明不影响核心业务规则。
- experience 承接空状态文案与反馈。

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

- 交互流程总览

### Boundary

- 不输出前端实现。
