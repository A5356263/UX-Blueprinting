# 交接规则

## facts → business_blueprint

- 业务蓝图只能基于 `facts.md` 与业务知识包推导
- 当事实不足时必须保留开放问题

## facts / business_blueprint → experience_blueprint

- 体验蓝图基于事实、业务蓝图与设计指南
- 体验蓝图不能回写业务规则真源

## 归档

- 最终产物与检查报告归档到 `artifacts/`
- 任务执行过程留在 `tasks/active/<task-id>/`
