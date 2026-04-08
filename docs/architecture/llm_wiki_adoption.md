# LLM Wiki 落地方案

## 目标

在不改变主链路的前提下，为仓库补一层长期可维护的知识编译层。

当前主链路仍然是：

1. 需求事实提炼
2. 业务蓝图构建
3. 体验蓝图构建
4. 检查与可选归档

## 在当前仓库中的定位

- 原始输入位于 `projects/<project-id>/source/`
- Wiki 位于 `knowledge/wiki/`
- 任务上下文快照位于 `projects/<project-id>/runtime/context_bundle/`
- 任务产物位于 `projects/<project-id>/workspace/`
- 可选交付镜像位于 `projects/<project-id>/exports/`

Wiki 不替代 `facts.md`、`business_blueprint.md`、`experience_blueprint.md`，而是作为这些产物的长期上游知识层。
