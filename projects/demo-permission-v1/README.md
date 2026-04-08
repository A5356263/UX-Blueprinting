# demo-permission-v1

本项目用于演示权限域任务在 `projects/` 主线下的完整执行。

## 先看哪里

1. `source/task_card.md`
2. `workspace/facts.md`
3. `workspace/business_blueprint.md`
4. `workspace/experience_blueprint.md`
5. `workspace/check_report.md`

## 目录说明

- `source/`：任务输入
- `workspace/`：任务主产物与阶段报告
- `runtime/`：机器状态与上下文包
- `exports/`：交付镜像

## 复跑命令

```bash
python -m packages assemble demo-permission-v1
python -m packages gate-facts demo-permission-v1
python -m packages gate-business demo-permission-v1
python -m packages gate-experience demo-permission-v1
python -m packages validate demo-permission-v1
python -m packages coverage demo-permission-v1
python -m packages archive demo-permission-v1
```
