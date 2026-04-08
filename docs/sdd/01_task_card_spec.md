# Task Card 说明

本文件用于解释 `task_card.md` 在项目中的角色与使用方式。  
正式规则真源请见 [03_task_card_contract.md](E:/AI设计/体验蓝图构建思路/specs/03_task_card_contract.md)。

## 它是什么

`task_card.md` 是单个项目的任务入口文件。它告诉 AI：

- 任务是什么
- 先读什么
- 要产出什么
- 结果写到哪里

## 它不是什么

- 不是业务判断正文
- 不是体验推导正文
- 不是聊天提示词合集

## 理解重点

- 任务入口固定在 `projects/<project-id>/source/task_card.md`
- 默认优先引用 Wiki，再回查真源
- 所有正式输出都落在 `projects/<project-id>/workspace/`
- 执行中枢会把它解析成 `runtime/task_card_resolved.json`
