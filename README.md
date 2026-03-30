# 业务蓝图 / 体验蓝图项目 v1

本项目是一个轻量工程化仓库。

它的目标不是搭建重型 Agent 平台，而是用固定结构支持以下工作：
- 需求事实提炼
- 业务蓝图构建
- 体验蓝图构建

本项目由以下部分共同组成：
- 独立 skill 文件，约束 AI Code 的执行方式
- 业务知识包与设计指南，提供判断依据
- 固定模板与检查清单，稳定输出结构
- 轻量脚本，负责装配、校验与归档

## 当前结构

- `docs/`：项目说明、SDD 规格、运行手册
- `skills/`：执行阶段 skill
- `knowledge/`：业务知识包与设计指南
- `templates/`：固定输出模板
- `checks/`：检查清单与覆盖规则
- `scripts/`：轻量脚本
- `tasks/`：任务工作区
- `artifacts/`：正式归档产物

## 快速开始

1. 创建新任务
2. 在 `tasks/active/<task-id>/inputs/` 放入需求材料
3. 按 `skills/` 与 `knowledge/` 执行事实提炼和蓝图构建
4. 运行校验脚本
5. 归档到 `artifacts/`

## 最小命令

```bash
python scripts/new_task.py demo-task
python scripts/assemble_context.py demo-task
python scripts/validate_outputs.py demo-task
python scripts/coverage_check.py demo-task
python scripts/archive_artifacts.py demo-task
```

## 说明

- 当前阶段不做 Web UI
- 当前阶段不做重型 runtime
- 当前阶段不做 monorepo 与复杂平台拆分
- 设计原则正文已并入 `knowledge/guidelines/`，不在本次工程搭建中改写
