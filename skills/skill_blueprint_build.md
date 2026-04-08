# skill_blueprint_build

## 职责

- 读取 `facts.md`
- 结合业务知识包构建业务蓝图
- 结合业务知识包与设计指南构建体验蓝图

## 不做

- 不臆造缺失业务事实
- 不直接输出页面稿与视觉实现

## 输入

- `task_card.md`
- `workspace/facts.md`
- `knowledge/business/<domain>/`
- `knowledge/guidelines/`
- 蓝图模板

## 使用建议

- 构建体验蓝图时，先读 `knowledge/guidelines/task_type_index.md`
- 再按当前任务风险读 `knowledge/guidelines/trigger_index.md`
- 最后只读取命中的 `principles/*/principles.md`
- 不整包展开全部设计原则

## 输出

- `workspace/business_blueprint.md`
- `workspace/experience_blueprint.md`
- 信息不足时补充开放问题
