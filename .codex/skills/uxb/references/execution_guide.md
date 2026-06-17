# 执行说明

这份说明只在下面这个前提成立后使用：

**用户已经明确选择“进入正式蓝图任务”。**

从这一刻开始，正式蓝图主链路已经开始。

## 用户侧先怎么说

先用大白话告诉用户：

1. 我会先创建正式任务目录
2. 把刚才确认过的内容写成正式输入
3. 先生成执行判断单
4. 再继续后续生成阶段

不要一上来就讲一堆命令细节。

## 主链路内部顺序

进入正式蓝图任务后，固定顺序是：

1. 创建项目目录
2. 写正式输入
3. 写判断单
4. 判断单校验
5. 后续生成阶段

不要再把“主链路”理解成这些动作之后才开始。

## 创建项目目录

常见起点仍然是：

```bash
python -m packages bootstrap <project-id> --task-name "<task-name>" --domain "<domain>"
```

如果 `python` 不可用：

- macOS / Linux 用 `python3 -m packages ...`
- Windows 用 `py -3 -m packages ...`

也可以使用仓库转发脚本。

## 写正式输入

bootstrap 后，将用户确认进入正式蓝图前已经收敛的信息写入正式输入层：

- `projects/<project-id>/source/requirement.md`
  - 写原始需求、用户确认后的目标、本次任务范围
- `projects/<project-id>/source/background.md`
  - 写背景资料、约束、历史上下文、正式任务分析收敛总结、风险与 GAP

默认不重写聊天记录。
默认不把完整推理过程写进去。
写的是后续 `facts.md` 可以稳定消费的正式输入。

## 写判断单

写 `projects/<project-id>/runtime/uxb_route_decision.json` 前，必须先读：

- `references/uxb_route_decision_authoring_guide.md`
- `assets/uxb_route_decision.template.json`

如果判断单缺失，或 `can_execute_mainline` 仍为 `false`，就不要继续。

判断单只写执行路由与知识选择，不写体验压力点、业务语义细节、设计策略或分析过程。

如当前 schema 仍存在 `experience_pressure`，保持空数组 `[]`，不要把 Step2 的体验承接重点写入判断单。

写判断单时仍然遵守：

1. 不把修复说明、排查结论或自然语言解释写进 JSON
2. 如需引用中文术语，优先用 `「」` 或 `“”`
3. 校验失败时，不在坏 JSON 上一直缝补，直接按模板重写

## 判断单校验

写完判断单后，先做判断单校验，再继续后续生成阶段。

不要跳过这一步。

## 后续生成阶段

判断单校验通过后，再进入后续生成。

`full` 路径下，`gap_list.md` 会在执行过程中生成，用于记录待确认问题。

Agent 不需要手动创建 `gap_list.md`，但应在最终检查时消费其内容。

统一通过仓库执行中枢运行真实命令。

先查真实命令：

```bash
python -m packages --help
python -m packages capabilities-list
python -m packages capability-show <capability-id>
```

以仓库里的真实实现为准，不只靠记忆。

## 质量边界

1. 没有真实检查结果，不要口头宣布成功
2. 不要跳过必要校验
3. 如果检查失败，优先修正式文件
4. 是否真正可用，以执行中枢结果为准
