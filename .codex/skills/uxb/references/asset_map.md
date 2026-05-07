# UXB Asset Map

用这个 guide 看仓库主要资产放在哪里，以及各自该怎么用。

## Principle

这个文件说明的是资产类型和使用边界，不承诺维护一份完整目录清单。

以当前仓库结构为准。

## Execution Hub

```text
packages/
```

这里是稳定执行入口，负责任务创建、上下文组装、生成、校验、修复、归档、预览等行为。

skill 应调用它，而不是复制它。

## Knowledge Base

```text
knowledge/
```

用它支撑业务与体验判断。

读取知识时从这里开始：

```text
knowledge/wiki/index.md
```

在继续往下钻之前，优先看 navigation、route card、index、summary 和 README 风格入口文件。

这里是正式知识系统，不是随手记录区。用户纠错或确认沉淀时，先进入知识候选区，不要直接改这里。

## Knowledge Candidate Area

```text
知识候选区/
```

这是人工 / AI 协作缓冲区，用来放待确认的知识候选，不是正式 knowledge，也不是 UXB 主链路产物。

子目录约定为：

```text
知识问答/
诊断咨询/
新需求文档/
```

这个区域：

- 不参与 `packages/` 执行中枢
- 不参与 run-main
- 不参与 gate / validate / archive / preview
- 不被 `specs/`、`templates/` 消费
- 不等于 `projects/<project-id>/` 正式产物

## Formal Rules

```text
specs/
```

这里是正式规则契约的事实来源。涉及正式产物或阶段边界时，以 `specs/` 为准。

## Templates

```text
templates/
```

生成 facts、business、experience 等正式产物时，优先使用这里的模板。

## Project Artifact Area

```text
projects/<project-id>/
```

这里是正式任务输入和输出的归属位置。

Typical structure:

```text
source/
workspace/
runtime/
exports/
```

除非任务本身要求写入已确认的正式输入，否则 skill 不手工管理这块区域。

知识候选不要写进这里。
