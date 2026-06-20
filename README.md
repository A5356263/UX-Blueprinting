# 体验蓝图构建思路

这是一个轻量的 prompt 驱动型体验设计工作站。

项目的正式主链路收敛为两个 Skill：

- `uxb`：负责需求分析、两次硬停对齐、输出正式需求定案文档
- `experience-blueprint`：负责读取 UXB 产出并展开为交互设计方案

## 当前架构

主链路由以下部分组成：

- `.claude/skills/uxb/`
- `.claude/skills/experience-blueprint/`
- `_shared/`
- `knowledge/`
- `input/`
- `spark-output/`

其中：

- `_shared/skill-graph.json` 定义 Skill 流转关系
- `_shared/context-schema.md` 定义上下文 JSON 字段
- `_shared/handoff.md` 定义交接话术模板

## 目录结构

- `input/`：用户输入层
- `knowledge/`：业务知识与设计准则
- `.claude/skills/`：Skill 定义
- `_shared/`：跨 Skill 协调层
- `spark-output/`：正式输出层
- `packages/experience_preview/`：HTML 预览参考实现
- `docs/`：文档与讨论记录

## 使用方式

不再通过 CLI 命令、工程主线或 `python -m packages` 运行正式主链路。

正式使用方式是：

1. 触发 `uxb`
2. 完成 Step 1 与 Step 2 分析对齐
3. 生成 `spark-output/uxb_output.md` 与 `spark-output/context/uxb.json`
4. 触发 `experience-blueprint`
5. 生成体验蓝图文档、context JSON 和 HTML 预览

## 说明

- 正式主链路不再依赖 `specs/`
- 正式主链路不再依赖 `templates/`
- 正式主链路不再依赖 `gate / validate / coverage`
- 仓库中保留的 `packages/experience_preview/` 仅作为预览实现参考
