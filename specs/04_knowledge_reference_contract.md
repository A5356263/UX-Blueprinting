# Knowledge 引用合同

## 目标

定义任务如何正式引用 `knowledge/business/`、`knowledge/guidelines/` 与 `knowledge/wiki/`。

## 知识层职责

- `knowledge/business/`：业务真源
- `knowledge/guidelines/`：原则真源
- `knowledge/wiki/`：默认消费层与编译层

## 默认消费顺序

1. `task_card.md`
2. `knowledge/wiki/` 中显式引用的页面
3. 必要的 `knowledge/business/`
4. 必要的 `knowledge/guidelines/`
5. 模板与检查规则

## 引用规则

- 任务应优先显式引用 Wiki 页面
- 当 Wiki 存在 `[GAP]`、`[CONFLICT]` 或缺少细节时，再回查真源
- 引用必须使用仓库相对路径
- 执行中枢只装配显式引用内容，不得静默扩展无关知识

## Context Assembly 要求

执行中枢装配上下文时，必须：

- 基于 `task_card_resolved.json`
- 把 `Knowledge`、`Wiki`、`Templates`、`Checks` 的显式引用写入 `context_manifest.json`
- 把显式引用内容复制到 `projects/<project-id>/runtime/context_bundle/`

## 失败条件

- 引用路径不存在
- 引用无法复制到 `context_bundle/`
- `context_manifest.json` 未生成
