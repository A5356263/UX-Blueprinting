# memory

本目录是长期 Memory 子系统。

它负责沉淀跨任务可复用的质量经验，不替代 `specs/`、`projects/`、`knowledge/wiki/`。

## 目录约定

- `index.json`：长期 memory 索引
- `patterns/`：高质量模式卡
- `failure_modes/`：失败模式卡
- `preferences/`：项目长期质量偏好骨架
- `capability_insights/`：围绕 capability 的经验沉淀

## 边界

- 长期 memory 顶层独立，不写进 `knowledge/wiki/`
- 不直接复制整篇 blueprint 作为 memory
- 用户可读摘要统一写入 `projects/<project-id>/workspace/memory_summary.md`
