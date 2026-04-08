# Skill 输入输出说明

本文件用于解释当前平台优化层中的 skill 分工。  
它不是正式规则真源，也不构成跨 AI 主线依赖。

## skill_requirements_refine

- 输入：原始需求、Task Card、必要背景
- 输出：`facts.md`
- 边界：不做业务规则与体验方案判断

## skill_blueprint_build

- 输入：`facts.md`、Task Card、业务知识、设计指南
- 输出：`business_blueprint.md`、`experience_blueprint.md`
- 边界：信息不足时保留开放问题，不擅自补造事实

## 说明

如果没有 skill，项目主线仍然应能依赖 `specs/`、`packages/`、`projects/`、`knowledge/` 与 `templates/` 执行。
