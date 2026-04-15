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
- `generation/`：正式 facts / business / experience 生成层
- `validate/`：检查与状态产出
- `archive/`：归档与导出
- `capability_registry/`：正式能力声明与只读查询入口
- `memory_layer/`：质量经验提取、接受与摘要生成
- `experience_preview/`：体验蓝图预览层生成与本地地址交付

## 运行方式

```bash
python -m packages bootstrap <project-id>
python -m packages assemble <project-id>
python -m packages generate-facts <project-id>
python -m packages generate-business <project-id>
python -m packages generate-experience <project-id>
python -m packages gate-facts <project-id>
python -m packages gate-business <project-id>
python -m packages gate-experience <project-id>
python -m packages validate <project-id>
python -m packages coverage <project-id>
python -m packages archive <project-id>
python -m packages run-main <project-id>
python -m packages capabilities-list
python -m packages capability-show <capability-id>
python -m packages memory-extract <project-id>
python -m packages memory-accept <project-id>
python -m packages memory-summary <project-id>
python -m packages preview <project-id> --host 127.0.0.1 --port 0
python -m packages sample-check
```
