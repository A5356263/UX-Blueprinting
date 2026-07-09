# 体验蓝图构建思路

这是一个基于 Plugin / Skill 组装的轻工作流项目。

它的核心不是传统工程主线，而是一组按职责拆分的 Skill：先做需求判断，再做体验方案展开，其他能力按需插入。

## 当前主流程

正式主流程只有两步：

1. `uxb`
   负责理解需求、分析问题、收敛判断，输出正式需求定案。
2. `experience-blueprint`
   负责读取需求定案，展开为体验蓝图和交互方案。

主链路如下：

```text
uxb -> experience-blueprint
```

除此之外，像 `knowledge-wiki`、`product-analysis` 等 Skill 属于支撑型能力，不强制进入主链路，按需调用。

## 关键目录

当前最关键的 3 个目录是：

- `.claude/`
  Skill 能力层，存放各个 Skill 的定义与规则。
- `shared-workflow/`
  协同规则层，定义 Skill 之间怎么衔接、什么时候衔接。
- `spark-output/`
  正式输出层，存放每一步的文档产物和结构化上下文数据。

## `shared-workflow/` 的作用

`shared-workflow/` 现在只保留 2 个文件：

- `skill-graph.json`
  Skill 关系与推荐流转的数据源，定义谁依赖谁、下一步推荐进入谁。
- `next-skill.md`
  统一承载“就绪判定规则 + 交接话术模板”。
  前者决定一个 Skill 什么时候适合启动，后者决定一个 Skill 完成后怎样自然交给下一个 Skill。

## `spark-output/` 的作用

`spark-output/` 是正式产物出口，当前主要包括：

- `uxb_output.md`：需求定案文档
- `experience_blueprint.md`：体验蓝图文档
- `context/`：结构化 JSON，上下游 Skill 用它来衔接
- `preview/`：预览结果

其中 `spark-output/context/*.json` 还承担流程状态作用：哪些 Skill 已完成，系统就按这里的 JSON 来判断。

## 其他目录说明

- `knowledge/`
  项目根目录下的历史知识库，目前仍保留，但主消费能力已收敛到 Skill 体系内。
- `docs/`
  讨论文档、执行文档和历史记录。
- `input/`、`projects/`、`tools/`
  作为补充材料、历史资产或辅助目录保留，不是当前主流程的核心协调层。

## 一句话总结

这个项目本质上是一套以 Skill 为核心、以 `shared-workflow` 为协同规则、以 `spark-output` 为结果出口的轻量智能工作流。
