# 跨 AI 执行说明

本文件用于解释为什么本项目可以被不同 AI 工具复用，以及主线应该如何被理解。  
正式执行规则请见 [01_execution_hub_spec.md](E:/AI设计/体验蓝图构建思路/specs/01_execution_hub_spec.md) 以及同目录下其他合同文件。

## 核心理解

本项目不是依赖某个特定平台的 prompt 组合，而是依赖：

- 固定目录结构
- 固定任务入口
- 固定知识分层
- 固定输出位置
- 固定检查状态

## 主线结构

当前主线由以下目录共同组成：

- `specs/`
- `packages/`
- `projects/`
- `knowledge/`
- `templates/`
- `docs/`

## 任务是如何被理解的

对任意 AI 来说，一个任务最重要的不是聊天上下文，而是：

- `projects/<project-id>/source/task_card.md`
- `projects/<project-id>/source/requirement.md`
- `projects/<project-id>/source/background.md`

## 知识是如何被消费的

- 默认先读 `knowledge/wiki/`
- 需要细节时再回到 `knowledge/business/` 与 `knowledge/guidelines/`

## 结果是如何被查看的

- 执行中结果看 `projects/<project-id>/workspace/`
- 最终交付看 `projects/<project-id>/exports/final/`
- 检查结果看 `projects/<project-id>/exports/checks/`

## 为什么 `docs/sdd` 仍然保留

因为解释层仍然有价值：

- 方便新 AI 或新协作者快速建立心智
- 方便用简洁语言解释“为什么这样设计”
- 避免每次都直接读完整法典

但正式规则已经全部以下沉到 `specs/`。
