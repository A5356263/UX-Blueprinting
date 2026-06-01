# 执行说明

用户明确确认执行后，再用这份说明。

## 执行前

先用大白话告诉用户你会做这几件事：

1. 创建一个 UXB 任务
2. 把已确认内容写成正式输入
3. 先生成 UXB 判断单
4. 再运行 UXB 主链路并检查产物

不要主动展开一堆命令细节，除非用户追问。

前提要成立：

- 已经有用户确认过的任务摘要
- 当前目标确实是正式产物执行，而不是纯咨询或知识候选整理

## 正式执行前必须先生成判断单

在调用主链路之前，先生成：

- `projects/<project-id>/runtime/uxb_route_decision.json`

生成时必须先读：

- `references/uxb_route_decision_authoring_guide.md`
- `assets/uxb_route_decision.template.json`

如果判断单缺失，或 `can_execute_mainline` 仍为 `false`，就不要启动主链路。

写判断单时，先确认三件事再继续往后跑：

1. 当前不确定项哪些只是影响细化，哪些会直接阻断正式产出
2. 当前知识选择是否已经收敛到后续真正会消费的最小资料集合
3. 当前 `required_outputs` 是否和事实成熟度匹配

## 稳定入口

统一通过仓库执行中枢进入：

```bash
python -m packages <command> <project-id>
```

如 `python` 不可用：

- macOS / Linux 用 `python3 -m packages <command> <project-id>`
- Windows 用 `py -3 -m packages <command> <project-id>`
- 或使用仓库里的转发脚本

```bash
bash run_packages.sh <command> <project-id>
powershell -ExecutionPolicy Bypass -File .\run_packages.ps1 <command> <project-id>
```

也可以使用：

```bash
scripts/uxb.sh <command> <project-id>
```

## 先查真实命令

不要在 skill 里维护静态命令表，也不要只信记忆里的命令。

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
python -m packages bootstrap <project-id> --task-name "<task-name>" --domain "<domain>"
```

bootstrap 后，把已确认的任务摘要写进正式输入，例如：

```text
projects/<project-id>/source/requirement.md
projects/<project-id>/source/background.md
```

只在需要时调整 `projects/<project-id>/source/task_card.md`。

## 推荐执行顺序

正式执行通常按下面顺序：

1. `bootstrap`
2. 写 `source/` 输入
3. 写 `runtime/uxb_route_decision.json`
4. 用 `route-decision` 做一次判断单校验
5. 再用 `run-routed-main <project-id> --route auto`

如果用户还没确认，停在摘要和判断阶段，不要往后跑。

写判断单时再补一条执行约束：

- 不要把修复说明、排查结论、代码围栏或自然语言解释写进 `uxb_route_decision.json`
- 如果字符串里需要引用中文术语，优先用 `「」` 或 `“”`，避免未转义的 ASCII 双引号破坏 JSON
- 如果 `route-decision` 校验失败，不要在原坏 JSON 上持续缝补，直接从 `assets/uxb_route_decision.template.json` 重新覆盖重写

## 质量边界

这个 skill 不替代执行中枢本身的质量判断。

要记住：

1. 没有真实检查结果，不要口头宣布成功
2. 不要跳过 validation 或 gate
3. 不要伪造通过状态
4. 如果检查失败，优先修正式文件，而不是只在聊天里解释
5. 是否可归档，以执行中枢结果为准

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
