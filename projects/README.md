# projects

本目录是项目真相层。

后续新任务与已迁移任务都以 `projects/<project-id>/` 作为唯一正式入口。

## 快速阅读顺序

1. `source/task_card.md`：先看任务边界与输入约束
2. `workspace/facts.md`：再看事实输入是否完整
3. `workspace/business_blueprint.md`：查看业务判断
4. `workspace/experience_blueprint.md`：查看体验转译
5. `workspace/check_report.md`：确认检查结果

## 目录分工

- `source/`：人读输入层（需求、背景、任务卡）
- `workspace/`：人读结果层（facts、业务蓝图、体验蓝图、检查报告）
- `runtime/`：机器运行层（解析产物、上下文包、gate 状态）
- `exports/`：可选交付镜像层（最终文档与检查结果）

## 可读性约定

- 评审时优先阅读 `source/` 与 `workspace/`
- `runtime/` 仅在排障或追溯时进入
- `exports/` 作为交付镜像，不作为日常编辑入口

## 最小执行清单

1. 在 `source/requirement.md` 粘贴原始需求
2. 在 `source/background.md` 补充背景、约束、正式任务分析收敛总结与 GAP
3. 按执行入口依次运行命令
4. 在 `workspace/` 查看三份主产物与检查报告
5. 需要交付镜像时再执行 `archive`

## 常见卡点定位

- 事实阶段不过：先检查 `source/` 是否写入真实输入，而非占位文本
- 业务或体验阶段不过：先看 `runtime/gates/facts_gate_report.md`、`business_gate_report.md`、`experience_gate_report.md`
- 覆盖检查告警：检查 `facts.md` 中的关键业务规则、角色和异常是否在 business 和 experience 中充分承接

## 执行入口

```bash
python -m packages bootstrap <project-id>
python -m packages assemble <project-id>
python -m packages gate-facts <project-id>
python -m packages gate-business <project-id>
python -m packages gate-experience <project-id>
python -m packages validate <project-id>
python -m packages coverage <project-id>
python -m packages archive <project-id>
```
