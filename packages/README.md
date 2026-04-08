# packages

本目录是本项目后续的执行中枢层。

本目录现在就是本项目的正式执行中枢层。

目标是收拢当前固定逻辑，
让固定执行步骤由 `packages/` 统一承载。

## 目标职责

- 读取 `specs/`
- 解析任务协议
- 装配上下文
- 执行检查
- 执行归档

## 目录约定

- `task_bootstrap/`：任务初始化
- `task_card_resolve/`：任务卡解析
- `context_assemble/`：上下文装配
- `validate/`：检查与状态产出
- `archive/`：归档与导出

## 运行方式

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
