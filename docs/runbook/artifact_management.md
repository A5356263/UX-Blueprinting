# 产物管理说明

当前项目不再使用根级 `tasks/`、`artifacts/` 或顶层 `checks/`。

正式产物统一位于：

- `projects/<project-id>/source/`
- `projects/<project-id>/workspace/`
- `projects/<project-id>/runtime/`
- `projects/<project-id>/exports/`

其中：

- `source/`：需求、背景、任务卡
- `workspace/`：人主要查看的产物
- `runtime/`：机器状态、解析结果、阶段 gate
- `exports/`：可选交付镜像
