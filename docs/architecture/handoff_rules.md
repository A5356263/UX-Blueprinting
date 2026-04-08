# 交接规则

## facts -> business_blueprint

- 业务蓝图只能基于 `facts.md` 与任务引用知识推导
- 当事实不足时必须保留开放问题

## business_blueprint -> experience_blueprint

- 体验蓝图基于事实、业务蓝图与设计原则
- 体验蓝图不能回写业务规则真源

## 项目真相

- 所有正式产物统一留在 `projects/<project-id>/`
- 阶段 gate 与运行时文件统一留在 `runtime/`
