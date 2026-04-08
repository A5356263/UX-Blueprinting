# 输出合同

## 目标

定义项目主链路产物与检查产物的最小结构合同。

## 正式输出位置

执行中产物：

- `projects/<project-id>/workspace/facts.md`
- `projects/<project-id>/workspace/business_blueprint.md`
- `projects/<project-id>/workspace/experience_blueprint.md`
- `projects/<project-id>/workspace/gap_list.md`
- `projects/<project-id>/workspace/check_report.md`
- `projects/<project-id>/workspace/check_status.json`

归档产物：

- `projects/<project-id>/exports/final/`
- `projects/<project-id>/exports/checks/`

## facts.md

必须包含：

- `任务目标`
- `业务事实清单`
- `已知约束`
- `输入来源`
- `开放问题`

## business_blueprint.md

必须包含：

- 业务判断
- 规则与约束
- 依赖与风险
- 开放问题

## experience_blueprint.md

必须包含：

- 体验目标
- 体验要求
- 原则引用
- 风险与保护
- 开放问题

## check_report.md

必须包含：

- `Summary`
- `Output Status`
- `Blockers`
- `Warnings`
- `Infos`
- `Machine Status`

## check_status.json

必须包含：

- `task_id`
- `status`
- `has_blocker`
- `blocker_count`
- `warning_count`
- `info_count`
- `completed_outputs`
- `missing_outputs`

## 失败条件

- 任一必需输出缺失
- 任一输出未落在规定位置
- 检查双产物缺失
