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

## 跨平台运行建议

- 标准入口保持为 `python -m packages`
- Windows 上优先使用 `python -m packages`，如果本机没有 `python`，再使用 `py -3 -m packages`
- macOS / Linux 上优先使用 `python3 -m packages`
- 仓库根目录提供两个薄转发脚本：
  - `bash run_packages.sh <command> ...`
  - `powershell -ExecutionPolicy Bypass -File .\\run_packages.ps1 <command> ...`
- 这些脚本只负责选择可用 Python 入口，不改变任何命令语义

## 运行方式

```bash
python -m packages bootstrap <project-id> --domain <domain>
python -m packages project-structure-check <project-id>
python -m packages assemble <project-id>
python -m packages generate-facts <project-id>
python -m packages generate-business <project-id>
python -m packages generate-experience <project-id>
python -m packages gate-facts <project-id>
python -m packages gate-business <project-id>
python -m packages gate-experience <project-id>
python -m packages validate <project-id>
python -m packages coverage <project-id>
python -m packages run-main <project-id>
python -m packages capabilities-list
python -m packages capability-show <capability-id>
python -m packages memory-extract <project-id>
python -m packages memory-accept <project-id>
python -m packages memory-summary <project-id>
python -m packages preview <project-id> --host 127.0.0.1 --port 0
python -m packages sample-check
python -m packages env-check
```
