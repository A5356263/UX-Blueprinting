# Wiki 说明

本文件用于解释为什么项目需要 `knowledge/wiki/` 这一层。  
正式 Wiki 页面合同请见 [07_wiki_contract.md](E:/AI设计/体验蓝图构建思路/specs/07_wiki_contract.md)。

## Wiki 的作用

- 作为默认消费层
- 做跨文件概念澄清
- 做任务入口页与关系页
- 保留 `[GAP]` 与 `[CONFLICT]`

## 与真源的关系

- `knowledge/raw/**` 是真源
- `knowledge/wiki/summaries/**` 是默认消费层
- summary 通过 `source_refs` 指向可回查的 raw 文件

默认从 Wiki 进入，必要时回真源核实。
