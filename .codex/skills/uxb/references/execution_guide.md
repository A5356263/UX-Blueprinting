# 执行说明

用户明确确认执行后，再用这份说明。

## 执行前

先用大白话告诉用户你会做这几件事：

1. 创建一个 UXB 任务。
2. 把已确认内容写成正式输入。
3. 运行 UXB 主链路并检查产物。

不要主动展开一堆命令细节，除非用户问。

前提要成立：

- 已经有用户确认过的任务摘要
- 当前目标确实是正式产物执行，而不是纯咨询或知识候选整理

知识候选创建、知识入库确认，不走 UXB 主链路。

默认确认话术模板见：

```text
.codex/skills/uxb/assets/execution_confirmation.template.md
```

## 稳定入口

统一通过仓库执行中枢进入：

```bash
python -m packages <command> <project-id>
```

如果 `python` 不可用：

- macOS / Linux 用 `python3 -m packages <command> <project-id>`
- Windows 用 `py -3 -m packages <command> <project-id>`
- 或使用仓库里的薄转发脚本：

```bash
bash run_packages.sh <command> <project-id>
powershell -ExecutionPolicy Bypass -File .\run_packages.ps1 <command> <project-id>
```

也可以使用：

```bash
scripts/uxb.sh <command> <project-id>
```

作为适合场景下的薄转发入口。

## 先查真实命令

不要在 skill 里维护静态命令表，也不要盲信记忆里的命令。

先查真实命令：

```bash
python -m packages --help
python -m packages capabilities-list
python -m packages capability-show <capability-id>
```

以仓库里的真实实现为准。

## 任务创建

常见起点是：

```bash
python -m packages bootstrap <project-id> --task-name "<task-name>"
```

bootstrap 后，把已确认的任务摘要写进正式输入，例如：

```text
projects/<project-id>/source/requirement.md
projects/<project-id>/source/background.md
```

只在需要时调整 `projects/<project-id>/source/task_card.md`。

不要把聊天原文直接当正式输入。

优先把已确认的任务摘要写入正式输入文件，再进入后续执行。

## 质量边界

这个 skill 不替代执行中枢本身的质量判断。

要记住：

1. 没有真实检查结果，不要口头宣布成功。
2. 不要跳过 validation 或 gate。
3. 不要伪造通过状态。
4. 如果检查失败，优先修正式文件，而不是只在聊天里解释。
5. 是否可归档，以执行中枢结果为准。

## 产物位置

正式产物目录是：

```text
projects/<project-id>/
```

典型结构包括：

```text
source/
workspace/
runtime/
exports/
```

知识候选区不是这里的一部分，也不是正式任务产物目录。
