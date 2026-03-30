# scripts

本目录放轻量脚本，只处理确定性工作。

## 可运行脚本

- `new_task.py`：新建任务目录并复制模板
- `assemble_context.py`：按 Task Card 收集上下文
- `validate_outputs.py`：检查输出结构与阶段边界
- `coverage_check.py`：检查事实与蓝图的覆盖关系
- `archive_artifacts.py`：归档任务产物

## 使用方式

```bash
python scripts/new_task.py demo-task
python scripts/assemble_context.py demo-task
python scripts/validate_outputs.py demo-task
python scripts/coverage_check.py demo-task
python scripts/archive_artifacts.py demo-task
```
