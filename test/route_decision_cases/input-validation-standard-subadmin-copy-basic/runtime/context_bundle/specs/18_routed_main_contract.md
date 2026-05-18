# Routed Main Contract

`run-routed-main` 是独立的 route-aware 执行入口，用于试运行 `fast / standard / full` 路线编排。

## 1. 入口边界

- `run-routed-main` 不改变 `run-main` 默认行为。
- `run-routed-main` 不删除、不降级 full 主链路。
- `run-routed-main` 只读取 route 产物与外置规则，不在代码中承载路线语义判断。

## 2. 路线选择

- `--route auto` 使用 `runtime/route_decision.json` 的 route。
- `--route fast|standard|full` 仅用于人工指定或测试。
- 人工指定路线低于 route 判断路线时，必须拒绝或提示风险，不得自动降级。
- 执行中允许升级，不建议自动降级。

## 3. 产物要求

fast 必须至少产生：

```text
workspace/facts.md
workspace/business_note.md
workspace/experience_blueprint.md
runtime/routed_main_plan.json
runtime/routed_main_report.json
```

standard 必须至少产生：

```text
workspace/facts.md
workspace/business_blueprint_lite.md
workspace/experience_blueprint.md
runtime/routed_main_plan.json
runtime/routed_main_report.json
```

full 复用当前完整主链路产物。

## 4. 报告要求

`routed_main_plan.json` 必须记录：

- route 来源。
- route 判断结果。
- 实际执行路线。
- 计划步骤。
- 是否存在降级拒绝。

`routed_main_report.json` 必须记录：

- 实际执行步骤。
- 每步退出码。
- 实际生成产物。
- gate / validate / coverage 结果。
- 是否建议正式启用执行分流。

## 5. 禁止事项

- 不得修改 `run-main` 默认步骤。
- 不得让 fast 完全跳过业务依据。
- 不得让 standard 省略规则边界。
- 不得让 full 走轻量路线。
- 不得把路线判断规则写死进 Python。
- 不得修改 knowledge 子系统或正式 projects 作为测试输入。
